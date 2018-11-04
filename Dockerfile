FROM ubuntu:16.04
MAINTAINER Sreekanth T M tmsreekanth98@gmail.com
RUN apt-get update
WORKDIR /JARVIS
COPY . /JARVIS
RUN apt-get install -y python python-setuptools python3-pip
RUN pip install virtualenv
#RUN pip install -r requirements.txt
RUN ./setup.sh
RUN jarvis
