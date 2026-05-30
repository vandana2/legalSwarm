# LegalSwarm Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                     │
│            React + Tailwind + TypeScript                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Routes                                          │  │
│  │  POST /api/contracts/analyze   (PDF upload)      │  │
│  │  POST /api/contracts/analyze-text (raw text)     │  │
│  │  POST /api/analyze/contract    (text, compat)    │  │
│  │  POST /api/upload/contract     (upload only)     │  │
│  └──────────────────┬───────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Orchestration (crew_orchestrator.py)            │  │
│  │  ContractAnalysisCrew – direct Python pipeline   │  │
│  └──────────────────┬───────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Six-Agent Pipeline                              │  │
│  │                                                  │  │
│  │  1. ParserAgent       (deterministic)            │  │
│  │  2. RiskDetectorAgent (deterministic)            │  │
│  │  3. ExplainerAgent    (deterministic)            │  │
│  │  4. RedlineAgent      (deterministic, filtered)  │  │
│  │  5. ComplianceAgent   (deterministic)            │  │
│  │  6. VerdictAgent      (deterministic aggregator) │  │
│  │                                                  │  │
│  │  Optional LLM enhancement via AIService          │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                ┌────▼────┐
                │ OpenAI  │  (optional – LLM enhancement)
                │  API    │
                └─────────┘
```

## Component Breakdown

### Frontend
- **Next.js 14** – React framework with server-side rendering
- **TypeScript** – type-safe development
- **Tailwind CSS** – utility-first styling

### Backend
- **FastAPI** – Python web framework
- **Pydantic v2** – data validation and schema definition
- **PyPDF2** – PDF text extraction
- **OpenAI SDK ≥ 1.x** – optional LLM calls (gpt-4o-mini default)

### Six-Agent Pipeline

| # | Agent | Implementation | Purpose |
|---|-------|----------------|---------|
| 1 | **ParserAgent** | `agents/parser_agent.py` | Extracts and structures clauses using regex |
| 2 | **RiskDetectorAgent** | `agents/risk_detector_agent.py` | Rule-based risk classification (CRITICAL→MINIMAL) |
| 3 | **ExplainerAgent** | `agents/explainer_agent.py` | Plain-English explanations with glossary lookup |
| 4 | **RedlineAgent** | `agents/redline_agent.py` | Safer clause rewrites — **MEDIUM/HIGH/CRITICAL only** |
| 5 | **ComplianceAgent** | `agents/compliance_agent.py` | Checks against IT Act 2000, DPDP Act 2023, GDPR |
| 6 | **VerdictAgent** | `agents/verdict_agent.py` | Aggregates all outputs → risk score + verdict |

### Orchestration

`ContractAnalysisCrew` in `services/crew_orchestrator.py` calls each agent in
order and passes typed outputs forward.  No CrewAI runtime is used in the main
execution path; CrewAI is available for future parallel execution experiments.

### Shared Schema

All agents use the types defined in `models/schemas.py`:
- `RiskLevel` enum (CRITICAL / HIGH / MEDIUM / LOW / MINIMAL) – uppercase
- `VerdictClass` enum (DO_NOT_SIGN / SIGN_WITH_MODIFICATIONS / SAFE_TO_SIGN)
- `Clause`, `RiskFlag`, `ClauseExplanation`, `RedlineSuggestion`, `ComplianceIssue`, `Verdict`
- `AnalysisResponse` – top-level response shape returned by both routes

### AI Service

`services/ai_service.py` wraps the OpenAI SDK:
- Uses `OpenAI()` client pattern (SDK ≥ 1.x)
- `call_llm()` – text response with retries + timeout
- `call_llm_json()` – forces `response_format=json_object` with fallback parsing
- Model configurable via `OPENAI_MODEL` env var (default: `gpt-4o-mini`)

Deterministic agents do **not** call the LLM.  LLM calls are reserved for
future enhancement of ExplainerAgent, RedlineAgent, ComplianceAgent, and
VerdictAgent's executive summary.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/contracts/analyze` | Upload PDF, run full pipeline |
| POST | `/api/contracts/analyze-text` | Raw text analysis |
| GET  | `/api/contracts/health` | Agent availability check |
| POST | `/api/analyze/contract` | Text analysis (compat alias) |
| POST | `/api/upload/contract` | PDF upload only (no analysis) |
| GET  | `/health` | Server health |

## Data Flow

```
PDF upload
    │
    ▼
PDFParser.extract_text()     ← handles None pages, rejects image-only PDFs
    │
    ▼
TextCleaner.clean_contract_text()   ← fix soft hyphens, preserve section numbers
    │
    ▼
ParserAgent.parse_document()        ← regex section detection, clause typing
    │
    ├──▶ RiskDetectorAgent.detect_risks_batch()
    │
    ├──▶ ExplainerAgent.explain_clauses_batch()
    │
    ├──▶ RedlineAgent.suggest_redlines_batch()   ← MEDIUM/HIGH/CRITICAL clauses only
    │
    ├──▶ ComplianceAgent.check_compliance_batch()
    │
    └──▶ VerdictAgent.generate_verdict()
              │
              ▼
         AnalysisResponse (JSON)
```

## Response Schema

```json
{
  "status": "success",
  "summary": {
    "total_clauses": 7,
    "risk_distribution": {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 2, "LOW": 1, "MINIMAL": 1},
    "compliance_status": "NON-COMPLIANT",
    "high_risk_clause_ids": [1, 2, 3]
  },
  "parsed_clauses": [...],
  "risk_analysis": [...],
  "explanations": [...],
  "redlines": [...],
  "compliance_issues": [...],
  "verdict": {
    "risk_score": 7.4,
    "verdict": "SIGN_WITH_MODIFICATIONS",
    "recommendation": "...",
    "rationale": "...",
    "top_issues": [...],
    "negotiation_priorities": [...],
    "executive_summary": "..."
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | – | OpenAI API key (required for LLM features) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model for LLM-backed agents |

## Deployment

- **Docker Compose** – local development (`docker-compose.yml`)
- No database required for synchronous analysis
- Future: add analysis_id + Redis/Postgres for async job state

## Testing

```
python test_parser.py           # run all agent + pipeline tests
python test_parser.py --file path/to/contract.pdf
python test_parser.py --list    # list sample contracts
```

Test groups: parser · risk · explainer · redline · compliance · verdict · pipeline

