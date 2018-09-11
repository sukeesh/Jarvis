FROM debian:jessie

ENV DEBIAN_FRONTEND noninteractive
RUN echo 'deb http://deb.debian.org/debian jessie-backports contrib non-free main' >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install --no-install-recommends \
            build-essential \
            chromedriver \
            chrpath \
            dbus-x11 \
            ffmpeg \
            libdbus-1-dev \
            libdbus-glib-1-dev \
            libespeak1 \
            libffi-dev \
            libfontconfig1-dev \
            libfreetype6-dev \
            libnotify-cil-dev \
            libssl-dev \
            libxft-dev \
            notification-daemon \
            python3 \
            python3-dbus \
            python-imdbpy \
            python3-notify2 \
            python3-pip \
            screenfetch \
            sudo \
            wget \
            xdg-utils \
            xorg  && \
     rm -rf /var/lib/apt/lists/*


RUN wget -qO - https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 | tar -C /usr/local/share -xjf - && \
  ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs

RUN useradd -Um jarvis && echo "jarvis  ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY --chown=jarvis:jarvis . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir dbus-python imdbpy && \
    ./docker/docker.sh

USER jarvis

EXPOSE 80

ENTRYPOINT ["/app/jarvis"]
