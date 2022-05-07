# FROM alpine:3.15.0
#
# RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
# RUN apk update && apk add --no-cache python3 python3-dev py-pip g++ gcc libxml2 libxslt musl-dev libxslt-dev linux-headers
FROM ubuntu:20.04

RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN sed -i 's/security.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt update && apt install -y python3 python3-pip python3-dev
ENV TZ=Asia/Shanghai

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
# https://pypi.tuna.tsinghua.edu.cn/simple
ENV LANG=C.UTF-8 PIP_MIRRORS="https://mirrors.cloud.tencent.com/pypi/simple"

WORKDIR /app
COPY ./main.py /app/main.py
COPY ./.secrets.toml /app/.secrets.toml
COPY ./requirements.txt /app/requirements.txt


RUN pip3 install --upgrade pip -i $PIP_MIRRORS
RUN pip3 install -r /app/requirements.txt --ignore-installed -i $PIP_MIRRORS

CMD ["uvicorn", "main:app", "--workers=4","--host", "0.0.0.0", "--port", "6380"]
