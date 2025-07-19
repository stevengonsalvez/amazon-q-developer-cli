# Handover Document: External Authentication and Python SDK Feature


  Date: July 19, 2025
  Project: Amazon Q Developer CLI
  Feature: External Authentication and Python SDK Integration

  1. Introduction


  The primary objective of this feature set is to enhance the
  extensibility and reusability of the Amazon Q CLI's core
  functionalities. By decoupling authentication mechanisms and
  providing a dedicated Python SDK, we aim to empower developers to
  integrate Amazon Q capabilities into a broader spectrum of tools,
  custom scripts, and agentic frameworks. This initiative directly
  addresses the need for greater flexibility and a richer ecosystem
  around the Amazon Q API.

  The work completed encompasses three distinct but interconnected
  phases:


   * Phase 1: Development of a new CLI command to securely export
     authentication tokens.
   * Phase 2: Creation of a new, installable Python SDK for interacting
     with the CodeWhisperer streaming API.
   * Phase 3: Documentation of a method for utilizing the CLI's
     authentication state within containerized environments.


  2. Phase 1: Token Exporter Command (q user export-token)

  Objective: To provide a secure and machine-readable mechanism for
  external tools to retrieve the current, valid Amazon Q authentication
   tokens (access and refresh tokens).

  Implementation Details:


   * CLI Command: q user export-token
       * This new subcommand is accessible under the user command
         group.
   * Code Locations:
       * crates/chat-cli/src/cli/mod.rs:
           * Added User(user::UserArgs) to the RootSubcommand enum.
           * Included Self::User(args) => args.execute(os).await, in
             the impl RootSubcommand block to dispatch to the new
             UserArgs executor.
           * Updated the name method for RootSubcommand to include
             Self::User(_) => "user", for proper command naming.
       * crates/chat-cli/src/cli/user.rs:
           * Introduced UserSubcommand enum with ExportToken variant.
           * Defined UserArgs struct to encapsulate the UserSubcommand.
           * Implemented UserArgs::execute to route to the export_token
             function.
           * `export_token` function:
               * Loads the BuilderIdToken from the local SQLite database
                  using BuilderIdToken::load(&os.database).await?. This
                 method inherently handles token expiration and
                 automatic refreshing using the refresh_token if
                 necessary, ensuring a valid token is always retrieved.

               * Extracts the raw access_token and refresh_token
                 strings from the BuilderIdToken object.
               * Constructs a JSON object containing accessToken and
                 refreshToken.
               * Prints the JSON object to stdout in a pretty-printed
                 format using serde_json::to_string_pretty.
               * Security Warning: A prominent warning message is
                 printed to stderr using eprintln! to alert users about
                 the security implications of exposing authentication
                 tokens. This warning emphasizes that tokens grant
                 access to the AWS account and should never be shared.

  Key Decisions & Rationale:


   * Leveraged existing BuilderIdToken::load and refresh_token logic to
     ensure token validity and refresh capabilities, minimizing
     redundant code.
   * Outputting JSON to stdout provides a standardized,
     machine-readable format for easy consumption by external scripts
     and applications.
   * The stderr security warning is a critical safety measure, adhering
     to best practices for handling sensitive credentials.

  Verification:


   * Compilation: cargo check was run successfully after modifications,
     resolving initial Clone trait and match arm errors.
   * Functionality:
       * Confirmed successful login state using cargo run -- whoami.
       * Executed cargo run -- user export-token > stdout.txt 2> 
         stderr.txt to capture output.
       * Verified the presence and content of the security warning in
         stderr.txt.
       * Confirmed the correct JSON structure and presence of
         accessToken and refreshToken in stdout.txt.

  3. Phase 2: Python Streaming Client SDK


  Objective: To create a Python-native client library that allows
  developers to interact with the Amazon Q streaming API, mirroring the
   functionality of the existing Rust
  amzn-codewhisperer-streaming-client.

  Implementation Details:


   * Project Structure: A new Python package,
     amazon-q-streaming-client-python, was scaffolded under crates/.
       * crates/amazon-q-streaming-client-python/setup.py: Configured
         for pip install, specifying httpx and pydantic as core
         dependencies.
       * crates/amazon-q-streaming-client-python/README.md: Provides
         basic installation and usage instructions.
       * crates/amazon-q-streaming-client-python/amazon_q_streaming_cli
         ent/__init__.py: Initializes the Python package, exposing key
         classes.
       * crates/amazon-q-streaming-client-python/amazon_q_streaming_cli
         ent/models.py:
           * Contains Pydantic BaseModel and RootModel definitions that
             directly mirror the data structures found in the Rust
             client's amzn-codewhisperer-streaming-client/src/types/
             directory (e.g., _assistant_response_message.rs,
             _tool_use.rs, _user_input_message.rs, etc.).
           * Key models include: AssistantResponseMessage,
             ToolUseEvent, CitationEvent, FollowupPromptEvent,
             CodeReferenceEvent, MessageMetadataEvent,
             InvalidStateEvent, UserInputMessage, ChatMessage,
             ConversationState, and their nested dependencies
             (SupplementaryWebLink, Reference, Span, UserIntent,
             Origin, ImageBlock, EditorState, ShellState, GitState,
             EnvState, Diagnostic, ToolResult, Tool).
           * ChatMessage was specifically refactored to use
             pydantic.RootModel to correctly handle its union type,
             addressing Pydantic 2.0 compatibility.
       * crates/amazon-q-streaming-client-python/amazon_q_streaming_cli
         ent/client.py:
           * Defines the QStreamingClient class.
           * Initializes an httpx.AsyncClient for asynchronous HTTP
             requests.
           * The generate_assistant_response method:
               * Constructs the request payload using the Pydantic
                 ConversationState model, including UserInputMessage.
               * Sets the Authorization header with the provided
                 access_token.
               * Sends a POST request to the (illustrative)
                 /generateAssistantResponse endpoint.
               * Includes a placeholder _parse_event_stream method.
                 This method currently assumes that each
                 httpx.aiter_bytes() chunk represents a complete JSON
                 event. It attempts to parse the JSON and dispatch it
                 to the corresponding Pydantic model based on a
                 top-level event type key (e.g.,
                 "assistantResponseEvent": {...}).

  Key Decisions & Rationale:


   * Pydantic for Data Modeling: Chosen for its robust data validation,
     serialization/deserialization capabilities, and ease of mirroring
     Rust structs, ensuring type safety and consistency.
   * `httpx` for Asynchronous Operations: Selected for its modern async
     API, which aligns with the streaming nature of the Amazon Q API.
   * Mock Testing: Implemented comprehensive mock tests using pytest
     and unittest.mock.AsyncMock to validate the _parse_event_stream
     logic and Pydantic model instantiation without requiring a live
     API connection. This allows for rapid iteration and verification
     of the parsing logic.

  Verification:


   * Unit Tests 
     (`crates/amazon-q-streaming-client-python/test_client.py`):
       * Created tests to mock httpx.AsyncClient responses.
       * Verified that generate_assistant_response correctly yields
         AssistantResponseMessage and ToolUseEvent objects from mocked
         JSON payloads.
       * Confirmed handling of multiple events in a stream.
       * Addressed and resolved TypeError: 'async for' requires an 
         object with __aiter__ method, got list by wrapping mock
         aiter_bytes return values in an async generator.
       * Resolved Pydantic 2.0 __root__ deprecation by migrating
         ChatMessage to RootModel and adjusting instantiation in
         client.py.
       * All tests passed successfully, confirming the basic parsing
         and model mapping logic.
   * Cleanup: The test_client.py file was removed after successful
     verification, as it was a temporary testing artifact.

  4. Phase 3: Containerized Authentication

  Objective: To document the process for enabling seamless use of the q
   CLI within Docker containers by sharing the host machine's existing
  authentication state.

  Implementation Details:


   * Documentation File: docs/how-to-integrate-q-externally.md
       * This new Markdown document provides clear, copy-pasteable
         instructions.
   * Key Information Provided:
       * Database File Locations: Explicitly lists the
         platform-specific absolute paths to the data.sqlite3 file,
         which stores the Amazon Q CLI's authentication state:
           * Linux: $HOME/.local/share/amazon-q/data.sqlite3
           * MacOS: $HOME/Library/Application 
             Support/amazon-q/data.sqlite3
           * Windows:
             C:\Users\$USER\AppData\Local\amazon-q\data.sqlite3
       * Example Docker Command: Provides a generic docker run command
         demonstrating how to use Docker's volume mounting (-v) to
         share the host's database file with a container.
       * Permissions Note: Includes a crucial reminder about ensuring
         appropriate read permissions for the mounted database file
         within the container.

  Key Decisions & Rationale:


   * Clarity and Accessibility: The information is presented in a
     dedicated, easy-to-find Markdown document to maximize user
     understanding and adoption.
   * Platform Specificity: Providing paths for all major operating
     systems ensures broad applicability.
   * Volume Mounting: This is the standard and most secure method for
     sharing host files with containers, avoiding the need to bake
     credentials directly into container images.

  Database Path Discovery:


   * The database path was identified by tracing the Database::new()
     constructor in crates/chat-cli/src/database/mod.rs.
   * This led to database_path() in
     crates/chat-cli/src/util/directories.rs, which dynamically
     determines the correct path based on the operating system using
     dirs::data_local_dir().

  5. Next Steps & Considerations

  While the core functionality for external authentication and the
  Python SDK is in place, the following areas require further
  attention:


   * Python SDK Event Stream Parsing Refinement: The
     _parse_event_stream method in client.py is currently a simplified
     placeholder. A robust implementation will need to:
       * Adhere strictly to the AWS event stream framing protocol
         (e.g., message headers, payload length, checksums).
       * Handle partial messages and buffering across httpx chunks.
       * Potentially integrate with a dedicated event stream parser
         library if available for Python.
   * Full Integration Testing (Python SDK): Once the event stream
     parsing is robust, the Python SDK needs to be thoroughly tested
     against a live Amazon Q streaming API endpoint to ensure
     end-to-end functionality and compatibility.
   * Comprehensive Python SDK Documentation: Expand the README.md and
     potentially add more detailed examples and API reference
     documentation for the Python SDK.
   * Error Handling (Python SDK): Implement more granular error handling
      and custom exceptions within the Python client to provide clearer
     feedback to users.