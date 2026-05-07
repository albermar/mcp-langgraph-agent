# MCP + LangGraph Agent Demo

**Live demo: [mcp.alberto.network](https://mcp.alberto.network)**

A minimal but complete demo showing how a **LangGraph ReAct agent** uses tools exposed via an **MCP server** (Model Context Protocol).

## Architecture

```
  Browser (https://mcp.alberto.network)
           │
           ▼
┌──────────────────────────────────────────────┐
│                   app.py                     │
│              Streamlit UI  (port 8501)        │
│                                              │
│  MultiServerMCPClient  →  StateGraph (ReAct) │
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

# 3. Run the Streamlit app
streamlit run app.py

# Or run the headless agent demo directly
python agent/agent.py
```

## Deployment

The app is deployed on a personal VPS using Docker and exposed via a reverse proxy.

**Public URL: https://mcp.alberto.network**

### Docker (production)

```bash
# Build and start
ANTHROPIC_API_KEY=sk-... docker compose up -d

# The container runs:
# streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

The `docker-compose.yml` attaches the container to an external Docker network (`shared_net`) so a reverse proxy (e.g. Nginx/Caddy/Traefik) running on the same host can route `https://mcp.alberto.network` → `localhost:8501`.

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
├── app.py             # Streamlit UI — chat interface for the agent
├── server/
│   └── server.py      # FastMCP server — tool definitions
├── agent/
│   └── agent.py       # LangGraph agent — headless CLI demo
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```
