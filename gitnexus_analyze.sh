#!/bin/bash
podman run --rm \
  --userns=keep-id \
  -v /mnt/d/cainiao:/workspace \
  -v gitnexus-data:/data/gitnexus \
  -w /workspace \
  ghcr.io/abhigyanpatwari/gitnexus:latest \
  node /app/gitnexus/dist/cli/index.js analyze --force
