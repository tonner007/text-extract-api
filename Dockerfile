FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Systémové závislosti
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libmagic-dev \
    libglib2.0-dev \
    poppler-utils \
    ghostscript \
    ffmpeg \
    pkg-config \
    automake \
    autoconf \
    libtool \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip setuptools wheel build
RUN pip install .

RUN chmod +x run.sh

CMD ["bash", "run.sh"]
