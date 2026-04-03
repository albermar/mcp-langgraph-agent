FROM python:3.12-slim

WORKDIR /app

COPY server/ ./server/
COPY agent/ ./agent/
COPY app.py .

RUN pip install --no-cache-dir \
    fastmcp \
    langchain-anthropic \
    langgraph \
    langchain-mcp-adapters \
    httpx \
    python-dotenv \
    streamlit

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
