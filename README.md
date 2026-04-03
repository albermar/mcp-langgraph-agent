# MCP + LangGraph Agent Demo

A minimal but complete demo showing how a **LangGraph ReAct agent** uses tools exposed via an **MCP server** (Model Context Protocol).

## Architecture

```
┌──────────────────────────────────────────────┐
│                agent/agent.py                │
│                                              │
│  MultiServerMCPClient  →  create_react_agent │
│  (langchain-mcp-adapters)   (langgraph)      │
│                                              │
│  Claude Haiku decides which tool to call     │
│  and when to stop based on the question.     │
└───────────────────┬──────────────────────────┘
                    │ stdio transport
┌───────────────────▼──────────────────────────┐
│               server/server.py               │
│                                              │
│  FastMCP server — 4 tools:                   │
│  • get_weather(city)       → wttr.in API     │
│  • get_crypto_price(coin)  → CoinGecko API   │
│  • calculate(expression)   → eval() locally  │
│  • search_news(topic)      → fake headlines  │
└──────────────────────────────────────────────┘
```

### Key concepts

| Concept | Where | Why it matters |
|---|---|---|
| **MCP** | `server/server.py` | Standard protocol for exposing tools to LLMs — server/client separation |
| **FastMCP** | `server/server.py` | Minimal decorator-based MCP server (`@mcp.tool()`) |
| **LangGraph ReAct** | `agent/agent.py` | Agent loop: think → call tool → observe → repeat until done |
| **MultiServerMCPClient** | `agent/agent.py` | Connects to one or more MCP servers, converts tools to LangChain format |
| **Async Python** | everywhere | `async def` + `httpx` for non-blocking I/O |

## Setup

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY

# 3. Run the demo
python agent/agent.py
```

## Expected output

```
Connected to MCP server. Tools available: ['get_weather', 'get_crypto_price', 'calculate', 'search_news']

============================================================
Q: What is the weather in Tokyo right now?
------------------------------------------------------------
A: The current weather in Tokyo is 18°C, partly cloudy.

============================================================
Q: What is the current price of bitcoin?
...
```

## Project structure

```
mcp-langgraph-agent/
├── server/
│   └── server.py      # FastMCP server — tool definitions
├── agent/
│   └── agent.py       # LangGraph agent — connects to server, runs demo
├── requirements.txt
├── .env.example
└── README.md
```
