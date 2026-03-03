# ResearchAssistant

AI-powered research assistant that generates comprehensive research reports using multi-agent architecture.

## Quick Start (Windows PowerShell)

### 1) One-time setup

#### Backend (FastAPI)

```powershell
cd D:\Projects\ResearchAssistant\backend
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create/update `backend/.env` with valid keys:

- `OPENROUTER_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001`

#### Frontend (Next.js)

```powershell
cd D:\Projects\ResearchAssistant\frontend
npm install
```

Create/update `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2) Run the project (every time)

Open **two terminals**.

#### Terminal 1: backend

```powershell
cd D:\Projects\ResearchAssistant\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Terminal 2: frontend

```powershell
cd D:\Projects\ResearchAssistant\frontend
npm run dev
```

### 3) Open in browser

- Frontend: `http://localhost:3000` (or `http://localhost:3001` if 3000 is already in use)
- Backend health: `http://127.0.0.1:8000/health`

## Troubleshooting

- **Auth says "Authentication failed" while backend is healthy**
  - Usually CORS mismatch when frontend runs on port 3001.
  - Ensure `CORS_ORIGINS` in `backend/.env` includes both `3000` and `3001` (see above), then restart backend.

- **`uvicorn` command fails or uses wrong Python**
  - Use the explicit interpreter command:
  - `.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

## Deploy on Vercel (Frontend)

This repository is best deployed as:

- **Frontend** on Vercel (Next.js)
- **Backend** on a persistent Python host (Render/Railway/Fly/Azure)

### Why this split?

The backend runs multi-step research orchestration and can exceed serverless limits. Vercel is ideal for the Next.js frontend, while a long-running backend host is more reliable for research jobs.

### Step-by-step

1. Push your repo to GitHub.
2. In Vercel, **New Project** → import this repo.
3. Set **Root Directory** to `frontend`.
4. Add frontend env var in Vercel:
  - `NEXT_PUBLIC_API_URL=https://<your-backend-domain>`
5. Deploy.

### Backend CORS for Vercel

Set these backend env vars on your backend host:

- `CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,https://<your-vercel-production-domain>`
- `CORS_ORIGIN_REGEX=https://.*\.vercel\.app`

`CORS_ORIGIN_REGEX` allows preview deployments (`*.vercel.app`) without editing env vars on every commit.

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **LLM**: OpenRouter (mistralai/mistral-7b-instruct)
- **Auth**: Supabase Auth (email-based, no verification, session/JWT)

## Architecture

Multi-agent system with specialized agents:
- Planner Agent: Generates research outline
- Search Agent: Fetches relevant information
- Summarization Agent: Condenses content
- Insight Agent: Extracts trends and conclusions
- Formatting Agent: Produces academic-quality output

## Development Status

- [x] PHASE 0: Project Bootstrap
- [x] PHASE 1: Backend Foundation
- [x] PHASE 2: OpenRouter LLM Layer
- [x] PHASE 3: Agent Implementation
- [x] PHASE 4: Orchestration Layer
- [x] PHASE 5: API Endpoints
- [ ] PHASE 6-11: Frontend, Export, Security, Deployment

## License

MIT
