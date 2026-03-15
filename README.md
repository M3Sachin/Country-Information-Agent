# Country Info Agent

AI agent that answers questions about countries using REST Countries API. Built with LangGraph and FastAPI.

## Install

```bash
pip install -r requirements.txt
cp .env.example .env
# Get free PUTER_AUTH_TOKEN from https://puter.com/dashboard
```

## Get Free API Token

1. Go to https://puter.com/dashboard
2. Click "Copy" to copy your auth token
3. Paste it in your .env file as PUTER_AUTH_TOKEN

**FREE Gemini 2.5 Flash - No credit card needed!**

## Run

```bash
# API Server (http://localhost:8000/docs)
uvicorn country_info_agent.api.main:app --reload --log-level info

# CLI
python -m country_info_agent.cli.main
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/query` | Process query |

### Example

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the population of Germany?"}'
```

### Response

```json
{
  "answer": "Germany has a population of approximately 83.2 million.",
  "country": "Germany",
  "fields": ["population"]
}
```

## Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `PUTER_AUTH_TOKEN` | Required | Get from puter.com/dashboard |
| `GEMINI_MODEL` | gemini-2.5-flash | Gemini model name |
| `API_BASE_URL` | https://restcountries.com/v3.1 | REST Countries API |
| `API_TIMEOUT` | 10 | Request timeout (seconds) |
| `MAX_RETRIES` | 3 | Retry attempts |
| `LOG_LEVEL` | INFO | Logging level |

## Deploy to Render

See `render.yaml` for deployment configuration.

1. Push to GitHub
2. Connect to render.com
3. Add `PUTER_AUTH_TOKEN` env var (from puter.com/dashboard)
4. Deploy for free