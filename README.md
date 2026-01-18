# ResearchAssistantAgent

An AI-powered Research Assistant built with agentic AI. The system searches the web, reads papers, and writes research reports.

## Monorepo Structure
- `backend/` — Python FastAPI service for search, paper ingestion, and report generation
- `frontend/` — Next.js (React) + TypeScript + Tailwind UI

## Quickstart
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
Create `backend/.env`:
```
OPENAI_API_KEY=your_key
SERP_API_KEY=your_key
```

## Roadmap
- [ ] Web search integration
- [ ] Paper parsing (PDF/HTML)
- [ ] Summarization + report generation
- [ ] Citations + export

---
Built for free, open access research.