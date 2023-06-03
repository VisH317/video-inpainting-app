import torch
import argparse
from ts.torch_handler.base_handler import BaseHandler
# custom handler for torchserve
import zipfile
import os
import subprocess
import io
import sys
from PIL import Image
import cv2
import deepspeed
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
import json
import numpy as np
import av

class InpaintHandler(BaseHandler):

    def __init__(self):
        self.initialized = False
        self.siammask = None
        self.model = None
        self.size = None
        self.device = None
        self.client: Client = None  #create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON"))

    def initialize(self, context):
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        if not torch.cuda.is_available() or properties.get("gpu_id") is None:
            raise RuntimeError("This model is not supported on CPU machines.")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")))

        with zipfile.ZipFile(model_dir + "/server.zip", "r") as zip_ref:
            zip_ref.extractall(model_dir)

        # process = subprocess.call(["sudo", "./server/get_mask/make.sh"], shell=True)
        # process.wait()

        print("LISTING DIR: ", os.listdir("./server"))
        load_dotenv("./server/.env")
        self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON"))
        # from server.E2FGVI.test import setup
        # from server.XMem.eval import mask_setup
        # from server.mask import mask_setup
        from server.TrackAnything.track_anything import TrackingAnything

        sam_checkpoint = ''
        xmem_checkpoint = ''

        args = argparse.Namespace()
        args.device = "cuda:0"
        args.sam_model_type = "vit_h"

        self.model = TrackingAnything(sam_checkpoint, xmem_checkpoint, args)

    def preprocess(self, model_input):
        print("model_input: ", str(model_input[0]['x']), ', ', model_input[0]['y'], ', ', model_input[0]['w'], ', ', model_input[0]['h'])
        preprocessed_input = {
            "data": io.BytesIO(model_input[0]['data']),
            "x": int(str(model_input[0]['x']).split("'")[1]),
            "y": int(str(model_input[0]['y']).split("'")[1]),
            "w": int(str(model_input[0]['w']).split("'")[1]),
            "h": int(str(model_input[0]['h']).split("'")[1]),
            "maxx": int(float(str(model_input[0]['maxx']).split("'")[1])),
            "maxy": int(float(str(model_input[0]['maxy']).split("'")[1]))
        }

        print("test model input: ", preprocessed_input)

        return preprocessed_input
    
    
    def postprocess(self, input):
        ret = { "url": input }
        return [json.dumps(ret)]
    

    def inference(self, data):
        os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
        os.environ['TORCH_USE_CUDA_DSA'] = "1"
        # data params: video (mp4), x, y, w, h (bounding box to inpaint)
        print("LISTING DIR: ", os.listdir())
        from server.E2FGVI.test import main_worker
        from server.mask import get_frames
        # from server.XMem.eval import mask

        maxx = int(data['maxx'])
        maxy = int(data['maxy'])

        ims = list(get_frames(data['data']))

        height, width, _ = ims[0].shape

        # args.resume = 'cp/SiamMask_DAVIS.pth'
        # args.mask_dilation = 32
        x = (int(data['x'])/maxx)*width
        y = (int(data['y'])/maxy)*height
        w = (int(data['w'])/maxx)*width
        h = (int(data['h'])/maxy)*height

        mask = ims[0]

        print("preargs: ", data['x'], ", ", data['y'], ", ", data['w'], ", ", data['h'])
        print("args: ", x, ", ", y, ", ", w, ", ", h, ", ")
        for ix in range(height):
            for ix2 in range(width):
                if not (ix>=x and ix<=x+w and ix2>=y and ix2<=y+h): 
                    mask[ix][ix2] = 0
                else: mask[ix][ix2] = 1

        masks, logits, images = self.model.generator(ims, mask)
        
        output_file = io.BytesIO()
        output = av.open(output_file, 'w', format="mp4")

        FPS = 24
        stream = output.add_stream('h264', str(FPS))
        stream.width = w
        stream.height = h
        stream.pix_fmt = 'yuv444p'
        stream.options = {'crf': '17'}
        for f in range(2): # change back to video_length
            comp = ims[f].astype(np.uint8)
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
            f.write(output.getbuffer())

        res = self.client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
        print(res)
        
        url = self.client.storage.from_('videos').get_public_url(f"{id}.mp4")

        return url


if __name__=="__main__":
    i = InpaintHandler()
    i.initialize()