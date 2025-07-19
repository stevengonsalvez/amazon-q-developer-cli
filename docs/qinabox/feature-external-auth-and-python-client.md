
# Feature: External Authentication and Python SDK

## 1. Summary

This document outlines a plan to decouple the `q` CLI's authentication and API communication into reusable components. This will enable developers to integrate Amazon Q into a wider range of tools, custom scripts, and agentic frameworks.

The core deliverables are:
1.  A new CLI command to securely export authentication tokens.
2.  A new, installable Python SDK for interacting with the CodeWhisperer streaming API.
3.  A documented method for using the CLI's authentication state within containerized environments.

## 2. Motivation

The primary goal is to enhance developer flexibility and enable a broader ecosystem around the Amazon Q API. By exposing the authentication state and providing a Python-native client, we empower users to:

*   **Build custom tools:** Integrate Q's capabilities into their own scripts and applications.
*   **Develop agentic frameworks:** Use the Python SDK as a foundational piece for creating sophisticated AI agents that can leverage Q.
*   **Streamline DevOps:** Run `q` within Docker containers for CI/CD or remote development without needing to re-authenticate inside the container.

## 3. Phased Implementation

### Phase 1: Token Exporter Command

To enable external tools to authenticate, we must provide a mechanism to retrieve the current, valid access token.

*   **Command:** `q user export-token`
*   **Functionality:**
    *   Access the local SQLite database (`~/.local/share/amazon-q/data.sqlite3`).
    *   Retrieve the secret corresponding to the key `codewhisperer:odic:token`.
    *   Deserialize the token and check for expiration.
    *   If the token is expired, it will automatically use the `refresh_token` to acquire a new one and update the database.
    *   Output the valid `access_token` and `refresh_token` in a machine-readable JSON format.
*   **Security:** The command will print a prominent warning to `stderr` about the security risks of exposing authentication tokens.

### Phase 2: Python Streaming Client SDK

This phase involves creating a Python-native equivalent of the `amzn-codewhisperer-streaming-client` Rust crate.

*   **Project Structure:** A standard Python package that can be installed via `pip` (e.g., `pip install amazon-q-streaming-client`).
*   **Dependencies:**
    *   `httpx` for asynchronous HTTP requests.
    *   `pydantic` for data modeling and validation, mirroring the Rust structs.
*   **Core Components:**
    1.  **Pydantic Models:** Replicate all necessary data structures from the Rust client (e.g., `ConversationState`, `ChatMessage`, `ToolUse`) to ensure API contract compliance.
    2.  **`QStreamingClient` Class:** An async client that accepts an `access_token` during initialization. It will use an `httpx.AsyncClient` to manage requests and automatically inject the `Authorization: Bearer <token>` header.
    3.  **Async Generator for Streaming:** The `generate_assistant_response` method will be implemented as an `async def` that `yield`s parsed event objects (e.g., `AssistantResponseEvent`, `ToolUseEvent`), making it intuitive to use in Python's `async for` loops.

### Phase 3: Containerized Authentication

This phase focuses on enabling seamless use of `q` within Docker containers by leveraging the host's existing authentication state.

*   **Mechanism:** Use Docker's volume mounting feature (`-v` or `--mount`) to share the host's SQLite database file with the container.
*   **Host Path:** The absolute path to the database on the host machine (e.g., `$HOME/.local/share/amazon-q/data.sqlite3`).
*   **Container Path:** The corresponding path where the CLI will look for the database inside the container (e.g., `/root/.local/share/amazon-q/data.sqlite3`).
*   **Documentation:** A new `how-to-integrate-q-externally.md` guide will be created to provide clear, copy-pasteable instructions for this process.

## 4. Success Criteria

*   A user can successfully run `q user export-token` and receive a valid, non-expired access token.
*   A developer can `pip install` the new Python client and use it to successfully stream a response from the Amazon Q API using an exported token.
*   A user can execute `q chat` within a Docker container, using a volume mount for the database, without being prompted to log in again.
