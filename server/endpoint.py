from TrackAnything.track_anything import TrackingAnything
import io
import torch
import cv2
from supabase import create_client
import argparse
import uuid
import av
import numpy as np
import os
from mask import mask_setup, mask
# from TrackAnything.app import inpaint_video

def get_frames(video_file):
    print("video file: ", video_file, flush=True)
    f = av.open(video_file, 'r', format="mp4")
    for frame in f.decode(video=0):
        yield cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)


def inpaint_video(video_state, mask_dropdown):
    operation_log = [("",""), ("Removed the selected masks.","Normal")]

    frames = np.asarray(video_state["origin_images"])
    fps = video_state["fps"]
    inpaint_masks = np.asarray(video_state["masks"])
    # for ix, f in enumerate(frames):
    #     frames[ix] = np.expand_dims(f, axis=0)
    # for ix, m in enumerate(inpaint_masks):
    #     inpaint_masks[ix] = np.expand_dims(m, axis=0)
    if len(mask_dropdown) == 0:
        mask_dropdown = ["mask_001"]
    mask_dropdown.sort()
    # convert mask_dropdown to mask numbers
    inpaint_mask_numbers = [int(mask_dropdown[i].split("_")[1]) for i in range(len(mask_dropdown))]
    # interate through all masks and remove the masks that are not in mask_dropdown
    unique_masks = np.unique(inpaint_masks)
    num_masks = len(unique_masks) - 1
    for i in range(1, num_masks + 1):
        if i in inpaint_mask_numbers:
            continue
        inpaint_masks[inpaint_masks==i] = 0
    # inpaint for videos

    print("shapes: ", inpaint_masks[0].shape, ', ', frames[0].shape[:3])

    inpainted_frames = model.baseinpainter.inpaint(frames, inpaint_masks)   # numpy array, T, H, W, 3 ratio=video_state["resize_ratio"]
    # except:
    #     operation_log = [("Error! You are trying to inpaint without masks input. Please track the selected mask first, and then press inpaint. If VRAM exceeded, please use the resize ratio to scaling down the image size.","Error"), ("","")]
    #     inpainted_frames = video_state["origin_images"]

    return inpainted_frames, operation_log



SUPABASE_URL="https://uwepaxzzdeivpecslmyh.supabase.co"
SUPABASE_ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3ZXBheHp6ZGVpdnBlY3NsbXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM3NzgyODQsImV4cCI6MTk5OTM1NDI4NH0.07v00Ciub-z4glwaomfeNkm5OkPuSeo65NNJgDj5S3I"

device = torch.device("cuda")
client = create_client(SUPABASE_URL, SUPABASE_ANON)

sam_checkpoint = './saves/sam_vit_h_4b8939.pth'
xmem_checkpoint = './saves/XMem-s012.pth'
e2fgvi_checkpoint = './saves/E2FGVI-HQ-CVPR22.pth'

args = argparse.Namespace()
args.device = "cpu"
args.sam_model_type = "vit_h"

model = TrackingAnything(sam_checkpoint, xmem_checkpoint, e2fgvi_checkpoint, args)

ar = argparse.Namespace()
ar.resume = './cp/SiamMask_DAVIS.pth'
ar.mask_dilation = 64
siammask, cfg = mask_setup(ar)


with open("./TrackAnything/test_sample/test-sample1.mp4") as f:

    i = {
        "data": f.buffer,
        "x": 350,
        "y": 700,
        "w": 550,
        "h": 1000,
        "maxx": 720,
        "maxy": 1080
    }

    ims = list(get_frames(i['data']))

    height, width, c = ims[0].shape
    print("shape: ", height, ", ", width, ', ', c)

    x = i['x']
    y = i['y']
    w = i['w']
    h = i['h']

    test_mask = ims[0][:,:,0]

    for ix in range(width):
        for ix2 in range(height):
            if not (ix>=x and ix<=x+w and ix2>=y and ix2<=y+h): 
                test_mask[ix2][ix] = 0
            else: test_mask[ix2][ix] = 1

    cv2.imwrite("im.png", test_mask*255)

    point = np.array([[x+w/2, y+h/2]])
    label = np.array([1])

    print("shapeeeee: ", point.shape, ", ", label.shape)

    model.samcontroler.sam_controler.set_image(ims[0])

    ma, log, im = model.first_frame_click(ims[0], point, label, False)

    print("bruh type: ", type(im), ", ", type(ma), ', ', ma.shape)

    cv2.imwrite("im2.png", cv2.cvtColor(ma.astype(np.uint8)*255, cv2.COLOR_GRAY2BGR))

    # args = argparse.Namespace()
    # args.data = [ims[0]]
    # args.x = x
    # args.y = y
    # args.w = w
    # args.h = h

    # not_ims, pre_mask = mask(args, siammask, cfg)
    # print("mask?: ", pre_mask, ", ", pre_mask[0].shape)

    # cv2.imwrite("mask.png", pre_mask[0])

    # masks, logits, images = model.generator(ims, test_mask*255)

    # video_state = {
    #     "masks": masks,
    #     "origin_images": ims[:4],
    #     "fps": 30
    # }

    # video, log = inpaint_video(video_state, [])


    # output_file = io.BytesIO()
    # output = av.open(output_file, 'w', format="mp4")

    # FPS = 24
    # stream = output.add_stream('h264', str(FPS))
    # stream.width = w
    # stream.height = h
    # stream.pix_fmt = 'yuv444p'
    # stream.options = {'crf': '17'}
    # for f in range(2): # change back to video_length
    #     # comp = video[f].astype(np.uint8)
    #     comp = cv2.cvtColor(masks[f], cv2.COLOR_GRAY2BGR).astype(np.uint8)
    #     # writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
    #     frame = av.VideoFrame.from_ndarray(comp, format='bgr24')
    #     packet = stream.encode(frame)
    #     output.mux(packet)
    # # writer.release()
    # packet = stream.encode(None)
    # output.mux(packet)
    # output.close()

    # id = str(uuid.uuid4())

    # if not os.path.exists(f"mask_test_{id}.mp4"):
    #     open(f"mask_test_{id}.mp4", 'w+')

    # with open(f"mask_test_{id}.mp4", 'wb') as f:
    #     f.write(output_file.getbuffer())

    
    
    # # res = client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
    # # print(res)
    
    # url = client.storage.from_('videos').get_public_url(f"{id}.mp4")

    # print(url)