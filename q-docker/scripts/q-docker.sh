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

# --- Load environment variables from .env file --- #
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✓ Found .env file. Loading environment variables..."
    set -a # Automatically export all variables
    source "$PROJECT_ROOT/.env" 2>/dev/null || true
    set +a # Stop automatically exporting
else
    echo "⚠️  No .env file found at $PROJECT_ROOT/.env"
fi

# --- Build the Docker image if it doesn't exist --- #
if ! docker image inspect "$IMAGE_NAME:latest" >/dev/null 2>&1; then
    echo "Building Docker image for Amazon Q CLI ($IMAGE_NAME)..."
    # Pass environment variables from .env as build arguments
    if [ -f "$PROJECT_ROOT/.env" ]; then
        # Use a loop to add each variable from .env as a build-arg
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ "$line" =~ ^#.* ]] || [[ -z "$line" ]]; then
                continue
            fi
            # Extract variable name (before =)
            VAR_NAME=$(echo "$line" | cut -d '=' -f 1)
            BUILD_ARGS+=("--build-arg" "$VAR_NAME")
        done < "$PROJECT_ROOT/.env"
    fi

    docker build $NO_CACHE "${BUILD_ARGS[@]}" -t "$IMAGE_NAME:latest" "$PROJECT_ROOT"
fi

# --- Prepare Docker run arguments --- #
RUN_ARGS=(
    -it
    --rm
    -v "$CURRENT_DIR:/workspace"
    -v "$HOST_Q_SHARE_DIR/data.sqlite3:/home/q-user/.local/share/amazon-q/data.sqlite3"
    -v "$HOST_Q_SHARE_DIR/settings.json:/home/q-user/.local/share/amazon-q/settings.json"
    -v "$HOST_Q_CONFIG_DIR:/home/q-user/.aws/amazonq"
)

# Pass GITHUB_TOKEN and GITLAB_TOKEN if available
if [ -n "$GITHUB_TOKEN" ]; then
    RUN_ARGS+=(-e "GITHUB_TOKEN=$GITHUB_TOKEN")
    echo "✓ Passing GITHUB_TOKEN to container."
fi
if [ -n "$GITLAB_TOKEN" ]; then
    RUN_ARGS+=(-e "GITLAB_TOKEN=$GITLAB_TOKEN")
    echo "✓ Passing GITLAB_TOKEN to container."
fi

# Mount git and ssh configuration for seamless git operations
if [ -f "$HOME/.gitconfig" ]; then
    RUN_ARGS+=(-v "$HOME/.gitconfig:/home/q-user/.gitconfig:ro")
fi
if [ -d "$HOME/.ssh" ]; then
    RUN_ARGS+=(-v "$HOME/.ssh:/home/q-user/.ssh:ro")
fi

# --- Run the container --- #
echo "Starting Amazon Q CLI in Docker..."

docker run "${RUN_ARGS[@]}" 
    --workdir /workspace 
    --name "amazon-q-cli-$(basename "$CURRENT_DIR")-$" 
    "$IMAGE_NAME:latest" "$@" 