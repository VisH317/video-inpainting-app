import torch
import argparse
from ts.torch_handler.base_handler import BaseHandler
# custom handler for torchserve
import zipfile
import os
import subprocess

class InpaintHandler(BaseHandler):

    def __init__(self):
        self.initialized = False
        self.siammask = None
        self.model = None
        self.size = None
        self.device = None

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
        from server.E2FGVI.test import setup
        from server.mask import mask_setup

        self.mask_weights = 'cp/SiamMask_DAVIS.pth'
        self.inpaint_weights = 'E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

        # siammask setup args:
        args = argparse.Namespace()
        args.resume = 'cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        self.siammask = mask_setup(args)

        # inpaint setup args
        args.model = "e2fgvi_hq"
        args.set_size = True
        args.height = "720"
        args.width = "1280"
        args.ckpt = self.inpaint_weights

        model, size = setup(args)
        self.model = model
        self.size = size

    def inference(self, data, context):
        # data params: video (mp4), x, y, w, h (bounding box to inpaint)
        print("LISTING DIR: ", os.listdir())
        from server.E2FGVI.test import main_worker
        from server.mask import mask

        args = argparse.Namespace()
        args.resume = 'cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        args.x = int(int(data.x)*256/330)
        args.y = int(int(data.y)*256/590)
        args.w = int(int(data.w)*256/330)
        args.h = int(int(data.h)*256/590)
        args.data = data.data

        ims, masks = mask(args)

        # setup inpainting args
        args = argparse.Namespace()
        args.mask = masks
        args.frames = ims
        args.model = "e2fgvi_hq"
        args.step = 10
        args.num_ref = -1
        args.neighbor_stride = 5
        args.savefps = 24

        out = main_worker(self.model, self.size, args, self.device)

        return out
