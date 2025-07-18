#!/bin/bash
# ABOUTME: Script to build the Amazon Q CLI Docker image.

set -e

IMAGE_NAME="amazon-q-cli"

echo "--- Building Docker Image ---"
docker build -t "$IMAGE_NAME:latest" q-docker/

echo "--- Build Completed ---"