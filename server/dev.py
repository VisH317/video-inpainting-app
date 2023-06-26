from TrackAnything.track_anything import TrackingAnything
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
from supabase import create_client

app = FastAPI()

SUPABASE_URL="https://uwepaxzzdeivpecslmyh.supabase.co"
SUPABASE_ANON="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV3ZXBheHp6ZGVpdnBlY3NsbXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODM3NzgyODQsImV4cCI6MTk5OTM1NDI4NH0.07v00Ciub-z4glwaomfeNkm5OkPuSeo65NNJgDj5S3I"

load_dotenv("./server/.env")
client = create_client(SUPABASE_URL, SUPABASE_ANON)

sam_checkpoint = './server/saves/sam_vit_h_4b8939.pth'
xmem_checkpoint = './server/saves/XMem-s012.pth'
e2fgvi_checkpoint = './server/E2FGVI/release_model/E2FGVI-HQ-CVPR22.pth'

args = argparse.Namespace()
args.device = "cpu"
args.sam_model_type = "vit_h"

model = TrackingAnything(sam_checkpoint, xmem_checkpoint, e2fgvi_checkpoint, args)

@app.post("/predictions")
def handler(file: UploadFile = File(), x: str = Form(), y: str = Form(), w: str = Form(), h: str = Form(), maxx: str = Form(), maxy: str = Form()):
    pass