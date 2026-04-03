import asyncio
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import streamlit as st
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

SERVER_PATH = Path(__file__).parent / "server" / "server.py"


async def query_agent(question: str):
    client = MultiServerMCPClient(
        {
            "demo": {
                "command": sys.executable,
                "args": [str(SERVER_PATH)],
                "transport": "stdio",
            }
        }
    )
    tools = await client.get_tools()

    llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    agent = graph.compile()

    response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})

    tool_calls = []
    answer = ""

    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({"name": tc["name"], "input": tc["args"], "output": None})
        elif msg.__class__.__name__ == "ToolMessage":
            for tc in tool_calls:
                if tc["name"] == msg.name and tc["output"] is None:
                    tc["output"] = msg.content
                    break
        elif msg.__class__.__name__ == "AIMessage" and not getattr(msg, "tool_calls", None):
            answer = msg.content

    return tool_calls, answer


def run(question: str):
    try:
        return asyncio.run(query_agent(question))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(query_agent(question))
        finally:
            loop.close()


# --- UI ---

st.set_page_config(page_title="MCP + LangGraph Demo", page_icon="🤖", layout="centered")

st.title("🤖 MCP + LangGraph Agent Demo")
st.caption("A LangGraph ReAct agent that uses tools exposed via an MCP server.")

with st.expander("How it works", expanded=False):
    st.markdown("""
**MCP (Model Context Protocol)** is a standard protocol for exposing tools to LLMs.
The server and the agent are completely decoupled — the server doesn't know about Claude,
and the agent doesn't know how the tools are implemented.

```
Your question
     ↓
agent.py  →  Claude Haiku (decides which tool to use)
                  ↓
            server.py  →  external API or local logic
                  ↓
            result returned to agent
                  ↓
            Claude generates final answer
```

**Available tools**

| Tool | Description | Real API? |
|---|---|---|
| `get_weather` | Current weather for a city | Yes — wttr.in |
| `get_crypto_price` | Cryptocurrency price in USD | Yes — CoinGecko |
| `calculate` | Evaluate a math expression | No — local eval() |
| `search_news` | News headlines for a topic | No — simulated |
""")

st.divider()

question = st.text_input(
    "Ask something:",
    placeholder="e.g. What's the weather in London and the price of ethereum?",
)

if st.button("Run", type="primary", disabled=not question):
    with st.spinner("Agent is thinking..."):
        tool_calls, answer = run(question)

    if tool_calls:
        st.subheader("Tools executed")
        for i, tc in enumerate(tool_calls, 1):
            with st.expander(f"{i}. `{tc['name']}` — input: `{tc['input']}`", expanded=True):
                st.markdown(f"**Input:** `{tc['input']}`")
                st.markdown(f"**Output:** {tc['output']}")

    st.subheader("Answer")
    st.markdown(answer)
