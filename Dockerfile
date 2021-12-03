FROM ubuntu:20.04

# remove several traces of debian python
RUN apt-get update -y && apt-get install python3-dev -y && apt-get autoremove -y && apt-get autoclean -y

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

COPY . /app

RUN pip3 install -r /app/requirements.txt

CMD ["cd", "/app", "uvicorn", "main:app", "--host=0.0.0.0","--port=7999"]
