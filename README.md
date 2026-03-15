# Country Info Agent

AI agent that answers questions about countries using REST Countries API. Built with LangGraph and FastAPI.

## Install

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY
```

## Run

```bash
# API Server (http://localhost:8000/docs)
uvicorn country_info_agent.api.main:app --reload --log-level info

# CLI
python -m country_info_agent.cli.main
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root |
| GET | `/health` | Health check |
| POST | `/query` | Process query |

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the population of Germany?"}'
```

## Config (.env)

| Variable | Default |
|----------|---------|
| `GOOGLE_API_KEY` | Required |
| `GEMINI_MODEL` | gemini-1.5-flash |
| `API_BASE_URL` | https://restcountries.com/v3.1 |
| `API_TIMEOUT` | 10 |
| `MAX_RETRIES` | 3 |
| `LOG_LEVEL` | INFO |