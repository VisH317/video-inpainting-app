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
# from TrackAnything.track_anything import TrackingAnything

SUPABASE_URL="https://uwepaxzzdeivpecslmyh.supabase.co"
SUPABASE_ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3ZXBheHp6ZGVpdnBlY3NsbXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM3NzgyODQsImV4cCI6MTk5OTM1NDI4NH0.07v00Ciub-z4glwaomfeNkm5OkPuSeo65NNJgDj5S3I"

def get_frames(video_file):
    print("video file: ", video_file, flush=True)
    f = av.open(video_file, 'r', format="mp4")
    for frame in f.decode(video=0):
        yield cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

class InpaintHandler(BaseHandler):

    def __init__(self):
        self.initialized = False
        self.siammask = None
        self.model = None
        self.size = None # uncomment the initialize, change the imports to include server, change other imports to include server in tracker and inpainter
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
        self.client = create_client(SUPABASE_URL, SUPABASE_ANON)
        # from server.E2FGVI.test import setup
        # from server.XMem.eval import mask_setup
        # from server.mask import mask_setup
        from server.TrackAnything.track_anything import TrackingAnything

        sam_checkpoint = './server/saves/sam_vit_h_4b8939.pth'
        xmem_checkpoint = './server/saves/XMem-s012.pth'
        e2fgvi_checkpoint = './server/E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'
        # sam_checkpoint = './saves/sam_vit_h_4b8939.pth'
        # xmem_checkpoint = './saves/XMem-s012.pth'
        # e2fgvi_checkpoint = './E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

        args = argparse.Namespace()
        args.device = "cpu"
        args.sam_model_type = "vit_h"

        self.model = TrackingAnything(sam_checkpoint, xmem_checkpoint, e2fgvi_checkpoint, args)

        print("ready!!!")


    def preprocess(self, model_inputs):

        preprocessed_inputs = []

        for ix, model_input in enumerate(model_inputs):

            print("model_input: ", str(model_input['x']), ', ', model_input['y'], ', ', model_input['w'], ', ', model_input['h'])
            preprocessed_input = {
                "data": io.BytesIO(model_input['data']),
                "x": int(str(model_input['x']).split("'")[1]),
                "y": int(str(model_input['y']).split("'")[1]),
                "w": int(str(model_input['w']).split("'")[1]),
                "h": int(str(model_input['h']).split("'")[1]),
                "maxx": int(float(str(model_input['maxx']).split("'")[1])),
                "maxy": int(float(str(model_input['maxy']).split("'")[1]))
            }

            print("test model input: ", preprocessed_input)

            preprocessed_inputs.append(preprocessed_input)

        return preprocessed_input
    
    
    def postprocess(self, input):

        rets = []
        for url in input:
            rets.append(json.dumps({ "url": url }))
        return rets
    

    def inference(self, data_list):

        """
        Create inpainted video from the original in a batch
        Args:
            data (list[{file, bounding box, dimensions}]) - main data for each batch item to be processed
        Returns:
            list: of output file supabase uuids for the frontend to access in a subsequent request
        """

        os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
        os.environ['TORCH_USE_CUDA_DSA'] = "1"
        # data params: video (mp4), x, y, w, h (bounding box to inpaint)
        print("LISTING DIR: ", os.listdir())
        # from server.E2FGVI.test import main_worker
        # from server.XMem.eval import mask

        url_list = []

        for idx, data in enumerate(data_list):

            maxx = int(data['maxx'])
            maxy = int(data['maxy'])

            ims = list(get_frames(data['data']))

            ims = [torch.from_numpy(im).squeeze().numpy() for im in ims]

            height, width, _ = ims[0].shape

            # args.resume = 'cp/SiamMask_DAVIS.pth'
            # args.mask_dilation = 32
            x = (int(data['x'])/maxx)*width
            y = (int(data['y'])/maxy)*height
            w = (int(data['w'])/maxx)*width
            h = (int(data['h'])/maxy)*height

            mask = ims[0][:,:,0]

            print("preargs: ", data['x'], ", ", data['y'], ", ", data['w'], ", ", data['h'])
            print("args: ", x, ", ", y, ", ", w, ", ", h, ", ")
            for ix in range(height):
                for ix2 in range(width):
                    if not (ix>=x and ix<=x+w and ix2>=y and ix2<=y+h): 
                        mask[ix][ix2] = 0
                    else: mask[ix][ix2] = 1

            print("mask: ", mask.shape)

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

            res = self.client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
            print(res)
            
            url = self.client.storage.from_('videos').get_public_url(f"{id}.mp4")
            url_list.append(url)

        return url_list


if __name__=="__main__":
    i = InpaintHandler()
    i.initialize(True)
    with open("./TrackAnything/test_sample/test-sample1.mp4", "rb") as f:
        data = {
            'data': f,
            "x": 100,
            "y": 100,
            "w": 100,
            "h": 100,
            "maxx": 720,
            "maxy": 1280
        }
        url = i.inference(data)
        print(url)