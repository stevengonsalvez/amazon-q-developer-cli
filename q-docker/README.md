# Amazon Q CLI Docker Environment

This directory contains the necessary files to build and run the Amazon Q CLI (`q`) in a consistent and isolated Docker environment.

## Purpose

Running `q` inside Docker provides several benefits:

- **Isolation**: The CLI and its dependencies are contained, preventing conflicts with your host system's configuration.
- **Consistency**: Ensures that `q` runs in the same environment every time, regardless of the host machine's setup.
- **Shared Authentication**: By mounting the host's authentication database, you can log in once on your machine and use the same session inside the container without re-authenticating.

## Files

- `Dockerfile`: The recipe for building the Docker image. It installs necessary dependencies and the `q` CLI.
- `scripts/q-docker.sh`: A wrapper script to build the Docker image and run the container with the correct volume mounts.
- `scripts/startup.sh`: The entrypoint script inside the container that executes the `q` command.

## How It Works

The setup leverages Docker's volume mounting to share key configuration and state files from your host machine to the container.

### MCP Server Management

MCP (Model Context Protocol) servers extend the functionality of `q`. You can add custom servers by following these steps:

1.  **Define Servers**: Add your `q mcp add` or `q mcp add-json` commands to the `mcp-servers.txt` file.
2.  **Add Secrets**: If a server requires API keys or other secrets, add them to a `.env` file in this directory (e.g., `GITHUB_TOKEN=...`).
3.  **Rebuild the Image**: Run `./scripts/q-docker.sh --rebuild`. The `install-mcp-servers.sh` script will run during the build, substituting any `${VAR_NAME}` placeholders with values from your `.env` file and registering the tools with the `default` agent.

### Authentication

The most critical part is sharing the authentication state. The `q` CLI stores its authentication tokens in a SQLite database located at `~/.local/share/amazon-q/data.sqlite3`. The `q-docker.sh` script mounts this file directly into the container at the corresponding location for the container's user (`/home/q-user/.local/share/amazon-q/data.sqlite3`).

### Configuration

Similarly, the following configurations are also mounted:

- **Global Agents & MCP Config**: `~/.aws/amazonq` on the host is mapped to `/home/q-user/.aws/amazonq` in the container.
- **Settings**: `~/.local/share/amazon-q/settings.json` is mapped to ensure consistent settings.
- **Git & SSH**: Your host's `~/.gitconfig` and `~/.ssh` directory are mounted read-only to allow `q` to perform git operations inside the container using your identity.

### Project Directory

Your current working directory on the host is mounted to `/workspace` inside the container, allowing you to run `q` commands against your project files.

## Usage

1.  **Make the script executable:**

    ```bash
    chmod +x scripts/q-docker.sh
    ```

2.  **Run the script:**

    Navigate to your project directory and run the script. It will automatically build the Docker image on the first run.

    ```bash
    ./scripts/q-docker.sh
    ```

3.  **Interact with `q`:**

    You will be dropped into an interactive `q chat` session inside the container. You can also pass any `q` command to the script.

    ```bash
    # Start a chat session
    ./scripts/q-docker.sh chat

    # Run a different q command
    ./scripts/q-docker.sh version
    ```
