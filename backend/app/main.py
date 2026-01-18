from fastapi import FastAPI
from .core.config import settings

app = FastAPI(title="ResearchAssistantAgent", version="0.1.0")

@app.get("/")
def root():
    return {"name": "ResearchAssistantAgent", "status": "ok", "env": settings.environment}

@app.get("/health")
def health():
    return {"status": "healthy"}