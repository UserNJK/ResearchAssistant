# ResearchAssistant Implementation Plan
## PHASE 0 & PHASE 1 Detailed File Specifications

**Locked Decisions:**
- Frontend: Next.js + TypeScript + Tailwind
- Supabase: Stub client connection only (no tables/migrations yet)
- LLM: OpenRouter with `mistralai/mistral-7b-instruct` (primary & fallback)
- Budget: Zero-cost, strict rate limiting
- Auth: Supabase Auth only (email-based, no verification, auto-create users, session/JWT)
  - **NO** NextAuth, SMTP, OTP, magic links, or OAuth
  - Controlled academic system (10-20 users)

---

## 🟦 PHASE 0: PROJECT BOOTSTRAP

### Task 0.1 – Verify/Create Repo Structure

**Files to Create:**

#### 1. `frontend/.gitkeep`
```
# Placeholder for frontend directory
```

#### 2. `backend/.gitkeep`
```
# Placeholder for backend directory
```

#### 3. `docs/.gitkeep`
```
# Placeholder for docs directory
```

#### 4. `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
backend/venv/
backend/.venv/
.venv/

# Environment variables
.env
.env.local
.env.*.local
backend/.env
frontend/.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
frontend/node_modules/
.next/
frontend/.next/
out/
frontend/out/
.turbo/

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
.coverage
.pytest_cache/
htmlcov/

# Supabase
.supabase/
```

---

### Task 0.2 – Environment Files

#### 5. `backend/.env.example`
```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Application Settings
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW_SECONDS=60
```

#### 6. `frontend/.env.local.example`
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration (client-side)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret_here

# Auth Providers
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

#### 7. `README.md`
```markdown
# ResearchAssistant

AI-powered research assistant that generates comprehensive research reports using multi-agent architecture.

## Quick Start

### Backend Setup (FastAPI)

1. Create virtual environment:
   \`\`\`bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Configure environment:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your actual keys
   \`\`\`

4. Run development server:
   \`\`\`bash
   uvicorn app.main:app --reload
   \`\`\`

5. Verify health check:
   \`\`\`bash
   curl http://localhost:8000/health
   \`\`\`

### Frontend Setup (Next.js)

1. Install dependencies:
   \`\`\`bash
   cd frontend
   npm install
   \`\`\`

2. Configure environment:
   \`\`\`bash
   cp .env.local.example .env.local
   # Edit .env.local with your actual keys
   \`\`\`

3. Run development server:
   \`\`\`bash
   npm run dev
   \`\`\`

4. Open browser: http://localhost:3000

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **LLM**: OpenRouter (mistralai/mistral-7b-instruct)
- **Auth**: NextAuth.js

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
- [ ] PHASE 2: OpenRouter LLM Layer
- [ ] PHASE 3: Agent Implementation
- [ ] PHASE 4: Orchestration Layer
- [ ] PHASE 5: API Endpoints
- [ ] PHASE 6-11: Frontend, Export, Security, Deployment

## License

MIT
```

---

## 🟦 PHASE 1: BACKEND FOUNDATION (FastAPI)

### Task 1.1 – FastAPI App Initialization

#### 8. `backend/requirements.txt`
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
supabase==2.3.0
httpx==0.26.0
python-multipart==0.0.6
```

#### 9. `backend/app/__init__.py`
```python
"""ResearchAssistant Backend Application"""
__version__ = "0.1.0"
```

#### 10. `backend/app/main.py`
```python
"""
FastAPI Application Entry Point
Provides health check and CORS configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI(
    title="ResearchAssistant API",
    description="AI-powered research assistant with multi-agent architecture",
    version="0.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    Returns API status and configuration info
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY)
    }


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ResearchAssistant API",
        "docs": "/docs",
        "health": "/health"
    }
```

---

### Task 1.2 – Configuration Management

#### 11. `backend/app/config.py`
```python
"""
Configuration Management
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Application Settings
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # LLM Models
    PLANNER_MODEL: str = "mistralai/mistral-7b-instruct"
    SUMMARY_MODEL: str = "mistralai/mistral-7b-instruct"
    INSIGHT_MODEL: str = "mistralai/mistral-7b-instruct"
    FORMATTER_MODEL: str = "mistralai/mistral-7b-instruct"
    DEFAULT_FALLBACK_MODEL: str = "mistralai/mistral-7b-instruct"
    
    # LLM Parameters
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_required_vars(self) -> None:
        """Validate that required environment variables are set"""
        errors = []
        
        if not self.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required")
        
        if not self.SUPABASE_URL:
            errors.append("SUPABASE_URL is required")
        
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            errors.append("SUPABASE_SERVICE_ROLE_KEY is required")
        
        if errors:
            raise ValueError(
                "Missing required environment variables:\n" + "\n".join(f"  - {e}" for e in errors)
            )


# Initialize settings
settings = Settings()

# Validate on startup (only in production)
if settings.ENVIRONMENT == "production":
    settings.validate_required_vars()
```

---

### Task 1.3 – Supabase Connection (Stub Implementation)

#### 12. `backend/app/db.py`
```python
"""
Supabase Database Connection and Helpers
Stub implementation for PHASE 1 - validates connection only
"""
from supabase import create_client, Client
from .config import settings
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class SupabaseDB:
    """Supabase database wrapper with helper methods"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Create Supabase client connection"""
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
                self.client = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not configured - running in stub mode")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if Supabase client is connected"""
        return self.client is not None
    
    # ===== STUB METHODS (will be implemented in later phases) =====
    
    async def create_research_job(
        self, 
        user_id: str, 
        topic: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new research job
        STUB: Returns mock data until tables are created
        """
        logger.info(f"[STUB] Creating research job for user {user_id}: {topic}")
        return {
            "id": "stub_job_123",
            "user_id": user_id,
            "status": "pending",
            "input": {"topic": topic, "metadata": metadata},
            "result": None,
            "created_at": "2026-01-18T00:00:00Z"
        }
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update research job status
        STUB: Returns mock confirmation
        """
        logger.info(f"[STUB] Updating job {job_id} to status: {status}")
        return {
            "id": job_id,
            "status": status,
            "result": result,
            "updated_at": "2026-01-18T00:00:00Z"
        }
    
    async def save_section(
        self, 
        job_id: str, 
        content: str, 
        index: int, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a research section
        STUB: Returns mock section data
        """
        logger.info(f"[STUB] Saving section {index} for job {job_id}")
        return {
            "id": f"stub_section_{index}",
            "job_id": job_id,
            "content": content,
            "index": index,
            "metadata": metadata
        }
    
    async def fetch_job_results(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch complete research job results
        STUB: Returns mock results
        """
        logger.info(f"[STUB] Fetching results for job {job_id}")
        return {
            "id": job_id,
            "status": "completed",
            "sections": [
                {"index": 0, "content": "Mock section 1"},
                {"index": 1, "content": "Mock section 2"}
            ],
            "metadata": {"generated_at": "2026-01-18T00:00:00Z"}
        }
    
    async def fetch_user_jobs(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch all jobs for a user
        STUB: Returns mock job list
        """
        logger.info(f"[STUB] Fetching jobs for user {user_id}")
        return [
            {
                "id": "stub_job_1",
                "user_id": user_id,
                "status": "completed",
                "created_at": "2026-01-18T00:00:00Z"
            }
        ]


# Global database instance
db = SupabaseDB()


def get_db() -> SupabaseDB:
    """Dependency injection for database instance"""
    return db
```

---

## Verification Commands

### Backend Verification (PHASE 1)

```bash
# 1. Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (copy from .env.example and add keys)
cp .env.example .env

# 4. Start FastAPI server
uvicorn app.main:app --reload

# 5. Test health endpoint
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "environment": "development",
#   "version": "0.1.0",
#   "openrouter_configured": true/false,
#   "supabase_configured": true/false
# }

# 6. Test Supabase connection (Python REPL)
python -c "from app.db import db; print('Connected:', db.is_connected())"
```

---

## Next Steps (After PHASE 1 Verification)

1. **PHASE 2**: Implement OpenRouter LLM wrapper (`backend/app/utils/openrouter.py`)
2. **PHASE 3**: Create agent implementations (planner, search, summarizer, insight, formatter)
3. **PHASE 4**: Build orchestrator to coordinate agents
4. **PHASE 5**: Add API endpoints for research operations

---

## Notes

- All Supabase database methods are **stubs** returning mock data
- No tables/migrations created yet - pure connection testing only
- Health check validates environment configuration
- OpenRouter integration comes in PHASE 2
- Frontend scaffolding deferred until backend is stable

## File Count Summary

**PHASE 0**: 7 files (structure + env + docs)
**PHASE 1**: 5 files (FastAPI core + Supabase stubs)
**Total**: 12 files

All files are minimal, testable, and follow incremental development principles.
