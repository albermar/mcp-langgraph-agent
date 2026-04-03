import asyncio
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

SERVER_PATH = Path(__file__).parent.parent / "server" / "server.py"

DEMO_QUESTIONS = [
    "What is the weather in Tokyo right now? Also, what is the current price of bitcoin? What is 2 to the power of 16? And finally, search for news about artificial intelligence.",
]


async def run_agent(agent, question: str) -> None:
    print(f"\n{'='*60}")
    print(f"Q: {question}")
    print("-" * 60)
    response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    answer = response["messages"][-1].content
    print(f"A: {answer}")


async def main() -> None:
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
    print(f"Connected to MCP server. Tools available: {[t.name for t in tools]}\n")

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

    for question in DEMO_QUESTIONS:
        await run_agent(agent, question)

    print(f"\n{'='*60}")
    print("Demo complete.")


if __name__ == "__main__":
    asyncio.run(main())
