FROM pytorch/torchserve

WORKDIR /app
COPY . .

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

RUN pip install -r requirements.txt
RUN rm -rf inpaint.mar
RUN rm -rf server.zip
RUN zip -r server.zip .
RUN torch-model-archiver --model-name inpaint --version 1 --handler trackhandler.py --extra-files server.zip

CMD ["torchserve", "--start", "--ncs", "--ts-config config.properties"]