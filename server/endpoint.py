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

def get_frames(video_file):
    print("video file: ", video_file, flush=True)
    f = av.open(video_file, 'r', format="mp4")
    for frame in f.decode(video=0):
        yield cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

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

with open("./TrackAnything/test_sample/test-sample1.mp4") as f:

    i = {
        "data": io.BytesIO(f),
        "x": 360,
        "y": 400,
        "w": 220,
        "h": 550,
        "maxx": 720,
        "maxy": 1080
    }

    ims = list(get_frames(i['data']))

    height, width, _ = ims[0].shape

    x = i['x']
    y = i['y']
    w = i['w']
    h = i['h']

    mask = ims[0][:,:,0]

    for ix in range(height):
        for ix2 in range(width):
            if not (ix>=x and ix<=x+w and ix2>=y and ix2<=y+h): 
                mask[ix][ix2] = 0
            else: mask[ix][ix2] = 1

    masks, logits, images = model.generator(ims, mask)


    output_file = io.BytesIO()
    output = av.open(output_file, 'w', format="mp4")

    FPS = 24
    stream = output.add_stream('h264', str(FPS))
    stream.width = w
    stream.height = h
    stream.pix_fmt = 'yuv444p'
    stream.options = {'crf': '17'}
    for f in range(2): # change back to video_length
        comp = images[f].astype(np.uint8)
        # writer.write(cv2.cvtColor(comp, cv2.COLOR_BGR2RGB))
        frame = av.VideoFrame.from_ndarray(comp, format='bgr24')
        packet = stream.encode(frame)
        output.mux(packet)
    # writer.release()
    packet = stream.encode(None)
    output.mux(packet)
    output.close()

    id = str(uuid.uuid4())

    if not os.path.exists(f"{id}.mp4"):
        open(f"{id}.mp4", 'w+')

    with open(f"{id}.mp4", 'wb') as f:
        f.write(output_file.getbuffer())

    res = client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
    print(res)
    
    url = client.storage.from_('videos').get_public_url(f"{id}.mp4")

    print(url)