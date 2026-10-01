# CRIEYA Assistant Chatbot

Production-ready backend API and domain intelligence agent for the **CRIEYA Pre-Incubation Hub**. The system integrates Smart India Hackathon (SIH) problem statements, CRIEYA innovation processes, Technology Readiness Levels (TRL), and institutional knowledge using FastMCP and Sarvam AI.

---

## Architecture

The application uses a decoupled, resilient multi-service architecture:

```text
       Client (Web App / Mobile / Postman)
                       │
                       ▼
       FastAPI Application (Port 8000 / $PORT)
           ├── Guardrails (Input length, injection detection)
           ├── CORS Middleware (Configurable origins)
           └── Health Probes (/health, /health/live, /health/ready)
                       │
                       ▼
            MCPClientManager (app/mcp/client.py)
           ├── Async-safe connection locking
           ├── Auto-reconnection on transport drops
           └── Health monitoring & ping verification
                       │ (SSE Transport)
                       ▼
        FastMCP Datastore Server (Port 9000 / SSE)
           ├── SIH Problem Statements Tool
           ├── Innovation Process & Annexures Tool
           ├── Pre-Incubation Hub QA Tool
           ├── Focus Areas & Technologies Tool
           └── Technology Readiness Level (TRL) Tool
                       │
                       ▼
             Domain Data Assets (data/)
```

---

## Repository Structure

```text
.
├── app/                          # FastAPI application package
│   ├── agent/
│   │   ├── agent.py              # LLM agent with tool-calling loop
│   │   └── prompts.py            # System prompt for CRIEYA scope
│   ├── api/
│   │   └── routes.py             # POST /api/v1/chat endpoint
│   ├── guard/
│   │   └── guard.py              # Input guardrails (length, injection)
│   ├── llm/
│   │   └── sarvam_client.py      # Sarvam AI LLM client wrapper
│   ├── mcp/
│   │   └── client.py             # MCPClientManager (retry, reconnect)
│   ├── models/
│   │   └── schemas.py            # Pydantic request/response models
│   ├── utils/
│   │   └── logger.py             # Logging configuration
│   ├── config.py                 # Centralized settings from env vars
│   ├── dependencies.py           # FastAPI dependency injection
│   └── main.py                   # FastAPI app factory, CORS, health probes
├── server/                       # FastMCP datastore server package
│   ├── core/
│   │   ├── loaders.py            # Dataset loaders (Excel, text)
│   │   ├── models.py             # Pydantic models for MCP tools
│   │   └── services.py           # Business logic for MCP tools
│   └── mcp_server.py             # FastMCP server entry point
├── data/                         # CRIEYA domain datasets (required at runtime)
│   ├── problem_statements.xlsx   # SIH problem statements
│   ├── crieya_innovation_process.xlsx  # Innovation process stages
│   ├── crieya_preincubation_hub.txt    # Hub institutional info
│   ├── crieya_focus.txt          # Focus areas and technologies
│   ├── trl_levels.txt            # Technology Readiness Level definitions
│   └── annexure_registry.xlsx    # Annexure reference data (reserved)
├── tests/                        # Unit test suite
│   ├── test_agent.py             # Agent response extraction tests
│   ├── test_api.py               # API endpoint and guardrail tests
│   └── test_loaders.py           # Dataset loader validation tests
├── config.yaml                   # Dataset path configuration
├── run.py                        # Production orchestrator (MCP + FastAPI)
├── pyproject.toml                # Project metadata and dependencies
├── uv.lock                       # Locked dependency versions
├── Dockerfile                    # Production container image
├── .dockerignore                 # Docker build exclusions
├── .env.example                  # Environment variable template
├── .python-version               # Python version pin (3.12)
└── README.md                     # This file
```

---

## Requirements

- **Python**: 3.12 or higher
- **uv**: Modern, high-performance Python package and project manager
- **Git**: Version control
- **Docker**: (Optional) For containerized deployments

---

## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/princesingh-ai/bot.git
cd bot
```

### 2. Create and Activate Virtual Environment

Do not use `uv pip`. Use standard `uv` commands:

**macOS / Linux:**
```bash
uv venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
uv venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Synchronize all project dependencies reproducibly from `uv.lock`:

```bash
uv sync
```

---

## Environment Configuration

Copy the example configuration file:

```bash
cp .env.example .env
```

Edit `.env` and supply your actual credentials:

```ini
# Required: Sarvam AI subscription key
SARVAM_API_KEY=your_sarvam_api_key_here

# Environment & Server
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# FastMCP Datastore Settings
MCP_HOST=127.0.0.1
MCP_PORT=9000
MCP_SERVER_URL=http://127.0.0.1:9000/sse
MCP_CONNECT_TIMEOUT_SECONDS=30.0
MCP_MAX_RETRIES=5

# CORS Configuration (comma-separated origins or * for all)
CORS_ORIGINS=*

# Security Guardrails
MAX_QUERY_LENGTH=2000
```

### Environment Variables Reference

| Variable | Required | Default | Description |
|:---|:---:|:---|:---|
| `SARVAM_API_KEY` | **Yes** | _(none)_ | Sarvam AI API subscription key |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | Server bind port (respected by both `run.py` and Dockerfile) |
| `MCP_HOST` | No | `127.0.0.1` | FastMCP server bind address |
| `MCP_PORT` | No | `9000` | FastMCP server bind port |
| `MCP_SERVER_URL` | No | `http://{MCP_HOST}:{MCP_PORT}/sse` | Full MCP SSE endpoint URL (auto-derived if not set) |
| `MCP_CONNECT_TIMEOUT_SECONDS` | No | `30.0` | Timeout for MCP client connection attempts |
| `MCP_MAX_RETRIES` | No | `5` | Max retry attempts for MCP connection |
| `CORS_ORIGINS` | No | `*` | Comma-separated allowed origins or `*` |
| `MAX_QUERY_LENGTH` | No | `2000` | Maximum allowed query character length |

> **Security Note:** Never commit `.env` or production credentials to version control. The `.gitignore` file is configured to exclude all `.env` files. The `.env.example` file is a safe template containing only placeholder values.

---

## Running Locally

To start both the FastMCP datastore server and the FastAPI application with coordinated readiness checks:

### Development Mode (with hot-reload)

```bash
uv run python run.py --reload
```

### Production Mode

```bash
uv run python run.py
```

The orchestrator (`run.py`) will:
1. Launch the FastMCP server on port 9000.
2. Poll the port via TCP until FastMCP is verified ready and accepting connections.
3. Launch the FastAPI server on port 8000.
4. Handle `SIGINT`/`SIGTERM` for clean shutdown of both processes.

---

## Running Tests

Execute the automated test suite:

```bash
uv run python -m unittest discover tests
```

The test suite validates:
- Domain dataset loaders and Excel/text parsing
- API liveness and readiness health endpoints
- Input security guardrails (prompt injection and query length rejection)
- Agent tool execution and LLM response handling

---

## API Documentation

### Base URLs

- **Local Development**: `http://localhost:8000`
- **Production**: `https://YOUR-PRODUCTION-URL.com`

---

### Primary Chat Endpoint

Processes user queries about CRIEYA, SIH problem statements, innovation stages, and TRL levels.

- **URL**: `POST /api/v1/chat`
- **Content-Type**: `application/json`

#### Request Body

```json
{
  "query": "What are the key focus areas of CRIEYA?"
}
```

| Field | Type | Required | Constraints |
|:---|:---|:---:|:---|
| `query` | `string` | Yes | Max 2000 characters (configurable via `MAX_QUERY_LENGTH`) |

#### Response (`200 OK`)

```json
{
  "response": "CRiEYA focuses on several key technological domains including Artificial Intelligence, IoT, Clean Energy, Healthcare Innovations, and Advanced Agriculture..."
}
```

#### Error Responses

| Status | Cause | Example |
|:---:|:---|:---|
| `400` | Guardrail: query too long or prompt injection detected | `{"detail": "Security Error: Your query contains disallowed commands or prompt override attempts."}` |
| `502` | Agent/LLM execution failure | `{"detail": "Agent service error: ..."}` |
| `503` | FastMCP backend is unreachable | `{"detail": "Backend MCP server is currently unavailable. Please try again shortly."}` |

#### Example cURL

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Smart India Hackathon problem statement for smart farming?"}'
```

---

### Health Check Endpoints

#### 1. Overall Health Check

- **URL**: `GET /health` (or `GET /health/ready`)
- **Status Codes**:
  - `200 OK` — Application and FastMCP backend are healthy.
  - `503 Service Unavailable` — Application is running but FastMCP is unreachable.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "mcp_connected": true,
  "version": "1.0.0",
  "environment": "production"
}
```

#### 2. Liveness Probe

- **URL**: `GET /health/live`
- **Status Code**: `200 OK`
- **Purpose**: Container orchestrator liveness verification.

**Response:**
```json
{
  "status": "alive"
}
```

---

## Docker

### Build the Image

```bash
docker build -t crieya-chatbot:latest .
```

### Run Container Locally

```bash
docker run -d \
  --name crieya-chatbot \
  -p 8000:8000 \
  --env-file .env \
  crieya-chatbot:latest
```

Or pass the API key directly:

```bash
docker run -d \
  --name crieya-chatbot \
  -p 8000:8000 \
  -e SARVAM_API_KEY="your_key_here" \
  -e ENVIRONMENT="production" \
  crieya-chatbot:latest
```

### Verify Container Health

```bash
# Liveness
curl http://localhost:8000/health/live

# Full health (includes MCP connectivity)
curl http://localhost:8000/health

# Chat smoke test
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is CRIEYA?"}'
```

### Dynamic Port

The container respects the `$PORT` environment variable. Both `run.py` and the Dockerfile `HEALTHCHECK` read `PORT` from the environment, making it compatible with platforms that inject `$PORT` (Google Cloud Run, AWS App Runner, Heroku, Render).

---

## Production Deployment

Follow these steps for any container-based cloud platform:

1. **Run tests locally:**
   ```bash
   uv run python -m unittest discover tests
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t crieya-chatbot:latest .
   ```

3. **Test the container locally** (see Docker section above).

4. **Tag and push to your container registry:**
   ```bash
   docker tag crieya-chatbot:latest <your-registry>/crieya-chatbot:latest
   docker push <your-registry>/crieya-chatbot:latest
   ```

5. **Create the cloud service** pointing to the container image.

6. **Configure environment variables in cloud settings:**
   - `SARVAM_API_KEY` — your valid Sarvam AI subscription key
   - `ENVIRONMENT` — `production`
   - `CORS_ORIGINS` — your frontend domain (e.g., `https://app.crieya.com`)

7. **Configure health checks:**
   - Path: `/health` (readiness) or `/health/live` (liveness)
   - Port: `8000` (or whatever `$PORT` is set to)

8. **Verify deployment:**
   ```bash
   curl https://YOUR-PRODUCTION-URL.com/health
   curl -X POST https://YOUR-PRODUCTION-URL.com/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is CRIEYA?"}'
   ```

---

## Data Files

The `data/` directory contains CRIEYA domain datasets that are **required runtime assets**. They are tracked in Git and copied into the Docker image.

| File | Purpose |
|:---|:---|
| `problem_statements.xlsx` | SIH problem statements with IDs, titles, categories, organizations |
| `crieya_innovation_process.xlsx` | Innovation process stages, inputs, processes, outputs |
| `crieya_preincubation_hub.txt` | Institutional info about CRIEYA (identity, programs, patents) |
| `crieya_focus.txt` | Focus areas, domains, and technologies |
| `trl_levels.txt` | Technology Readiness Level definitions (TRL 1–9) |
| `annexure_registry.xlsx` | Annexure reference data (reserved for future use) |

Dataset paths are configured in `config.yaml`. The loaders in `server/core/loaders.py` resolve all paths relative to the project root using `pathlib`.

---

## Security

- **Input guardrails**: All queries pass through `app/guard/guard.py` (length limits and prompt injection keyword blocklist) before reaching the LLM or MCP tools.
- **Non-root container**: The Docker image runs under a dedicated `appuser` account.
- **Secrets isolation**: `.env` is gitignored. No credentials are baked into the Docker image, source code, or Git history.
- **CORS**: Defaults to `*` for development. Set `CORS_ORIGINS` to your specific frontend domain in production.
- **Authentication**: The API does not enforce authentication. For production, add an API gateway, reverse proxy, or authentication middleware.

---

## Troubleshooting

| Issue | Cause | Solution |
|:---|:---|:---|
| `503 Service Unavailable` on `/health` | FastMCP subprocess failed to start or port 9000 is occupied | Check if another process uses port 9000. Verify `data/` files exist and `config.yaml` is valid |
| `RuntimeError: SarvamAI client is not initialized` | `SARVAM_API_KEY` is missing or invalid | Set a valid `SARVAM_API_KEY` in `.env` or container environment |
| `FileNotFoundError: Required dataset file not found` | Datasets under `data/` were omitted | Ensure all files listed in `config.yaml` are present in `data/` |
| `400 Bad Request: Security Error` | Query triggered guardrail regex | Remove prompt-override phrases like "ignore previous instructions" |
| `502 Bad Gateway` on `/api/v1/chat` | Agent or LLM execution error | Check logs for Sarvam AI errors; verify API key validity |
| `CORS Error in Browser` | Frontend domain not in `CORS_ORIGINS` | Add your frontend URL to `CORS_ORIGINS` in `.env` |

---

## Checklist

Use this checklist when deploying to a new environment:

- [ ] Clone the repository and verify all files in `data/` are present
- [ ] Install Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- [ ] Run `uv sync` to install dependencies
- [ ] Copy `.env.example` to `.env` and set `SARVAM_API_KEY` to a valid key
- [ ] Run `uv run python -m unittest discover tests` — all tests must pass
- [ ] Run `uv run python run.py` and verify `/health` returns `{"status": "healthy"}`
- [ ] Test `POST /api/v1/chat` with a CRIEYA question
- [ ] Build Docker image: `docker build -t crieya-chatbot:latest .`
- [ ] Run Docker container and verify health and chat endpoints
- [ ] For production: set `CORS_ORIGINS` to your frontend domain
- [ ] For production: add authentication at the ingress/gateway level
- [ ] Never commit `.env` or API keys to version control
- [ ] Rotate `SARVAM_API_KEY` if it was ever exposed in logs or history
