FROM python:3.11-slim-bookworm

# Patch OS packages + C++ toolchain for compiling QuickFIX
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# Slow step (compiles QuickFIX), cached after the first build
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir quickfix==1.16.0 pytest

WORKDIR /src/fixrobot
ENV FIXROBOTPATH=/src/fixrobot