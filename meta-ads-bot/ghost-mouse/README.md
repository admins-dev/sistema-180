# 🐭 Ghost Mouse V2

**Sistema 180 — B2B Prospecting Engine**

Enterprise-grade lead prospecting pipeline built for quality over volume.

## Architecture

```
Ingestion → Normalization → Deduplication → Enrichment → Scoring → Qualification → Outreach
```

### 7 Layers

| Layer | Purpose |
|-------|---------|
| **Ingestion** | Import leads from CSV, Google Maps, directories |
| **Normalization** | Clean names, cities, domains, phones, niches |
| **Deduplication** | Exact (place_id/domain/phone) + Fuzzy (rapidfuzz) |
| **Enrichment** | Web signals, emails, social profiles (traceable) |
| **Scoring** | 7 auditable scores with explainable factors |
| **Qualification** | Gate: HOT/WARM/COLD/NURTURE/DISCARD |
| **Outreach** | Email/DM sequences (only for qualified leads) |

### 7 Scores

1. `data_quality` — How complete is the lead data?
2. `contactability` — Can we reach them?
3. `website_quality` — How good is their web presence?
4. `social_dependency` — Too dependent on Instagram?
5. `redesign_opportunity` — Would they benefit from our services?
6. `commercial_fit` — Do they match our ideal customer?
7. `outreach_readiness` — Ready for contact? (gate score)

## Quick Start

```bash
# 1. Install
pip install -e ".[dev]"

# 2. Configure
cp .env.example .env
# Edit .env with your settings

# 3. Initialize database
ghostmouse init

# 4. Import leads
ghostmouse import-csv leads.csv --source manual

# 5. Run full pipeline
ghostmouse pipeline

# 6. Check status
ghostmouse status
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `ghostmouse init` | Create database tables |
| `ghostmouse import-csv <file>` | Import leads from CSV |
| `ghostmouse normalize` | Normalize all raw leads |
| `ghostmouse dedupe` | Run deduplication |
| `ghostmouse score` | Calculate 7 scores |
| `ghostmouse qualify` | Assign lead grades |
| `ghostmouse pipeline` | Run all stages |
| `ghostmouse status` | System health check |

## Modes

| Mode | Description |
|------|-------------|
| `DEV` | Development with verbose logging |
| `DRY_RUN` | No external actions (default) |
| `PROD` | Live operations (validates API keys) |
| `SAFE_MODE` | Read-only, no writes |

## Tech Stack

- **Python 3.12** with type hints
- **SQLAlchemy 2.x** — ORM with SQLite + WAL mode
- **Pydantic** — Config validation + data contracts
- **Typer** — CLI framework
- **rapidfuzz** — Fuzzy string matching
- **phonenumbers** — Phone normalization
- **structlog** — Structured logging
- **Rich** — Beautiful terminal output

## Project Structure

```
ghost-mouse/
├── app/
│   ├── config/settings.py      # Pydantic-settings config
│   ├── domain/models/          # SQLAlchemy models (Lead, Contact, etc.)
│   ├── storage/db.py           # DB engine + sessions
│   ├── normalizers/            # 5 normalizers (name, city, domain, phone, niche)
│   ├── dedupe/                 # Exact + fuzzy deduplication
│   ├── scoring/scorer.py       # 7 auditable scores
│   ├── qualification/gate.py   # Lead qualification gate
│   ├── observability/          # Structured logging
│   └── cli.py                  # Typer CLI
├── tests/
│   └── unit/                   # Pure function tests
├── pyproject.toml
├── .env.example
└── README.md
```

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing
```

---

*Ghost Mouse V2 — Sistema 180 — Built for conversion, not for volume.*
