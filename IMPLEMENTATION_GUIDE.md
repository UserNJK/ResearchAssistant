# ResearchAssistant - Complete Implementation Guide

An AI-powered research paper generator with a 6-stage pipeline: **planner** → **search** → **summarizer** → **insight** → **formatter** → **PDF**. Emphasizes academic integrity with source-centric design, in-text citations, minimum section depth, and validation against generic filler text.

## Key Features
- **Source-Centric Pipeline**: Metadata preserved end-to-end from search through formatter.
- **LLM-First Search**: Uses budget-friendly LLM (Qwen 2.5 72B) for rich built-in knowledge; falls back to Wikipedia with metadata, then structured placeholders.
- **Academic Quality Enforcement**: Minimum 300 words per section, in-text citations `(Source, Year)`, references sourced from actual data.
- **PDF Generation**: Professional academic styling with proper structure, sections, and bibliography.

---

## Repository Structure
```
ResearchAssistant/
├─ backend/
│  ├─ app/
│  │  ├─ agents/
│  │  │  ├─ planner.py                    # Outline generation
│  │  │  ├─ search_agent.py              # LLM-first search (v2)
│  │  │  ├─ summarizer.py                # Content condensing
│  │  │  ├─ insight_agent.py             # Trends, gaps, conclusions
│  │  │  ├─ formatter.py                 # Academic formatting + citations
│  │  ├─ utils/
│  │  │  ├─ openrouter.py                # OpenRouter API client, caching, fallback
│  │  ├─ config.py                       # Pydantic settings + validation
│  │  ├─ main.py                         # FastAPI app setup
│  │  ├─ orchestrator.py                 # Job orchestration
│  │  ├─ __init__.py
│  │  ├─ __pycache__/
│  ├─ requirements.txt                   # Python dependencies
│  ├─ .env                              # **CREATE THIS** (see below)
│  ├─ .gitignore
├─ frontend/
│  ├─ src/...                           # React/Next.js app
│  ├─ package.json                      # npm dependencies
│  ├─ .env.local                        # **CREATE THIS** (see below)
│  ├─ .gitignore
├─ README.md                            # Main documentation
├─ IMPLEMENTATION_GUIDE.md              # This file
├─ .gitignore                           # Root-level ignore
```

---

## Prerequisites
- **OS**: Windows 10/11, macOS, or Linux
- **Python**: 3.10 or later
- **Node.js**: 16 or later (with npm)
- **OpenRouter API Key**: [Get a free key](https://openrouter.ai/settings/keys)
- **Supabase Account** (optional but recommended): [Sign up](https://supabase.com)

---

## Step-by-Step Installation

### Step 1: Clone Repository
```powershell
git clone https://github.com/YourUsername/ResearchAssistant.git
cd ResearchAssistant
```

### Step 2: Backend Setup

#### 2a) Create Virtual Environment
```powershell
cd backend

# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
# python -m venv .venv
# source .venv/bin/activate
```

#### 2b) Install Python Dependencies
```powershell
pip install -r requirements.txt
```
This installs: FastAPI, uvicorn, httpx, Pydantic, reportlab, python-dotenv, supabase-py, etc.

#### 2c) Create Backend Environment File
**Create a new file named `.env` in the `backend/` directory:**

**Windows (PowerShell):**
```powershell
echo "" | Out-File -Encoding utf8 .env
notepad .env
```

**macOS/Linux:**
```bash
touch .env
nano .env
```

**Copy and paste this template into `.env`:**
```env
# ============================================
# CORE APPLICATION
# ============================================
ENVIRONMENT=development
DEBUG=true

# CORS Origins - Update to your frontend URL
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ============================================
# OPENROUTER API (Required)
# ============================================
# Get free API key: https://openrouter.ai/settings/keys
OPENROUTER_API_KEY=sk-or-YOUR_KEY_HERE
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# ============================================
# SUPABASE (Recommended for Production)
# ============================================
# Create project: https://supabase.com
# Get keys from: Project Settings > API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# ============================================
# JWT & AUTHENTICATION
# ============================================
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=86400

# ============================================
# RATE LIMITING
# ============================================
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
USER_RATE_LIMIT_REQUESTS=100
USER_RATE_LIMIT_WINDOW_SECONDS=3600

# ============================================
# LLM MODELS (Budget-Friendly Defaults)
# ============================================
# Planner: Generates research outlines
PLANNER_MODEL=mistralai/mistral-7b-instruct

# Summarizer: Condenses content
SUMMARY_MODEL=meta-llama/llama-3.1-8b-instruct

# Insight: Extracts trends/gaps
INSIGHT_MODEL=meta-llama/llama-3.1-70b-instruct

# Formatter: Produces academic papers
FORMATTER_MODEL=meta-llama/llama-3.1-70b-instruct

# Fallback for search agent (LLM-first search)
# Options: qwen/qwen-2.5-72b-instruct, deepseek/deepseek-chat, mistralai/mistral-7b-instruct
DEFAULT_FALLBACK_MODEL=qwen/qwen-2.5-72b-instruct

# ============================================
# LLM GENERATION PARAMETERS
# ============================================
LLM_TEMPERATURE=0.4
LLM_MAX_TOKENS=2000
LLM_TIMEOUT_SECONDS=30
```

**Important**: Replace `sk-or-YOUR_KEY_HERE` with your actual OpenRouter API key.

### Step 3: Frontend Setup

#### 3a) Install Node Dependencies
```powershell
cd frontend
npm install
```

#### 3b) Create Frontend Environment File
**Create a new file named `.env.local` in the `frontend/` directory:**

**Windows (PowerShell):**
```powershell
echo "" | Out-File -Encoding utf8 .env.local
notepad .env.local
```

**macOS/Linux:**
```bash
touch .env.local
nano .env.local
```

**Copy and paste into `.env.local`:**

For **Vite-based React**:
```env
VITE_API_URL=http://localhost:8000
```

For **Next.js**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Application

### Option A: Two Terminal Windows (Recommended for Development)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\YourUsername\Desktop\ResearchAssistant\backend
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\YourUsername\Desktop\ResearchAssistant\frontend
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Option B: Background Process (Single Terminal)

```powershell
# Start backend in background
cd backend
.\.venv\Scripts\activate
Start-Process -NoNewWindow python -ArgumentList "-m uvicorn app.main:app --reload"

# Start frontend
cd frontend
npm run dev
```

---

## API Testing

### 1) Create a Research Job
```powershell
curl -X POST http://localhost:8000/api/research `
  -H "Content-Type: application/json" `
  -d '{"topic":"Edge Computing in Healthcare"}'
```

**Response:**
```json
{
  "job_id": "ea80740a-e493-48af-b917-2497505fb57c",
  "status": "processing",
  "topic": "Edge Computing in Healthcare"
}
```

### 2) Check Job Status (Poll until `status: "completed"`)
```powershell
curl http://localhost:8000/api/research/ea80740a-e493-48af-b917-2497505fb57c
```

**Response (when complete):**
```json
{
  "job_id": "ea80740a-e493-48af-b917-2497505fb57c",
  "status": "completed",
  "content": "# Edge Computing in Healthcare\n\n...",
  "sources": {
    "Introduction": {"source": "Qwen AI Research", "url": "..."}
  }
}
```

### 3) Download PDF
```powershell
curl -O http://localhost:8000/api/research/ea80740a-e493-48af-b917-2497505fb57c/pdf
```

The PDF will be saved to your current directory.

---

## Files Created & Their Purpose

### Backend Files

| File | Purpose |
|------|---------|
| `backend/.env` | **YOU CREATE THIS** - Secrets & config |
| `backend/app/main.py` | FastAPI app initialization, routes setup, CORS config |
| `backend/app/config.py` | Pydantic BaseSettings for loading & validating env vars |
| `backend/app/agents/planner.py` | Calls LLM to generate paper outline & section titles |
| `backend/app/agents/search_agent.py` | LLM-first search + Wikipedia fallback + structured placeholders |
| `backend/app/agents/summarizer.py` | Condenses raw search content while preserving specifics |
| `backend/app/agents/insight_agent.py` | Extracts trends, research gaps, conclusions |
| `backend/app/agents/formatter.py` | Enforces 300+ word minimum, in-text citations, academic quality |
| `backend/app/utils/openrouter.py` | OpenRouter API client with caching, retry logic, fallbacks |
| `backend/app/orchestrator.py` | Manages 6-stage pipeline, tracks sources through stages |
| `backend/requirements.txt` | Python package list |

### Frontend Files

| File | Purpose |
|------|---------|
| `frontend/.env.local` | **YOU CREATE THIS** - API URL config |
| `frontend/src/...` | React/Next.js components |
| `frontend/package.json` | npm package list |

### Environment Files You Must Create

1. **`backend/.env`** - Required secrets and configuration
2. **`frontend/.env.local`** - Required frontend configuration

---

## Environment Variables Explained

### `backend/.env`

| Variable | Required? | Example | Notes |
|----------|-----------|---------|-------|
| `OPENROUTER_API_KEY` | ✅ **YES** | `sk-or-abc123...` | Get from https://openrouter.ai/settings/keys |
| `ENVIRONMENT` | No | `development` | Set to `production` for deployment |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated URLs your frontend uses |
| `DEFAULT_FALLBACK_MODEL` | No | `qwen/qwen-2.5-72b-instruct` | Fallback LLM for search agent |
| `PLANNER_MODEL` | No | `mistralai/mistral-7b-instruct` | LLM for outline generation |
| `FORMATTER_MODEL` | No | `meta-llama/llama-3.1-70b-instruct` | LLM for academic formatting |
| `LLM_TEMPERATURE` | No | `0.4` | 0–1; lower = more factual, higher = more creative |
| `LLM_MAX_TOKENS` | No | `2000` | Max response length from LLM |
| `SUPABASE_URL` | No | `https://xxx.supabase.co` | Optional; for persistent job storage |
| `SUPABASE_SERVICE_ROLE_KEY` | No | `xxx-xxx-xxx` | Optional; Supabase admin key |

### `frontend/.env.local` (Vite)
```env
VITE_API_URL=http://localhost:8000
```

### `frontend/.env.local` (Next.js)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Architecture & Pipeline Flow

```
┌─────────────────────────────────────────────────────────┐
│ User submits topic: "Machine Learning in Healthcare"   │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [1] PLANNER AGENT                                        │
│ • Generates outline & section titles                     │
│ • Output: ["Introduction", "Background", ...]           │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [2] SEARCH AGENT (LLM-First)                             │
│ For each section:                                        │
│ • Try 1: Ask LLM to write detailed content              │
│ • Try 2: Search Wikipedia + extract metadata            │
│ • Try 3: Use structured placeholder templates           │
│ Output: {content, source, url, type, metadata}          │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [3] SUMMARIZER AGENT                                     │
│ • Condenses content while preserving specifics          │
│ • Keeps source metadata attached                        │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [4] INSIGHT AGENT                                        │
│ • Extracts trends, research gaps, conclusions           │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [5] FORMATTER AGENT                                      │
│ • Enforces academic quality:                            │
│   - Minimum 300 words per section                       │
│   - In-text citations: (Source, Year)                   │
│   - References only from sources (no hallucination)     │
│   - No generic language ("This section discusses...")   │
│ • Generates markdown paper with citations               │
└──────────────────────────┬──────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│ [6] PDF GENERATOR                                        │
│ • Converts markdown → PDF with academic styling         │
│ • Includes: Title, Abstract, Sections, References       │
└──────────────────────────┬──────────────────────────────┘
                           ↓
                    PDF Ready for Download
```

### Key: Source Metadata Preservation
```
Stage 2 (Search):     {content, source: "Wikipedia - Topic", url: "...", type: "encyclopedia"}
                                    ↓ passed through stages
Stage 5 (Formatter):  Uses source info for in-text citations & bibliography
                                    ↓
                      PDF references match content (no hallucinated refs)
```

---

## Troubleshooting

### **Error: "OPENROUTER_API_KEY not configured"**
**Solution:**
1. Verify `backend/.env` exists
2. Ensure the line `OPENROUTER_API_KEY=sk-or-...` is present
3. Get a key from [OpenRouter](https://openrouter.ai/settings/keys)
4. Restart the backend server

### **Error: "API call failed with status 503"**
**Solution:**
This is a transient provider outage. The system will retry automatically.
- If persistent, update `backend/.env`:
  ```env
  DEFAULT_FALLBACK_MODEL=deepseek/deepseek-chat
  ```

### **CORS Errors in Frontend Console**
**Solution:**
Update `CORS_ORIGINS` in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourdomain.com
```

### **"Cannot find module" errors**
**Solution:**
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### **Frontend can't reach backend**
**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `VITE_API_URL` or `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Check browser console for CORS/network errors

---

## Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `backend/.env`
- [ ] Generate strong `JWT_EXPIRATION_SECONDS` value
- [ ] Configure all Supabase credentials for persistent storage
- [ ] Set proper `CORS_ORIGINS` to your domain
- [ ] Use HTTPS with a reverse proxy (Nginx, Caddy)
- [ ] Deploy backend (Docker, Railway, Render, Heroku)
- [ ] Deploy frontend (Vercel, Netlify, GitHub Pages)
- [ ] Set up monitoring & logging
- [ ] Configure CI/CD pipelines

---

## Git Ignore Configuration

**Ensure `.gitignore` includes:**
```
*.env
backend/.env
frontend/.env.local
.venv/
node_modules/
__pycache__/
*.pyc
.DS_Store
```

**Never commit `.env` files to GitHub!**

---

## Quick Reference Commands

### Start Backend
```powershell
cd backend
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Start Frontend
```powershell
cd frontend
npm run dev
```

### Create Research Job
```powershell
curl -X POST http://localhost:8000/api/research -H "Content-Type: application/json" -d '{"topic":"Your Topic"}'
```

### Check Job Status
```powershell
curl http://localhost:8000/api/research/JOB_ID
```

### Download PDF
```powershell
curl -O http://localhost:8000/api/research/JOB_ID/pdf
```

---

## Support & Issues

- Open a GitHub issue for bugs
- Check the troubleshooting section above
- Review backend logs for detailed error messages
- Verify all `.env` variables are set correctly

---

**Happy researching!** 🚀
