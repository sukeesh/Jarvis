FROM python:3.6.5-jessie

env DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install \
            dbus-x11 \
            libdbus-1-dev \
            libespeak1 \
            libnotify-cil-dev \
            notification-daemon \
            sudo \
            xorg

RUN pip3 install virtualenv


COPY . /app
WORKDIR /app

RUN sudo /bin/bash ./docker.sh

RUN useradd -Um jarvis && echo "jarvis  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN chown -R jarvis /app
USER jarvis

RUN sudo /bin/bash ./setup.sh --python3

EXPOSE 80

# Remove root access for container users
RUN sudo sed -i '/^jarvis/d' /etc/sudoers

ENTRYPOINT ["/usr/local/bin/jarvis"]
