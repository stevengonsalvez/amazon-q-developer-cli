from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from enum import Enum

class SupplementaryWebLink(BaseModel):
    url: str
    title: str
    snippet: Optional[str] = None

class Span(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

class Reference(BaseModel):
    license_name: Optional[str] = None
    repository: Optional[str] = None
    url: Optional[str] = None
    recommendation_content_span: Optional[Span] = None

class UserIntent(str, Enum):
    APPLY_COMMON_BEST_PRACTICES = "APPLY_COMMON_BEST_PRACTICES"
    CITE_SOURCES = "CITE_SOURCES"
    CODE_GENERATION = "CODE_GENERATION"
    EXPLAIN_CODE_SELECTION = "EXPLAIN_CODE_SELECTION"
    EXPLAIN_LINE_BY_LINE = "EXPLAIN_LINE_BY_LINE"
    GENERATE_CLOUDFORMATION_TEMPLATE = "GENERATE_CLOUDFORMATION_TEMPLATE"
    GENERATE_UNIT_TESTS = "GENERATE_UNIT_TESTS"
    IMPROVE_CODE = "IMPROVE_CODE"
    SHOW_EXAMPLES = "SHOW_EXAMPLES"
    SUGGEST_ALTERNATE_IMPLEMENTATION = "SUGGEST_ALTERNATE_IMPLEMENTATION"

class FollowupPrompt(BaseModel):
    content: str
    user_intent: Optional[UserIntent] = None

class ToolUse(BaseModel):
    tool_use_id: str
    name: str
    input: Any  # This can be a complex JSON object

class AssistantResponseMessage(BaseModel):
    message_id: Optional[str] = None
    content: str
    supplementary_web_links: Optional[List[SupplementaryWebLink]] = None
    references: Optional[List[Reference]] = None
    followup_prompt: Optional[FollowupPrompt] = None
    tool_uses: Optional[List[ToolUse]] = None

class Origin(str, Enum):
    AI_EDITOR = "AI_EDITOR"
    CHATBOT = "CHATBOT"
    CLI = "CLI"
    CONSOLE = "CONSOLE"
    DOCUMENTATION = "DOCUMENTATION"
    GITLAB = "GITLAB"
    IDE = "IDE"
    MARKETING = "MARKETING"
    MD = "MD"
    MOBILE = "MOBILE"
    OPENSEARCH_DASHBOARD = "OPENSEARCH_DASHBOARD"
    SAGE_MAKER = "SAGE_MAKER"
    SERVICE_INTERNAL = "SERVICE_INTERNAL"
    UNIFIED_SEARCH = "UNIFIED_SEARCH"
    UNKNOWN_VALUE = "UNKNOWN"

class ImageFormat(str, Enum):
    JPEG = "JPEG"
    PNG = "PNG"

class ImageSource(BaseModel):
    bytes: str # Base64 encoded bytes

class ImageBlock(BaseModel):
    format: ImageFormat
    source: ImageSource

class TextDocument(BaseModel):
    file_path: str
    content: str
    programming_language: Optional[str] = None

class CursorState(BaseModel):
    position: int

class RelevantTextDocument(BaseModel):
    file_path: str
    content: str
    programming_language: Optional[str] = None

class EditorState(BaseModel):
    document: Optional[TextDocument] = None
    cursor_state: Optional[CursorState] = None
    relevant_documents: Optional[List[RelevantTextDocument]] = None
    use_relevant_documents: Optional[bool] = None
    workspace_folders: Optional[List[str]] = None

class ShellHistoryEntry(BaseModel):
    command: str
    exit_code: Optional[int] = None

class ShellState(BaseModel):
    shell_name: str
    shell_history: Optional[List[ShellHistoryEntry]] = None

class GitState(BaseModel):
    repository_root: Optional[str] = None
    branch_name: Optional[str] = None
    commit_id: Optional[str] = None
    staged_changes: Optional[str] = None
    unstaged_changes: Optional[str] = None
    untracked_files: Optional[str] = None

class EnvironmentVariable(BaseModel):
    name: str
    value: str

class EnvState(BaseModel):
    environment_variables: Optional[List[EnvironmentVariable]] = None

class AppStudioState(BaseModel):
    pass # Placeholder, as the Rust definition is empty

class DiagnosticLocation(BaseModel):
    file_path: str
    range: Span

class DiagnosticRelatedInformation(BaseModel):
    message: str
    location: DiagnosticLocation

class DiagnosticSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    HINT = "HINT"

class Diagnostic(BaseModel):
    message: str
    location: DiagnosticLocation
    severity: Optional[DiagnosticSeverity] = None
    source: Optional[str] = None
    code: Optional[str] = None
    related_information: Optional[List[DiagnosticRelatedInformation]] = None

class ConsoleState(BaseModel):
    pass # Placeholder, as the Rust definition is empty

class UserSettings(BaseModel):
    pass # Placeholder, as the Rust definition is empty

class AdditionalContentEntry(BaseModel):
    content_type: str
    content: str

class ToolResult(BaseModel):
    tool_use_id: str
    status: str # TODO: Make this an enum
    output: Optional[str] = None

class Tool(BaseModel):
    name: str
    description: Optional[str] = None
    input_schema: Optional[str] = None # JSON schema string

class UserInputMessageContext(BaseModel):
    editor_state: Optional[EditorState] = None
    shell_state: Optional[ShellState] = None
    git_state: Optional[GitState] = None
    env_state: Optional[EnvState] = None
    app_studio_context: Optional[AppStudioState] = None
    diagnostic: Optional[Diagnostic] = None
    console_state: Optional[ConsoleState] = None
    user_settings: Optional[UserSettings] = None
    additional_context: Optional[List[AdditionalContentEntry]] = None
    tool_results: Optional[List[ToolResult]] = None
    tools: Optional[List[Tool]] = None

class UserInputMessage(BaseModel):
    content: str
    user_input_message_context: Optional[UserInputMessageContext] = None
    user_intent: Optional[UserIntent] = None
    origin: Optional[Origin] = None
    images: Optional[List[ImageBlock]] = None
    model_id: Optional[str] = None

from pydantic import RootModel

class ChatMessage(RootModel):
    root: Union[AssistantResponseMessage, UserInputMessage]

class ChatTriggerType(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"

class ConversationState(BaseModel):
    conversation_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    current_message: ChatMessage
    chat_trigger_type: ChatTriggerType
    customization_arn: Optional[str] = None

class ToolUseEvent(BaseModel):
    tool_use_id: str
    name: str
    input: Optional[str] = None
    stop: Optional[bool] = None

class CitationTarget(str, Enum):
    PARAGRAPH = "PARAGRAPH"
    SENTENCE = "SENTENCE"
    WORD = "WORD"

class CitationEvent(BaseModel):
    target: CitationTarget
    citation_text: Optional[str] = None
    citation_link: str

class FollowupPromptEvent(BaseModel):
    followup_prompt: Optional[FollowupPrompt] = None

class CodeReferenceEvent(BaseModel):
    references: Optional[List[Reference]] = None

class MessageMetadataEvent(BaseModel):
    conversation_id: Optional[str] = None
    utterance_id: Optional[str] = None

class InvalidStateReason(str, Enum):
    INVALID_CONVERSATION_STATE = "INVALID_CONVERSATION_STATE"
    INVALID_REQUEST_CONTENT = "INVALID_REQUEST_CONTENT"
    INVALID_AUTH_TOKEN = "INVALID_AUTH_TOKEN"
    UNKNOWN_VALUE = "UNKNOWN"

class InvalidStateEvent(BaseModel):
    reason: InvalidStateReason
    message: str
