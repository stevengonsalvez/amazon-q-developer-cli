#!/bin/bash
# ABOUTME: Entrypoint for the Amazon Q CLI Docker container.
# ABOUTME: Executes the 'q' command, passing all arguments to it.

set -e

# Run MCP server installation as q-user
sudo -u q-user /home/q-user/.local/bin/q mcp add --agent default --name fs --command "npx -y @modelcontextprotocol/server-filesystem"

# Execute the q command as q-user with all arguments passed to the script
sudo -u q-user /home/q-user/.local/bin/q "$@"
