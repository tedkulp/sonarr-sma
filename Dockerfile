FROM jrottenberg/ffmpeg:4.4-ubuntu as ffmpeg
FROM linuxserver/sonarr:latest

LABEL maintainer="mdhiggins <mdhiggins23@gmail.com>"

ENV SMA_PATH /usr/local/sma
ENV SMA_RS Sonarr
ENV SMA_UPDATE false

# Add files from ffmpeg
COPY --from=ffmpeg /usr/local/ /usr/local/

# get python3 and git, and install python libraries
RUN \
  apk update && \
  apk add \
  git \
  wget \
  python3 \
  py3-pip && \
  # make directory
  mkdir ${SMA_PATH} && \
  # download repo
  git clone https://github.com/mdhiggins/sickbeard_mp4_automator.git ${SMA_PATH} && \
  cat ${SMA_PATH}/setup/requirements.txt | sed 's/qtfaststart/qtfaststart\=\=24\.0/g' > ${SMA_PATH}/setup/requirements.txt && \
  # install pip, venv, and set up a virtual self contained python environment
  python3 -m pip install --user --break-system-packages --upgrade pip && \
  python3 -m pip install --user --break-system-packages virtualenv && \
  python3 -m virtualenv ${SMA_PATH}/venv && \
  ${SMA_PATH}/venv/bin/pip install -r ${SMA_PATH}/setup/requirements.txt && \
  # ffmpeg
  chgrp users /usr/local/bin/ffmpeg && \
  chgrp users /usr/local/bin/ffprobe && \
  chmod g+x /usr/local/bin/ffmpeg && \
  chmod g+x /usr/local/bin/ffprobe && \
  # cleanup
  rm -rf \
  /tmp/* \
  /var/lib/apt/lists/* \
  /var/tmp/*

RUN \
  apk update && \
  apk add libva libdrm libva-intel-driver && \
  rm -rf \
  /tmp/* \
  /var/lib/apt/lists/* \
  /var/tmp/*

EXPOSE 8989

VOLUME /config
VOLUME /usr/local/sma/config

# update.py sets FFMPEG/FFPROBE paths, updates API key and Sonarr/Radarr settings in autoProcess.ini
COPY extras/ ${SMA_PATH}/
COPY root/ /
