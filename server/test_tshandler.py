import torch
import argparse
from ts.torch_handler.base_handler import BaseHandler
# custom handler for torchserve
import os
import io
import sys
import json
import base64
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

SUPABASE_URL="https://uwepaxzzdeivpecslmyh.supabase.co"
SUPABASE_ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3ZXBheHp6ZGVpdnBlY3NsbXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM3NzgyODQsImV4cCI6MTk5OTM1NDI4NH0.07v00Ciub-z4glwaomfeNkm5OkPuSeo65NNJgDj5S3I"

class InpaintHandler(BaseHandler):

    def __init__(self):
        self.initialized = False
        self.siammask = None
        self.model = None
        self.size = None
        self.device = None
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON)

    def initialize(self, context):
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        if not torch.cuda.is_available() or properties.get("gpu_id") is None:
            raise RuntimeError("This model is not supported on CPU machines.")
        self.device = torch.device("cuda:" + str(properties.get("gpu_id")))

        # with zipfile.ZipFile(model_dir + "/server.zip", "r") as zip_ref:
        #     zip_ref.extractall(model_dir)

        # # process = subprocess.call(["sudo", "./server/get_mask/make.sh"], shell=True)
        # # process.wait()

        # print("LISTING DIR: ", os.listdir("./server"))
        # from server.E2FGVI.test import setup
        # from server.mask import mask_setup

        # self.mask_weights = './server/cp/SiamMask_DAVIS.pth'
        # self.inpaint_weights = './server/E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

        # # siammask setup args:
        # args = argparse.Namespace()
        # args.resume = './server/cp/SiamMask_DAVIS.pth'
        # args.mask_dilation = 32
        # siammask, cfg = mask_setup(args)
        # tp_config = {
        #     "enabled": True,
        #     "tp_size": 2,
        # }
        # # siammask = deepspeed.init_inference(
        # #     siammask,
        # #     dtype=torch.float,
        # #     tensor_parallel=tp_config
        # # )
        # self.siammask = siammask
        # self.cfg = cfg

        # # inpaint setup args
        # args.model = "e2fgvi_hq"
        # args.set_size = True
        # args.height = "720"
        # args.width = "1280"
        # args.ckpt = self.inpaint_weights

        # model, size = setup(args)
        # # model = deepspeed.init_inference(
        # #     model,
        # #     dtype=torch.float,
        # #     tensor_parallel=tp_config
        # # )
        # self.model = model
        # self.size = size

    def preprocess(self, model_input):
        preprocessed_input = {
            "data": io.BytesIO(model_input[0]['data']),
            "x": int.from_bytes(model_input[0]['x'], byteorder=sys.byteorder),
            "y": int.from_bytes(model_input[0]['y'], byteorder=sys.byteorder),
            "w": int.from_bytes(model_input[0]['w'], byteorder=sys.byteorder),
            "h": int.from_bytes(model_input[0]['h'], byteorder=sys.byteorder),
        }

        return preprocessed_input
    
    def postprocess(self, input):
        # out = json.dumps(str(input))
        # out = base64.b64encode(input.read())
        # return [out]
        out = { 'url': input }
        return [out]
    

    def inference(self, data):
        # data params: video (mp4), x, y, w, h (bounding box to inpaint)
        # print("LISTING DIR: ", os.listdir())
        # from server.E2FGVI.test import main_worker
        # from server.mask import mask

        args = argparse.Namespace()
        args.resume = 'cp/SiamMask_DAVIS.pth'
        args.mask_dilation = 32
        args.x = int(int(data['x'])*256/330)
        args.y = int(int(data['y'])*256/590)
        args.w = int(int(data['w'])*256/330)
        args.h = int(int(data['h'])*256/590)
        args.data = data['data']

        i = io.BytesIO()

        id = str(uuid.uuid4())

        if not os.path.exists(f"{id}.mp4"):
            open(f"{id}.mp4", 'w+')

        with open("{}.mp4".format(id), 'wb') as f:
            f.write(args.data.getbuffer())

        print("storage: ", self.client.__dict__)
        res = self.client.storage.from_('videos').upload(f"{id}.mp4", f"{id}.mp4")
        print(res)
        
        url = self.client.storage.from_('videos').get_public_url(f"{id}.mp4")

        return url
        

        # ims, masks = mask(args, self.siammask, self.cfg)
        
        # ims = [Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)) for image in ims]
        # newmasks = []
        # for m in masks:
        #     mp = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)), iterations=4)
        #     newmasks.append(mp*255)
        # newmasks = [Image.fromarray(cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)) for mask in newmasks]
        # print("NEWMASK: ", newmasks[0])

        # # setup inpainting args
        # args = argparse.Namespace()
        # args.mask = newmasks
        # args.frames = ims
        # args.model = "e2fgvi_hq"
        # args.step = 10
        # args.num_ref = -1
        # args.neighbor_stride = 5
        # args.savefps = 24

        # out = main_worker(self.model, args, self.device)
        x = []

        return args.data


# if __name__=="__main__":
#     i = InpaintHandler()
#     i.initialize()