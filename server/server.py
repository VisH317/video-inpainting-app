import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from mask import mask_setup, mask
from E2FGVI.test import setup, main_worker
import cv2
from PIL import Image
import torch
import uuid
import deepspeed

import argparse
# from mask import mask
# from inpaint import inpaint

args = argparse.Namespace()
args.resume = './server/cp/SiamMask_DAVIS.pth'
args.mask_dilation = 32
siammask, cfg = mask_setup(args)
tp_config = {
    "enabled": True,
    "tp_size": 2,
}
siammask = deepspeed.init_inference(
    siammask,
    dtype=torch.float,
    tensor_parallel=tp_config
)

inpaint_weights = './server/E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

args.model = "e2fgvi_hq"
args.set_size = True
args.height = "720"
args.width = "1280"
args.ckpt = inpaint_weights

model, size = setup(args)
model = deepspeed.init_inference(
    model,
    dtype=torch.float,
    tensor_parallel=tp_config
)

app = FastAPI()

class Item(BaseModel):
    file: UploadFile = File()
    x: int
    y: int
    w: int
    h: int

@app.get("/video")
def getvid(id : str = ""):
    return FileResponse(f'./results/{id}.mp4')

@app.post("/video")
def video(file: UploadFile = File(), x: str = Form(), y: str = Form(), w: str = Form(), h: str = Form()):
    args = argparse.Namespace()
    args.resume = 'cp/SiamMask_DAVIS.pth'
    args.mask_dilation = 32
    args.x = int(int(x)*256/330)
    args.y = int(int(y)*256/590)
    args.w = int(int(w)*256/330)
    args.h = int(int(h)*256/590)
    args.data = file.file

    ims, masks = mask(args, siammask, cfg)

    newmasks = []
    for m in masks:
        mp = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3)), iterations=4)
        newmasks.append(mp*255)
    newmasks = [Image.fromarray(cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)) for mask in newmasks]

    args = argparse.Namespace()
    args.mask = newmasks
    args.frames = ims
    args.model = "e2fgvi_hq"
    args.step = 10
    args.num_ref = -1
    args.neighbor_stride = 5
    args.savefps = 24

    out = main_worker(model, args, torch.device("cuda:0" if torch.cuda.is_available() else 'cpu'))

    id = str(uuid.uuid4())

    with open("results/{}.mp4".format(id), 'wb') as f:
        f.write(out.getbuffer())

    return { "id": id }
#     return FileResponse('./results/test.mp4')
#     # write into a file or find a way to send the direct stream data
#     # setup the arguments and run mask and paint, get the returned file and send raw