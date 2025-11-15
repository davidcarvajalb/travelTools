#!/bin/bash
podman run -it --rm \
  -v ./data:/app/data:Z \
  -v ./outputs:/app/outputs:Z \
  -v ./config:/app/config:Z \
  traveltools:latest \
  python -m travel_tools.step2_scrape "${@}"
