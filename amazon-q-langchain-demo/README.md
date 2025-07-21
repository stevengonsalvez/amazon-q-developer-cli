# Amazon Q LangChain Integration

A comprehensive LangChain integration for Amazon Q, providing seamless access to Amazon Q's capabilities through the familiar LangChain interface.

## 🚀 Features

- ✅ **Drop-in Replacement**: Use `ChatAmazonQ` exactly like `ChatOpenAI`
- ✅ **Automatic Token Management**: Seamless CLI integration with auto-refresh
- ✅ **Streaming Support**: Full async streaming with LangChain's streaming interface
- ✅ **LangGraph Compatible**: Works with all LangGraph workflows
- ✅ **Advanced Workflows**: Multi-step agentic code review assistant
- ✅ **Production Ready**: Comprehensive error handling and logging
- ✅ **Type Safe**: Full type hints and Pydantic validation

## 📦 Installation

```bash
# Basic installation
pip install -e .

# With demo dependencies
pip install -e ".[demo]"

# Development installation
pip install -e ".[dev]"
```

## 🏃 Quick Start

### 1. Prerequisites

Make sure you have the Amazon Q CLI installed and are logged in:

```bash
# Install Amazon Q CLI (if not already installed)
# Follow instructions at: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-installing.html

# Login to Amazon Q
q login

# Verify login works
q whoami
```

### 2. Basic Usage

```python
from amazon_q_langchain import ChatAmazonQ
from langchain_core.messages import HumanMessage

# Initialize (just like ChatOpenAI)
llm = ChatAmazonQ()

# Simple chat
response = llm.invoke([HumanMessage(content="Hello! Help me write a Python function.")])
print(response.content)

# Streaming
for chunk in llm.stream([HumanMessage(content="Explain async/await in Python")]):
    print(chunk.content, end="", flush=True)
```

### 3. Advanced Code Review Assistant

```bash
# Web interface
cd demo_apps/code_review_assistant
streamlit run app.py

# CLI interface
python cli.py -f script.py -d -v
```

## 🔧 Project Structure

```
amazon-q-langchain-demo/
├── amazon_q_langchain/          # Core LangChain wrapper
│   ├── chat_model.py           # ChatAmazonQ implementation
│   ├── token_manager.py        # CLI token management
│   └── __init__.py            # Package exports
├── demo_apps/                  # Demo applications
│   ├── simple_chat/           # Basic chat interface
│   └── code_review_assistant/ # Advanced LangGraph workflow
│       ├── workflows/         # LangGraph workflows
│       ├── app.py            # Streamlit web interface
│       ├── cli.py            # Command-line interface
│       └── tests/            # Comprehensive test suite
├── examples/                   # Usage examples
└── README.md                  # This file
```

## 🌊 LangGraph Integration

Works seamlessly with LangGraph for building agentic workflows:

```python
from langgraph.graph import StateGraph
from amazon_q_langchain import ChatAmazonQ

# Use in LangGraph workflows
llm = ChatAmazonQ()

def my_node(state):
    response = llm.invoke([HumanMessage(content=state["input"])])
    return {"output": response.content}

# Build your graph...
workflow = StateGraph(...)
workflow.add_node("analyze", my_node)
```

## 🧪 Examples

### Basic Chat Example

```bash
python examples/basic_usage.py
```

### Advanced Code Review Assistant

```bash
# Web interface
cd demo_apps/code_review_assistant
streamlit run app.py

# CLI interface
python cli.py -f script.py -d -v

# Run tests
pytest tests/ -v
```

## 🔍 Token Management

The integration automatically manages Amazon Q CLI tokens:

- **Automatic Refresh**: Tokens are refreshed automatically before expiration
- **Caching**: Tokens are cached locally to avoid unnecessary CLI calls
- **Error Handling**: Clear error messages for authentication issues

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=amazon_q_langchain

# Run specific test
pytest tests/test_chat_model.py -v
```

## 🐛 Troubleshooting

### Common Issues

1. **"CLI not found" error**
   ```bash
   # Make sure Amazon Q CLI is installed and in PATH
   q --version
   ```

2. **"Not logged in" error**
   ```bash
   # Login to Amazon Q
   q login
   q whoami  # Verify login
   ```

3. **Token refresh failures**
   ```python
   # Clear token cache and retry
   from amazon_q_langchain import TokenManager
   TokenManager().clear_cache()
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [Amazon Q CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line.html)
- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
