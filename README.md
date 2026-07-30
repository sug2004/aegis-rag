# AegisRAG

** AegisRAG ** — Production-ready document ingestion, retrieval, and generation system with LangGraph agentic core, NeMo Guardrails safety, Portkey LLM gateway, and RAGAS evaluation suite. Built with Python, Qdrant Cloud, Jina AI embeddings/reranking, and structured observability (Logfire + LangSmith).

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   DATA/         │────▶│  Ingestion   │────▶│  Qdrant Cloud   │
│  ├── true_data/ │     │  Pipeline    │     │  (Vector DB)    │
│  └── noisy_data/│     │              │     │                 │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  Local JSON  │
                       │  Backup      │
                       └──────────────┘
```

## Features

- **Multi-format document processing**: PDF, HTML, TXT, DOCX, PPTX
- **Semantic text chunking**: Configurable overlap and chunk size
- **Vector embeddings**: Pluggable providers (Gemini, Groq, etc.)
- **Qdrant Cloud integration**: Managed vector database with cosine similarity
- **Dual persistence**: Local JSON backup + cloud vector storage
- **Observability**: Logfire integration for tracing and monitoring
- **CLI interface**: Flexible ingestion commands with wipe/resume support

## Quick Start

### Prerequisites

- Python 3.10+
- Qdrant Cloud account (or local Qdrant instance)
- API keys for embedding provider (Gemini/Groq)

### Installation

```bash
# Clone and setup
git clone <repo-url>
cd Prod_Enterprise_RAG

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
# Qdrant Cloud
QDRANT_CLUSTER_ENDPOINT=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION=enterprise_rag

# Embedding Provider (choose one)
GEMINI_API_KEY=your-gemini-key
# GROQ_API_KEY=your-groq-key

# Optional: Logfire
LOGFIRE_TOKEN=your-logfire-token
```

### Usage

```bash
# Full ingestion with collection wipe (fresh start)
python -m app.ingestion.processor DATA --wipe

# Ingest specific directory with explicit source type
python -m app.ingestion.processor DATA/true_data true

# Resume ingestion (no wipe)
python -m app.ingestion.processor DATA
```

### CLI Arguments

| Argument | Description |
|----------|-------------|
| `DATA` | Path to data directory (default: `DATA`) |
| `true`/`noisy` | Explicit source type for single directory |
| `--wipe` | Delete and recreate Qdrant collection before ingestion |

## Project Structure

```
Prod_Enterprise_RAG/
├── app/
│   ├── config.py                    # Settings management
│   └── ingestion/
│       ├── processor.py             # Main pipeline orchestration
│       ├── loaders/                 # Document parsers
│       │   ├── __init__.py
│       │   ├── pdf.py
│       │   ├── html.py
│       │   ├── text.py
│       │   └── office.py
│       ├── chucking/
│       │   └── splitter.py          # Text chunking logic
│       └── services/
│           └── retrieval/
│               └── embeddings.py    # Embedding generation
├── DATA/
│   ├── true_data/                   # Curated documents
│   └── noisy_data/                  # Raw documents for testing
├── processed_data/                  # Local JSON backups
├── requirements.txt
└── .env                             # Configuration (not committed)
```

## Data Sources

### True Data (Curated)
- `job_management.html` - Job scheduling documentation
- `parallel_work_queue.txt` - Work queue implementation
- `pods_autoscale.html` - Kubernetes autoscaling guide

### Noisy Data (Raw)
- Technical PDFs, HTML docs, text files for noise robustness testing

## Configuration

Key settings in `app/config.py`:

```python
class Settings:
    QDRANT_CLUSTER_ENDPOINT: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str = "enterprise_rag"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "text-embedding-004"  # Gemini
```

## Observability

Integrated with [Logfire](https://logfire.pydantic.dev/) for:
- Distributed tracing across ingestion stages
- Performance metrics (embedding latency, indexing throughput)
- Error tracking and debugging
- Custom spans for each processing step

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format
black app/

# Lint
ruff check app/

# Type check
mypy app/
```

## License

MIT License - see LICENSE file for details.