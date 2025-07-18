# ABOUTME: Docker image for Amazon Q CLI
# ABOUTME: Provides an isolated, consistent environment for running q chat with shared authentication.

FROM ubuntu:latest

# Install required system dependencies and common developer tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    sudo \
    gettext-base \
    jq \
    unzip \
    wget \
    zsh \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (gh)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt-get update \
    && sudo apt-get install gh -y

# Install GitLab CLI (glab)RUN curl -sL "https://packages.gitlab.com/install/repositories/gitlab/cli/script.deb.sh" | sudo bash     && sudo apt-get install -y glab

# Create a non-root user to match host user, avoiding permission issues with mounted volumes
ARG USER_UID=1001
ARG USER_GID=1001
RUN groupadd --gid $USER_GID q-user || true &&     useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash q-user &&     echo "q-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to the non-root user
USER q-user
WORKDIR /home/q-user

# Install the Amazon Q CLI
# Determine architecture and download the appropriate q CLI binary
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-x86_64-linux.zip" -o "q.zip"; \
    elif [ "$ARCH" = "arm64" ]; then \
        curl --proto '=https' --tlsv1.2 -sSf "https://desktop-release.q.us-east-1.amazonaws.com/latest/q-aarch64-linux.zip" -o "q.zip"; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    unzip q.zip &&     ./q/install.sh --no-confirm &&     rm q.zip && rm -rf q
ENV PATH="/home/q-user/.local/bin:${PATH}"
ENV PATH="/home/q-user/.local/bin:${PATH}"

# Set up directories for MCP server installation
USER root
WORKDIR /app
COPY mcp-servers.txt ./
COPY scripts/install-mcp-servers.sh ./
RUN chmod +x ./install-mcp-servers.sh

# Copy the startup script into the container and make it executable
COPY scripts/startup.sh /app/startup.sh

# Switch back to non-root user for the rest of the setup
USER q-user
WORKDIR /home/q-user

# Run the MCP server installation script
# This runs as the q-user to ensure configs are placed in the correct home directory
# RUN /app/install-mcp-servers.sh

# Set the entrypoint to our startup script
ENTRYPOINT ["/app/startup.sh"]