#!/bin/bash
# ABOUTME: Installs MCP servers from the mcp-servers.txt configuration file.

set -e

APP_DIR="/app"
MCP_SERVERS_FILE="$APP_DIR/mcp-servers.txt"

echo "Installing MCP servers from configuration..."

if [ ! -f "$MCP_SERVERS_FILE" ]; then
    echo "ERROR: MCP servers configuration file not found: $MCP_SERVERS_FILE"
    exit 1
fi

# Read and process each line
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Check for required environment variables
    REQUIRED_VARS=$(echo "$line" | grep -oE '\$\{[a-zA-Z0-9_]+\}' | sed 's/\${\(.*\)}/\1/')
    SKIP_LINE=false
    for VAR in $REQUIRED_VARS; do
        if [ -z "${!VAR}" ]; then
            echo "WARNING: Skipping MCP server install. Required environment variable '$VAR' is not set."
            SKIP_LINE=true
            break
        fi
    done

    if [ "$SKIP_LINE" = true ]; then
        continue
    fi

    # Substitute environment variables in the command and execute it
    expanded_line=$(envsubst <<< "$line")
    echo "Running: $expanded_line"
    if eval "$expanded_line"; then
        echo "Successfully installed MCP server."
    else
        echo "WARNING: Failed to install MCP server from line: $line"
    fi
    echo "---------------------------------"
done < "$MCP_SERVERS_FILE"

echo "MCP server installation completed."
