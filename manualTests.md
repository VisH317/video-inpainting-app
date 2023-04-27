## Manual Tests to run for TorchServe server

**Main:**
 * curl -X POST http://localhost:8080/predictions/inpaint -F "data=@/home/vish/projects/deep-video-inpainting-server/DAVIS_demo/bmx-trees.mp4" -F "x=0" -F "y=0" -F "w=64" -F "h=64"