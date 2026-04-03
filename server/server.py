import httpx
from fastmcp import FastMCP

mcp = FastMCP("demo-server")


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://wttr.in/{city}?format=3", timeout=10)
        resp.raise_for_status()
        return resp.text.strip()


@mcp.tool()
async def get_crypto_price(coin: str) -> str:
    """Get current price in USD for a cryptocurrency (e.g. bitcoin, ethereum)."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"ids": coin.lower(), "vs_currencies": "usd"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()        
    if coin.lower() not in data:
        return f"Coin '{coin}' not found. Try 'bitcoin' or 'ethereum'."
    price = data[coin.lower()]["usd"]
    return f"{coin.capitalize()}: ${price:,.2f} USD"


@mcp.tool()
async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression (e.g. '2 ** 10', '(3 + 5) * 12')."""
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return "Error: only basic arithmetic operators are allowed."
    try:
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating expression: {e}"


@mcp.tool()
async def search_news(topic: str) -> str:
    """Return simulated recent news headlines for a topic."""
    headlines = [
        f"Breaking: Major developments in {topic} shake global markets",
        f"Experts weigh in on the future of {topic}",
        f"New study reveals surprising findings about {topic}",
        f"World leaders gather to discuss {topic} strategy",
        f"Startup raises $50M to disrupt the {topic} industry",
    ]
    return "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))


if __name__ == "__main__":
    mcp.run(transport="stdio")
