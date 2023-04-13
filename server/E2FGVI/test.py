# -*- coding: utf-8 -*-
import io
import cv2
from PIL import Image
import numpy as np
import importlib
import os
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import animation
import torch
import av
import time
import torch._dynamo as dynamo
import logging

dynamo.config.log_level = logging.INFO

from core.utils import to_tensors

parser = argparse.ArgumentParser(description="E2FGVI")
parser.add_argument("-v", "--video", type=str, required=True)
parser.add_argument("-c", "--ckpt", type=str, required=True)
parser.add_argument("-m", "--mask", type=str, required=True)
parser.add_argument("--model", type=str, choices=['e2fgvi', 'e2fgvi_hq'])
parser.add_argument("--step", type=int, default=10)
parser.add_argument("--num_ref", type=int, default=-1)
parser.add_argument("--neighbor_stride", type=int, default=5)
parser.add_argument("--savefps", type=int, default=24)

# args for e2fgvi_hq (which can handle videos with arbitrary resolution)
parser.add_argument("--set_size", action='store_true', default=False)
parser.add_argument("--width", type=int)
parser.add_argument("--height", type=int)

args = parser.parse_args()
# new_args = args.Namespace()
# new_args.model = "e2fgvi_hq"


ref_length = args.step  # ref_step
num_ref = args.num_ref
neighbor_stride = args.neighbor_stride
default_fps = args.savefps


# sample reference frames from the whole video
def get_ref_index(f, neighbor_ids, length):
    ref_index = []
    if num_ref == -1:
        for i in range(0, length, ref_length):
            if i not in neighbor_ids:
                ref_index.append(i)
    else:
        start_idx = max(0, f - ref_length * (num_ref // 2))
        end_idx = min(length, f + ref_length * (num_ref // 2))
        for i in range(start_idx, end_idx + 1, ref_length):
            if i not in neighbor_ids:
                if len(ref_index) > num_ref:
                    break
                ref_index.append(i)
    return ref_index


# read frame-wise masks
def read_mask(mpath, size):
    masks = []
    mnames = os.listdir(mpath) #comment this out 
    mnames.sort()
    for mp in mpath:
        # m = Image.open(os.path.join(mpath, mp))
        # m = m.resize(size, Image.NEAREST) # comment this out
        # m = np.array(m.convert('L'))
        # m = np.array(m > 0).astype(np.uint8)
        mp = cv2.dilate(mp,
                       cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)),
                       iterations=4)
        masks.append(Image.fromarray(mp * 255))
    return masks


#  read frames from video
def read_frame_from_videos(args):
    vname = args.video
    frames = []
    if args.use_mp4:
        vidcap = cv2.VideoCapture(vname)
        success, image = vidcap.read()
        count = 0
        while success:
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            frames.append(image)
            success, image = vidcap.read()
            count += 1
    else:
        lst = os.listdir(vname)
        lst.sort()
        fr_lst = [vname + '/' + name for name in lst]
        for fr in fr_lst:
            image = cv2.imread(fr)
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            frames.append(image)
    return frames


# resize frames
def resize_frames(frames, size=None):
    if size is not None:
        frames = [f.resize(size) for f in frames]
    else:
        size = frames[0].size
    return frames, size

# device = None
# model = None
# size = None

def setup(args):
    global device
    global model
    global size
    # set up models
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.model == "e2fgvi":
        size = (432, 240)
    elif args.set_size:
        size = (args.width, args.height)
    else:
        size = None
    # args.use_mp4 = True if args.video.endswith('.mp4') else False
    # print(
    #     f'Loading videos and masks from: {args.video} | INPUT MP4 format: {args.use_mp4}'
    # )
    net = importlib.import_module('model.' + args.model)
    model = net.InpaintGenerator().to(device)
    data = torch.load(args.ckpt, map_location=device)
    model.load_state_dict(data)
    print(f'Loading model from: {args.ckpt}')
    model.eval()
    opt_model = torch.compile(model)
    return opt_model, size


def main_worker(model, size):
    # set up models

    # prepare datset
    # args.use_mp4 = True if args.video.endswith('.mp4') else False
    # print(
    #     f'Loading videos and masks from: {args.video} | INPUT MP4 format: {args.use_mp4}'
    # )
    #frames = read_frame_from_videos(args)
    frames = args.frames
    frames, size = resize_frames(frames, size)
    h, w = size[1], size[0]
    video_length = len(frames)
    imgs = to_tensors()(frames).unsqueeze(0) * 2 - 1
    frames = [np.array(f).astype(np.uint8) for f in frames]

    masks = read_mask(args.mask, size)
    binary_masks = [
        np.expand_dims((np.array(m) != 0).astype(np.uint8), 2) for m in masks
    ]
    masks = to_tensors()(masks).unsqueeze(0)
    imgs, masks = imgs.to(device), masks.to(device)
    comp_frames = [None] * video_length

    # completing holes by e2fgvi
    print(f'Start test...')
    starttime = time.time()
    individual_times = []
    for f in tqdm(range(0, video_length, neighbor_stride)):
        tim = time.time()
        neighbor_ids = [
            i for i in range(max(0, f - neighbor_stride),
                             min(video_length, f + neighbor_stride + 1))
        ]
        ref_ids = get_ref_index(f, neighbor_ids, video_length)
        selected_imgs = imgs[:1, neighbor_ids + ref_ids, :, :, :]
        selected_masks = masks[:1, neighbor_ids + ref_ids, :, :, :]
        with torch.no_grad():
            masked_imgs = selected_imgs * (1 - selected_masks)
            mod_size_h = 60
            mod_size_w = 108
            h_pad = (mod_size_h - h % mod_size_h) % mod_size_h
            w_pad = (mod_size_w - w % mod_size_w) % mod_size_w
            masked_imgs = torch.cat(
                [masked_imgs, torch.flip(masked_imgs, [3])],
                3)[:, :, :, :h + h_pad, :]
            masked_imgs = torch.cat(
                [masked_imgs, torch.flip(masked_imgs, [4])],
                4)[:, :, :, :, :w + w_pad]
            pred_imgs, _ = model(masked_imgs, len(neighbor_ids))
            pred_imgs = pred_imgs[:, :, :h, :w]
            pred_imgs = (pred_imgs + 1) / 2
            pred_imgs = pred_imgs.cpu().permute(0, 2, 3, 1).numpy() * 255
            for i in range(len(neighbor_ids)):
                idx = neighbor_ids[i]
                img = np.array(pred_imgs[i]).astype(
                    np.uint8) * binary_masks[idx] + frames[idx] * (
                        1 - binary_masks[idx])
                if comp_frames[idx] is None:
                    comp_frames[idx] = img
                else:
                    comp_frames[idx] = comp_frames[idx].astype(
                        np.float32) * 0.5 + img.astype(np.float32) * 0.5
        newtim = time.time()
        individual_times.append(newtim - tim)
    endtime = time.time()
    duration = endtime - starttime

    # saving videos
    print('Saving videos...')
    # save_dir_name = 'results'
    # ext_name = '_results.mp4'
    # save_base_name = args.video.split('/')[-1]
    # save_name = save_base_name.replace(
    #     '.mp4', ext_name) if args.use_mp4 else save_base_name + ext_name
    # if not os.path.exists(save_dir_name):
    #     os.makedirs(save_dir_name)
    # save_path = os.path.join(save_dir_name, save_name)
    # writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*"mp4v"),
    #                          default_fps, size)
    output_file = io.BytesIO()
    output = av.open(output_file, 'w', format="mp4")

    FPS = 24
    stream = output.add_stream('h264', str(FPS))
    stream.width = w
    stream.height = h
    stream.pix_fmt = 'yuv444p'
    stream.options = {'crf': '17'}
    for f in range(video_length):
        # comp = comp_frames[f].astype(np.uint8)
        # writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
        frame = av.VideoFrame.from_ndarray(comp, format='bgr24')
        packet = stream.encode(frame)
        output.mux(packet)
    # writer.release()
    print("overall duration: ", duration)
    for i in individual_times:
        print("individual duration: ", i)
    packet = stream.encode(None)
    output.mux(packet)
    output.close()
    
    return output

    # show results
    # print('Let us enjoy the result!')
    # fig = plt.figure('Let us enjoy the result')
    # ax1 = fig.add_subplot(1, 2, 1)
    # ax1.axis('off')
    # ax1.set_title('Original Video')
    # ax2 = fig.add_subplot(1, 2, 2)
    # ax2.axis('off')
    # ax2.set_title('Our Result')
    # imdata1 = ax1.imshow(frames[0])
    # imdata2 = ax2.imshow(comp_frames[0].astype(np.uint8))

    # def update(idx):
    #     imdata1.set_data(frames[idx])
    #     imdata2.set_data(comp_frames[idx].astype(np.uint8))

    # fig.tight_layout()
    # anim = animation.FuncAnimation(fig,
    #                                update,
    #                                frames=len(frames),
    #                                interval=50)
    # plt.show()


if __name__ == '__main__':
    model, size = setup()
    main_worker(model, size)
