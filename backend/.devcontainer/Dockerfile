# https://mcr.microsoft.com/v2/devcontainers/python/tags/list
FROM mcr.microsoft.com/devcontainers/python:2.1-3.13-bookworm

ENV PYTHONUNBUFFERED 1

# Set environment variable for non-interactive installation
ARG DEBIAN_FRONTEND=noninteractive

USER root
RUN rm -f /etc/apt/sources.list.d/yarn.list
RUN apt update \
    && apt install -y build-essential \
    ca-certificates \
    curl \
    git \
    python3-dev \
    wget \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

USER vscode
RUN git config --global user.name "OttawaSTEM" \
    && git config --global user.email "ottawasteem@gmail.com" \
    && pip install --upgrade pip \
    && pip install uv