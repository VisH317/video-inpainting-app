import torch
import argparse
# custom handler for torchserve
from .E2FGVI.test import setup, main_worker
from .mask import mask_setup, mask

class InpaintHandler(object):

    def __init__(self):
        self.initialized = False
        self.siammask = None
        self.model = None
        self.size = None
        self.device = None

    def initialize(self, context):
        properties = context.system_properties
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")) if torch.cuda.is_available() else "cpu")

        self.mask_weights = 'cp/SiamMask_DAVIS.pth'
        self.inpaint_weights = 'E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

        # siammask setup args:
        args = argparse.Namespace()
        args.resume = 'cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        siammask = mask_setup(args)

        # inpaint setup args
        args.model = "e2fgvi_hq"
        args.set_size = True
        args.height = "720"
        args.width = "1280"
        args.ckpt = self.inpaint_weights

        model, size = setup(args)
        self.model = model
        self.size = size

    def handle(self, data, context):
        # data params: video (mp4), x, y, w, h (bounding box to inpaint)
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

        out = main_worker(args)

        return out
