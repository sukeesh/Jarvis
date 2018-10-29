FROM python:3

RUN apt-get update && apt-get install -y espeak libnotify-bin ffmpeg sudo cheese

RUN pip install virtualenv

RUN git clone https://github.com/sukeesh/Jarvis.git

WORKDIR Jarvis

RUN echo "\n" | ./setup.sh

CMD jarvis