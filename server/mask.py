# --------------------------------------------------------
# SiamMask
# Licensed under The MIT License
# Written by Qiang Wang (wangqiang2015 at ia.ac.cn)
# --------------------------------------------------------
import os
import av
from get_mask.test import *
from get_mask.models.custom import Custom
import cv2
import glob
import json
import torch

def local_load_config(args):
    # assert os.path.exists(args.config), '"{}" not exists'.format(args.config)
    # config = json.load(open("./get_mask/experiments/siammask/config_davis.json"))
    config = {
        "network": {
            "arch": "Custom"
        },
        "hp": {
            "instance_size": 255,
            "base_size": 8,
            "out_size": 120,
            "seg_thr": 0.35,
            "penalty_k": 0.04,
            "window_influence": 0.4,
            "lr": 1.0
        },
        "anchors": {
            "stride": 8,
            "ratios": [0.33, 0.5, 1, 2, 3],
            "scales": [8],
            "round_dight": 0
        }
    }

    # deal with network
    if 'network' not in config:
        print('Warning: network lost in config. This will be error in next version')

        config['network'] = {}

        if not args.arch:
            raise Exception('no arch provided')
    args.arch = config['network']['arch']

    return config


def get_frames_old (video_name):
    if not video_name:
        cap = cv2.VideoCapture(0)
        # warmup
        for i in range(5):
            cap.read()
        while True:
            ret, frame = cap.read()
            if ret:
                yield frame
            else:
                break
    elif video_name.endswith('avi') or \
        video_name.endswith('mp4'):
        f = av.open(video_name)
        for frame in f.decode(video=0):
            yield frame.to_array()
    else:
        images = glob.glob(os.path.join(video_name, '*.jp*'))
        images = sorted(images,
                        key=lambda x: int(x.split('/')[-1].split('.')[0]))
        for img in images:
            frame = cv2.imread(img)
            yield frame

def get_frames(video_file):
    print("video file: ", video_file, flush=True)
    f = av.open(video_file, 'r', format="mp4")
    for frame in f.decode(video=0):
        yield cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

def mask_setup(args):
    args.config = "./get_mask/experiments/siammask/config_davis.json"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    # Setup Model
    cfg = local_load_config(args)
    siammask = Custom(anchors=cfg['anchors'])
    # assert isfile(args.resume), '{} is not a valid file'.format(args.resume)
    print("loading")
    siammask = load_pretrain(siammask, args.resume)
    # opt_siammask = torch.compile(siammask)
    return siammask, cfg


def mask(args, siammask, cfg):
    # Setup device
    

    # siammask.eval().to(device)

    # Parse Image file
    # img_files = sorted(glob.glob(join(args.base_path, '*.jp*')))
    img_files = args.data
    ims = [imf for imf in img_files]
    # print("SIZE: ", ims[0].size)
    # print("IM: ", ims[0])
    print("hola: ", len(ims))

    # height, width, channels = ims[0].shape

    # Select ROI
    # cv2.setWindowProperty("SiamMask", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    x = int(args.x)
    y = int(args.y)
    w = int(args.w)
    h = int(args.h)
    print("x: ", x, ", y: ", y, ", w: ", w, ", h: ", h)

    toc = 0
    counter = 0

    if not os.path.exists(os.path.join('results', '{}_mask'.format("test"))):
        os.makedirs(os.path.join('results', '{}_mask'.format("test")))
        os.makedirs(os.path.join('results', '{}_frame'.format("test")))

    print("starting the inference")
    totalf = 0
    masks = []
    for f, im in enumerate(ims):
        tic = cv2.getTickCount()
        if f == 0:  # init
            print(f)
            target_pos = np.array([x + w / 2, y + h / 2])
            target_sz = np.array([w, h])
            print("shape:",im.shape)
            state = siamese_init(im, target_pos, target_sz, siammask, cfg['hp'])  # init tracker

            state = siamese_track(state, im, mask_enable=True, refine_enable=True)  # track
            location = state['ploygon'].flatten()
            mask = state['mask'] > state['p'].seg_thr
            mask = (mask * 255.).astype(np.uint8)
            masks.append(mask)
            # cv2.imwrite('{:05d}.png'.format(counter), mask)
            # cv2.imwrite('{:05d}.jpg'.format(counter), im)
            counter += 1
            
        elif f > 0:  # tracking
            print(f)
            state = siamese_track(state, im, mask_enable=True, refine_enable=True)  # track
            location = state['ploygon'].flatten()
            mask = state['mask'] > state['p'].seg_thr
            mask = (mask * 255.).astype(np.uint8)
            masks.append(mask)
            # cv2.imwrite('{:05d}.png'.format(counter), mask)
            # cv2.imwrite('{:05d}.jpg'.format(counter), im)
            counter += 1

            im[:, :, 2] = (mask > 0) * 255 + (mask == 0) * im[:, :, 2]
            # cv2.polylines(im, [np.int0(location).reshape((-1, 1, 2))], True, (0, 255, 0), 3)
            # cv2.imshow('Get_mask', im)
            # key = cv2.waitKey(1)
            # if key > 0:
            #     break
        totalf+=1
        if f>10: break

        toc += cv2.getTickCount() - tic
    toc = cv2.getTickCount()
    toc /= cv2.getTickFrequency()
    print(toc)
    fps = totalf / toc
    print('SiamMask Time: {:02.1f}s Speed: {:3.1f}fps (with visulization!)'.format(toc, fps))
    return ims, masks

# if __name__=="__main__":
#     args = argparse.Namespace()
#     args.resume = 'cp/SiamMask_DAVIS.pth'
#     args.mask_dilation = 32
#     mask_setup(args)