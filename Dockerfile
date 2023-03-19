FROM ubuntu:22.04


RUN mkdir /email && \
    apt update && apt install -y python3 python3-pip && apt clean 

COPY ./ /email

RUN cd /email && pip install -r requirements.txt

WORKDIR /email

CMD python3 main.py
