FROM alpine:3.15.0

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --no-cache python3 python3-dev py-pip g++ gcc libxml2 libxslt musl-dev libxslt-dev linux-headers

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

WORKDIR /app
COPY ./main.py /app/main.py
COPY ./.secrets.toml /app/.secrets.toml
COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

CMD ["uvicorn", "main:app", "--workers=4","--host", "0.0.0.0", "--port", "6380"]
