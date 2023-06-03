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
        from server.E2FGVI.test import setup
        # from server.XMem.eval import mask_setup
        from server.mask import mask_setup

        self.mask_weights = './server/cp/SiamMask_DAVIS.pth'
        self.inpaint_weights = './server/E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

        # siammask setup args:
        # args = argparse.Namespace()
        # args.benchmark = False
        # args.model = './server/XMem/model/XMem.pth'
        # args.buffer_size = 100
        # args.num_objects = 1
        # args.max_mid_term_frames = 10
        # args.min_mid_term_frames = 5
        # args.max_long_term_elements = 10000
        # args.num_prototypes = 128
        # args.top_k = 30
        # args.mem_every = 10
        # args.deep_update_every = -1
        # args.no_amp = 'store_true'
        # args.size = -1
        # args.save_scores = False
        # args.flip = False
        # args.enable_long_term_count_usage = True
        # args.enable_long_term = True
        # args.mem_every=5
        # args.deep_update_every=-1
        # args.hidden_dim = 1
        
        args = argparse.Namespace()
        args.resume = './server/cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        siammask, cfg = mask_setup(args)

        siammask = mask_setup(args)
        tp_config = {
            "enabled": True,
            "tp_size": 2,
        }
        # siammask = deepspeed.init_inference(
        #     siammask,
        #     dtype=torch.float,
        #     tensor_parallel=tp_config
        # )
        self.siammask = siammask
        self.cfg = cfg

        # inpaint setup args
        args.model = "e2fgvi_hq"
        args.set_size = True
        args.height = "720"
        args.width = "1280"
        args.ckpt = self.inpaint_weights

        model, size = setup(args)
        # model = deepspeed.init_inference(
        #     model,
        #     dtype=torch.float,
        #     tensor_parallel=tp_config
        # )
        self.model = model
        self.size = size

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
        from server.mask import get_frames, mask
        # from server.XMem.eval import mask

        maxx = int(data['maxx'])
        maxy = int(data['maxy'])

        args = argparse.Namespace()
        # args.images = list(get_frames(data['data']))
        # height, width, channels = args.images[0].shape
        # args.benchmark = False
        # args.model = './saves/XMem.pth'
        # args.buffer_size = 100
        # args.num_objects = 1
        # args.max_mid_term_frames = 10
        # args.min_mid_term_frames = 5
        # args.max_long_term_elements = 10000
        # args.num_prototypes = 128
        # args.top_k = 30
        # args.mem_every = 10
        # args.deep_update_every = -1
        # args.no_amp = 'store_true'
        # args.size = -1
        # args.save_scores = False
        # args.flip = False
        # args.enable_long_term_count_usage = True
        # args.enable_long_term = True
        # args.hidden_dim = 1
        # args.mask = args.images[0]
        args.resume = 'cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        args.x = int(data['x'])/maxx
        args.y = int(data['y'])/maxy
        args.w = int(data['w'])/maxx
        args.h = int(data['h'])/maxy


        # args.resume = 'cp/SiamMask_DAVIS.pth'
        # args.mask_dilation = 32
        x = (int(data['x'])/maxx)
        y = (int(data['y'])/maxy)
        w = (int(data['w'])/maxx)
        h = (int(data['h'])/maxy)
        print("preargs: ", data['x'], ", ", data['y'], ", ", data['w'], ", ", data['h'])
        print("args: ", x, ", ", y, ", ", w, ", ", h, ", ")
        # for ix in range(height):
        #     for ix2 in range(width):
        #         if not (ix>=x and ix<=x+w and ix2>=y and ix2<=y+h): 
        #             args.images[0][ix][ix2] = 0
        #             args.mask[ix][ix2] = 0
        #         else: args.mask[ix][ix2] = 1

        ims, masks = mask(args, self.siammask)
        print("im size: ", ims[0].shape, ', ', masks[0].shape)
        print("vid length: ", len(ims), ', ', len(masks))
        
        ims = [Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)) for image in ims]
        newmasks = []
        for i,m in enumerate(masks):
            img = Image.fromarray(np.uint8(m))
            mp = np.array(img.convert("L"))
            mp = np.array(mp > 0).astype(np.uint8)
            print("shape: ", mp.shape)
            # cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
            mp = cv2.dilate(mp, np.ones((50, 50), np.uint8), iterations=3)
            newmasks.append(mp*255)
            cv2.imwrite('bruh{:05d}.png'.format(i), mp*255)
        newmasks = [Image.fromarray(cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)) for mask in newmasks]
        print("NEWMASK: ", newmasks[0])

        # setup inpainting args
        args = argparse.Namespace()
        args.mask = newmasks
        args.frames = ims
        args.model = "e2fgvi_hq"
        args.step = 5
        args.num_ref = -1
        args.neighbor_stride = 1
        args.savefps = 24

        out = main_worker(self.model, args, torch.device("cpu"))

        id = str(uuid.uuid4())

        if not os.path.exists(f"{id}.mp4"):
            open(f"{id}.mp4", 'w+')

        with open(f"{id}.mp4", 'wb') as f:
            f.write(out.getbuffer())

        res = self.client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
        print(res)
        
        url = self.client.storage.from_('videos').get_public_url(f"{id}.mp4")

        return url


if __name__=="__main__":
    i = InpaintHandler()
    i.initialize()