FROM python:3.13-bookworm
LABEL Pierre Augier <pierre.augier@univ-grenoble-alpes.fr>

RUN apt-get update
RUN apt-get install -y --no-install-recommends rsync

RUN rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && useradd -m -r -u 1000 -g appuser -s /bin/bash appuser -s /bin/bash && usermod -a -G sudo appuser
RUN echo appuser:appuser | chpasswd
USER appuser
ARG HOME=/home/appuser
RUN mkdir -p $HOME/opt
WORKDIR $HOME/opt
RUN echo $USER $HOME $PWD && whoami

RUN mkdir -p $HOME/.local/bin
ENV PATH=$HOME/.local/bin:$PATH

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN python -m pip install pdm --user
