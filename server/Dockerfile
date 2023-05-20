FROM pytorch/torchserve

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["torchserve", "--start", "--ncs", "--ts-config config.properties"]