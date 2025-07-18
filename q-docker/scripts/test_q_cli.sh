#!/bin/bash
# ABOUTME: Tests the Amazon Q CLI Docker container setup.

set -e

IMAGE_NAME="amazon-q-cli"

echo "--- Building Docker Image ---"
(cd q-docker && docker build -t "$IMAGE_NAME:latest" .)

echo "--- Running Container Test ---"

# Run a simple command that doesn't require login
OUTPUT=$(docker run --rm "$IMAGE_NAME:latest" version 2>&1 || true)

# Check if the output contains the expected version string
if echo "$OUTPUT" | grep -q "You are not logged in"; then
  echo "Test Passed: q CLI is installed and functional (not logged in)."
else
  echo "Test Failed: q CLI is not functional. Full Output:"
  echo "$OUTPUT"
  exit 1
fi

echo "--- Test Completed ---"
