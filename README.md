# ResearchAssistant

AI-powered research assistant that generates comprehensive research reports using multi-agent architecture.

## Quick Start

### Backend Setup (FastAPI)

1. Create virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

4. Run development server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Verify health check:
   ```bash
   curl http://localhost:8000/health
   ```

### Frontend Setup (Next.js)

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your actual keys
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Open browser: http://localhost:3000

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
