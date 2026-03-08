---
title: Installation
description: 1. Download a release from GitHub or build from source: go build -o custom-exporter ./cmd/exporter 2. Copy `configs/config.example.yaml` to `configs/config.yaml` and edit. 3. Run: ./custom-exporter -c
tags: [documentation, portfolio]
path: portfolio/custom-prometheus-exporter/installation
created: 2026-03-08T22:19:13.449206+00:00
updated: 2026-03-08T22:04:38.832902+00:00
---

# Installation

## Binary

1. Download a release from GitHub or build from source:

```bash
go build -o custom-exporter ./cmd/exporter
```

2. Copy `configs/config.example.yaml` to `configs/config.yaml` and edit.
3. Run:

```bash
./custom-exporter -config configs/config.yaml
```

## Docker

```bash
docker build -t custom-exporter:latest .
docker run -p 9108:9108 -v $(pwd)/configs/config.example.yaml:/app/config.yaml custom-exporter:latest
```

## systemd

```bash
sudo cp deploy/systemd/custom-prometheus-exporter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now custom-prometheus-exporter
```
