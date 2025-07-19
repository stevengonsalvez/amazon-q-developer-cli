# How to Integrate Amazon Q Externally

This guide provides instructions on how to integrate the Amazon Q CLI's authentication state into external tools and containerized environments.

## 1. Exporting Authentication Tokens

To enable external tools to authenticate with Amazon Q, you can export your authentication tokens using the `q user export-token` command. This command outputs the `accessToken` and `refreshToken` in a machine-readable JSON format.

**Security Warning:** Never share your authentication tokens. These tokens grant access to your AWS account.

```bash
q user export-token
```

Example Output:

```json
{
  "accessToken": "YOUR_ACCESS_TOKEN",
  "refreshToken": "YOUR_REFRESH_TOKEN"
}
```

## 2. Containerized Authentication

To use the `q` CLI within Docker containers without re-authenticating, you can mount the host's SQLite database file into the container. This shares your existing authentication state.

### Database File Locations:

*   **Linux:** `$HOME/.local/share/amazon-q/data.sqlite3`
*   **MacOS:** `$HOME/Library/Application Support/amazon-q/data.sqlite3`
*   **Windows:** `C:\Users\$USER\AppData\Local\amazon-q\data.sqlite3`

### Example Docker Command:

Replace `/path/to/your/host/data.sqlite3` with the actual path on your host machine, and `/path/in/container/data.sqlite3` with the desired path inside your Docker container (e.g., `/root/.local/share/amazon-q/data.sqlite3` for Linux-based containers).

```bash
docker run -v /path/to/your/host/data.sqlite3:/path/in/container/data.sqlite3 your-q-cli-image q chat
```

**Note:** Ensure the user inside the Docker container has appropriate read permissions for the mounted database file.
