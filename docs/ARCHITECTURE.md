# LegalSwarm Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                     │
│            React + Tailwind + TypeScript                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │          API Routes (upload, analyze)            │  │
│  └──────────────────┬───────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │         Services Layer                           │  │
│  │  - PDF Parser  - AI Service - Agent Service     │  │
│  └──────────────────┬───────────────────────────────┘  │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │      AI Agent Swarm (LangChain)                  │  │
│  │  ┌─────────────────────────────────────────┐   │  │
│  │  │  Risk | Compliance | Explainer | etc   │   │  │
│  │  └─────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼──┐    ┌────▼──┐   ┌───▼────┐
   │ OpenAI│    │PostgreSQL │  │ Redis │
   │ GPT-4 │    │(DB)      │  │(Cache)│
   └───────┘    └──────────┘  └───────┘
```

## Component Breakdown

### Frontend
- **Next.js 14**: React framework with server-side rendering
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Query**: Server state management
- **Axios**: HTTP client

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **PyPDF2**: PDF parsing and extraction
- **LangChain**: Agent orchestration framework
- **OpenAI API**: GPT-4 for intelligent analysis

### Database
- **PostgreSQL**: Persistent data storage
- **Redis**: Caching and session management

## Data Flow

1. **Upload**: User uploads PDF contract
2. **Parse**: PDF is extracted and chunked
3. **Analyze**: AI agents process the contract
4. **Report**: Results compiled and displayed

## Deployment

- **Docker Compose**: Local development
- **Docker**: Individual container deployment
- **Cloud**: AWS/GCP/Azure for production
