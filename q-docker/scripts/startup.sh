#!/bin/bash
# ABOUTME: Entrypoint for the Amazon Q CLI Docker container.
# ABOUTME: Executes the 'q' command, passing all arguments to it.

set -e

exec /home/q-user/.local/bin/q "$@"
