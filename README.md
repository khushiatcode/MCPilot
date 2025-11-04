# 🚀 MCPilot

An AI assistant powered by Google Gemini that can actually **do things** - not just chat about them.

MCPilot uses the Model Context Protocol (MCP) to interact with real tools: browse the web, manage files, run git commands, and automate browser tasks - all through natural language.

## ✨ Features

- 🤖 **AI-Powered**: Powered by Google Gemini 2.0 Flash
- 🌐 **Browser Automation**: Navigate websites, take screenshots, fill forms (Playwright)
- 🔍 **Web Search**: Search the internet for information (DuckDuckGo)
- 📁 **File Operations**: Read, write, create, and manage files (Filesystem)
- 🔧 **Git Integration**: Check status, create branches, review commits (Git)
- 💬 **Memory**: Maintains conversation context across interactions
- 🎨 **Modern UI**: Clean web interface built with Gradio

## 🎯 Real-World Use Cases

**Debugging Workflow:**
```
"Review my last commit, find the issue, search for solutions, create a fix branch"
```

**Research & Documentation:**
```
"Search for 'Python async best practices', create a file with the top 5 patterns, then show git status"
```

**Code Review:**
```
"Check my git status, review all changed Python files, and create a summary of modifications"
```

**Web Automation:**
```
"Go to https://example.com, take a screenshot, then search the web for similar sites"
```

## 🛠️ Tech Stack

- **LLM**: Google Gemini 2.0 Flash (via LangChain)
- **MCP Framework**: mcp-use
- **UI**: Gradio
- **MCP Servers**:
  - Playwright (Browser automation)
  - DuckDuckGo Search (Web search)
  - Filesystem (File operations)
  - Git (Version control)

## 📋 Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Node.js and npx (for MCP servers)
- Google Gemini API key

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd mcpproj1
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Configure MCP servers**
   Edit `browser_mcp.json` to customize MCP server paths if needed.

5. **Run the application**
   ```bash
   uv run python app.py
   # or
   python app.py
   ```

6. **Access the UI**
   Open your browser to `http://localhost:7860`

## 💡 Usage Examples

### Basic Commands

- `"What can you do?"` - See available capabilities
- `"servers"` - List connected MCP servers
- `"clear"` - Reset conversation history

### File Operations

```
"Create a file called demo.py with a hello world function"
"List all Python files in the current directory"
"Read app.py and summarize what it does"
```

### Git Operations

```
"Check git status"
"Create a new branch called feature-branch"
"Show me the last 3 commits"
```

### Web Search

```
"Search for latest Python 3.13 features"
"Find information about MCP protocol"
```

### Browser Automation

```
"Go to https://www.python.org and tell me the latest Python version"
"Navigate to https://github.com/trending and take a screenshot"
```

### Combined Workflows

```
"Search for 'best React patterns 2024', create a markdown file with the top 5, then show git status"
"Review my last commit, identify issues, search for solutions, create a fix branch"
```

## 🔧 Configuration

### MCP Servers

Edit `browser_mcp.json` to add or modify MCP servers:

```json
{
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "duckduckgo-search": {
            "command": "npx",
            "args": ["-y", "duckduckgo-mcp-server"]
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"]
        },
        "git": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "/path/to/repo"]
        }
    }
}
```

### Model Configuration

Edit `app.py` to change the Gemini model:

```python
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)
```

## 🐛 Troubleshooting

**Connection Issues:**
- If you see "Connection closed" errors, click the "🔄 Reconnect" button
- Check that all MCP servers are properly installed via npx
- Verify your `.env` file has the correct `GEMINI_API_KEY`

**MCP Servers Not Connecting:**
- Ensure Node.js and npx are installed
- Check that the paths in `browser_mcp.json` are correct
- Wait a few seconds after startup for servers to initialize

**Blank Page:**
- Hard refresh your browser (Cmd+Shift+R or Ctrl+Shift+R)
- Check the terminal for initialization errors
- Ensure port 7860 is not already in use

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Share your own MCP server integrations

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - For the amazing MCP framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - For the powerful LLM
- [LangChain](https://www.langchain.com/) - For the LLM integration
- [Gradio](https://www.gradio.app/) - For the beautiful UI framework


---

**Built with ❤️ using MCP, Gemini, and Python**

