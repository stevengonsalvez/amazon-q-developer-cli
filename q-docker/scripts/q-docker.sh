#!/bin/bash
# ABOUTME: Wrapper script to run Amazon Q CLI in a Docker container.
# ABOUTME: Handles project mounting, shared authentication, and configuration.

set -e

# Get the absolute path of the current directory
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# --- Configuration --- #
IMAGE_NAME="amazon-q-cli"

# --- Host-side directory setup --- #
# Determine the correct host paths based on the operating system
if [[ "$(uname)" == "Darwin" ]]; then
    # macOS
    HOST_Q_SHARE_DIR="$HOME/Library/Application Support/amazon-q"
elif [[ "$(uname)" == "Linux" ]]; then
    # Linux
    HOST_Q_SHARE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/amazon-q"
else
    # For now, we'll default to the Linux path for other OSes.
    # A more robust solution would handle Windows paths if this script were to be used with WSL.
    HOST_Q_SHARE_DIR="$HOME/.local/share/amazon-q"
fi
HOST_Q_CONFIG_DIR="$HOME/.aws/amazonq"

mkdir -p "$HOST_Q_SHARE_DIR"
mkdir -p "$HOST_Q_CONFIG_DIR"

# --- Build the Docker image if it doesn't exist --- #
if ! docker image inspect "$IMAGE_NAME:latest" >/dev/null 2>&1; then
    echo "Building Docker image for Amazon Q CLI ($IMAGE_NAME)..."
    # Pass environment variables from .env as build arguments
    if [ -f "$PROJECT_ROOT/.env" ]; then
        BUILD_ARGS+=$(sed 's/^/ --build-arg /' "$PROJECT_ROOT/.env" | tr '\n' ' ')
    fi

    eval "docker build $NO_CACHE $BUILD_ARGS -t \"$IMAGE_NAME:latest\" \"$PROJECT_ROOT\""
fi

# --- Prepare Docker run arguments --- #
# Mount the current project directory
MOUNT_ARGS="-v \"$CURRENT_DIR:/workspace\""

# Mount the authentication database and settings
MOUNT_ARGS+=" -v \"$HOST_Q_SHARE_DIR/data.sqlite3:/home/q-user/.local/share/amazon-q/data.sqlite3\""
MOUNT_ARGS+=" -v \"$HOST_Q_SHARE_DIR/settings.json:/home/q-user/.local/share/amazon-q/settings.json\""

# Mount the global agents and MCP configuration
MOUNT_ARGS+=" -v \"$HOST_Q_CONFIG_DIR:/home/q-user/.aws/amazonq\""

# Mount git and ssh configuration for seamless git operations
if [ -f "$HOME/.gitconfig" ]; then
    MOUNT_ARGS+=" -v \"$HOME/.gitconfig:/home/q-user/.gitconfig:ro\""
fi
if [ -d "$HOME/.ssh" ]; then
    MOUNT_ARGS+=" -v \"$HOME/.ssh:/home/q-user/.ssh:ro\""
fi

# --- Run the container --- #
echo "Starting Amazon Q CLI in Docker..."

eval "docker run -it --rm \
    $MOUNT_ARGS \
    --workdir /workspace \
    --name amazon-q-cli-$(basename \"$CURRENT_DIR\")-$$ \
    $IMAGE_NAME:latest \"$@\""