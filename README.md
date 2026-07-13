# Remediation_Search

Local document chunking and remediation lookup from processed chunks. Query a knowledge base of troubleshooting guides to find relevant remediation steps for Kubernetes and Azure issues.

## Quick Start

### Setup

Install the package in editable mode with its dependencies:

```bash
pip install -r requirements.txt
```

This runs `pip install -e .`, which installs the `Remediation_Search` project in editable mode, allowing you to:
- Run the `avi` CLI command from anywhere
- Import the package in Python: `from remediation_search import ...`
- Make code changes and see them reflected immediately without reinstalling

### How It Works

The entry point is smart — it auto-detects what you give it:

| Input | What happens |
|-------|-------------|
| A file path (`.docx`, `.pdf`, `.txt`, etc.) | Processes the document into chunks |
| A plain text string | Searches chunks and returns remediation steps |

### Process a Document

```bash
python -m remediation_search "Pod(s)inPendingState.docx"
```

Or use the CLI command:

```bash
avi "Pod(s)inPendingState.docx"
```

This parses the document, splits it into chunks, and saves them to `outputs/processed_chunks/`.

### Find Remediation Steps

Provide the root cause (e.g. an alert name or Kubernetes issue):

```bash
python -m remediation_search "Pod Pending State"
```

Or use the CLI command:

```bash
avi "Pod Pending State"
```

This searches the processed chunks and returns the most relevant remediation steps.

## Backend API For UI Integration

If your UI has a Remediation button on alerts, run this project as a backend API.

### Start API Server

Option 1:

```bash
avi-api
```

Option 2:

```bash
python -m remediation_search.api
```

The API startup settings now come from [`pyproject.toml`](pyproject.toml) under `tool.remediation_search.api`, so the default host, port, and reload mode are loaded automatically.

### API Endpoints

- GET /health
- POST /api/remediation
- POST /api/ingest

### Request Example

```json
{
    "alert_name": "Pod Pending Alert",
    "root_cause": "pod in pending",
    "limit": 3
}
```

### Response Example

```json
{
    "alert_name": "PodsInCrashloopbackoff.docx",
    "root_cause": "pod in pending",
    "status": "success",
    "steps": [
        {
            "rank": 1,
            "score": 14,
            "source": "PodsInCrashloopbackoff.docx",
            "chunk_id": "0",
            "content": "When a Kubernetes Pod is in the CrashLoopBackOff state..."
        }
    ],
    "message": "Found 1 remediation step(s)."
}
```

### Auth Stub (No JWT)

This API keeps the original API-key stub for the existing remediation endpoints:

- `GET /api/remediation/search` and `POST /api/remediation` use the `X-API-Key` header.
- If `AVI_API_KEY` is not set, auth is bypassed in dev mode.
- If `AVI_API_KEY` is set, `X-API-Key` must match.

Set key example:

```bash
export AVI_API_KEY="your-internal-key"
```

PowerShell:

```powershell
$env:AVI_API_KEY = "your-internal-key"
```

Example payload for the new ingest route:

```json
{
    "api_key": "your-internal-key",
    "alert_name": "Pod Pending Alert",
    "root_cause": "pod in pending",
    "limit": 3
}
```

### Test With curl

```bash
curl -X POST "http://localhost:8000/api/remediation" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: your-internal-key" \
    -d '{"alert_name":"Pod Pending Alert","root_cause":"pod in pending","limit":3}'
```

### Test With PowerShell

```powershell
$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "your-internal-key" }
$body = @{ alert_name = "Pod Pending Alert"; root_cause = "pod in pending"; limit = 3 } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/remediation" -Method Post -Headers $headers -Body $body
```

### Ingest a New Knowledge File

Use `POST /api/ingest` with `multipart/form-data`.

Postman fields:

- `file`: choose the document to ingest
- `api_key`: your token value

Example curl:

```bash
curl -X POST "http://localhost:8000/api/ingest" \
    -F "api_key=your-internal-key" \
    -F "file=@C:/path/to/your-file.docx"
```

Example PowerShell:

```powershell
$form = @{
    api_key = "your-internal-key"
    file = Get-Item "C:\path\to\your-file.docx"
}
Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Form $form
```

### Run Tests

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```
Remediation_Search/
├── README.md                          # This file
├── pyproject.toml                     # Package metadata and setuptools config
├── requirements.txt                   # Dependencies (default: pip install -e .)
├── outputs/                           # Output directory
│   └── processed_chunks/              # Ingested document chunks (JSON)
├── remediation_search/            # Main package
│   ├── __init__.py
│   ├── __main__.py                    # CLI entrypoint
│   ├── api/                           # FastAPI backend for UI integration
│   ├── core/                          # Domain models and entities
│   ├── services/                      # Business services (ingestion/remediation)
│   ├── strategies/                    # Matching/scoring strategies
│   ├── handlers/                      # Input handler chain
│   ├── formatters/                    # Response formatting
│   ├── processing/                    # Orchestration for CLI input processing
│   └── legacy/                        # Backward-compatible helper APIs
└── tests/                             # Unit tests
    └── test_remediation_finder.py     # Remediation finder module tests
```

## Key Features

- **Multi-format Support**: Parse PDF, DOCX, TXT, MD, CSV, JSON, PY, HTML, XML
- **Smart Dispatcher**: Single entry point auto-detects file input vs. root-cause query
- **Recursive Chunking**: Split documents intelligently with configurable overlap (1000 char chunks, 100 char overlap)
- **Relevance Scoring**: Composite strategy (token overlap, exact phrase, keyword sequence, fuzzy match)
- **SOLID Layering**: Categorized modules with clean separation of concerns and compatibility shims
- **Single CLI Command**: `avi` handles both ingestion and remediation lookup
- **Backend API**: FastAPI endpoint for UI-driven remediation workflows
- **Editable Install**: Development-friendly package setup for rapid iteration

## Configuration

Environment variables (via `.env`):
- `OPENAI_API_KEY` – Required for LangChain OpenAI integrations (if using embeddings)
- `AVI_API_KEY` – Optional API key for backend endpoint protection (non-JWT stub)
- Additional Azure Search credentials as needed for your deployment

See `.env.example` or LangChain documentation for detailed configuration.

## Development

To modify the ingestion or query logic:

1. Edit files in `remediation_search/`
2. Changes are immediately available in CLI commands and imports (thanks to editable install)
3. Run tests to validate:
   ```bash
   python -m unittest discover -s tests -v
   ```

## License

[Add your license here]

