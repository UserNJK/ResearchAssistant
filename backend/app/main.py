"""
FastAPI Application Entry Point
PHASE 5: Research API endpoints with background task orchestration
PHASE 6: Authentication, JWT validation, and per-user rate limiting
PHASE 8: Academic formatting and PDF export
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import io
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from .config import settings
from .orchestrator import (
    orchestrate_research,
    create_job,
    get_job,
    list_jobs,
    cancel_job,
    get_job_stats,
    ResearchJob,
    JobStatus
)
from .auth import init_auth_service, get_auth_service, AuthenticationError
from .middleware import init_auth_middleware, get_auth_middleware, clear_rate_limit_cache
from .db import db

app = FastAPI(
    title="ResearchAssistant API",
    description="AI-powered research assistant with multi-agent architecture",
    version="0.3.0"  # PHASE 8: Academic formatting and PDF export
)

logger = logging.getLogger(__name__)

# Initialize auth service and middleware
init_auth_service(db.client)
init_auth_middleware()

# CORS Configuration - enforce per origin
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=(settings.CORS_ORIGIN_REGEX or None),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Stricter methods
    allow_headers=["Authorization", "Content-Type"],  # Strict headers
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
        "version": "0.2.0",
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY),
        "auth_enabled": True  # PHASE 6
    }


@app.get("/test-llm")
async def test_llm_endpoint():
    """
    Test endpoint to verify OpenRouter LLM connection
    Requires OPENROUTER_API_KEY to be configured
    Uses caching to avoid repeated API calls
    """
    from .utils.openrouter import test_llm_connection
    
    result = await test_llm_connection()
    return result


@app.get("/llm-stats")
async def llm_cache_stats():
    """
    Get LLM cache and rate limiting statistics
    Useful for monitoring API usage
    """
    from .utils.openrouter import get_cache_stats
    
    stats = get_cache_stats()
    return {
        "cache": stats,
        "info": "Cache reduces duplicate API calls. Rate limiting prevents rapid requests."
    }


@app.post("/llm-cache/clear")
async def clear_llm_cache():
    """
    Clear the LLM response cache
    Use this if you want fresh responses
    """
    from .utils.openrouter import clear_cache
    
    cleared = clear_cache()
    return {
        "status": "success",
        "cleared_entries": cleared,
        "message": f"Cleared {cleared} cached responses"
    }


# ===== PHASE 6: AUTHENTICATION MODELS & DEPENDENCIES =====

class SignupRequest(BaseModel):
    """Request model for user signup"""
    email: EmailStr
    password: Optional[str] = None  # Not used, for compatibility


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: Optional[str] = None  # Not used, for compatibility


class AuthResponse(BaseModel):
    """Response model for auth endpoints"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfile(BaseModel):
    """Response model for user profile"""
    id: str
    email: str
    verified: bool = False


async def get_current_user(request: Request) -> dict:
    """
    Dependency injection for authenticated user.
    Extracts and validates JWT from Authorization header.
    
    Returns:
        User dict with id, email
    
    Raises:
        HTTPException: If not authenticated
    """
    middleware = get_auth_middleware()
    return await middleware.get_current_user(request)


# ===== PHASE 6: AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/signup", response_model=AuthResponse, tags=["Authentication"])
async def signup(request: SignupRequest):
    """
    Sign up a new user with email.
    
    PHASE 6: Password-less signup (no verification required).
    User account created immediately, JWT returned.
    
    Args:
        request: SignupRequest with email
    
    Returns:
        AuthResponse with access_token and user info
    
    Raises:
        400: If invalid email or signup fails
    """
    try:
        auth_service = get_auth_service()
        user_data = await auth_service.signup(request.email)
        
        # Login immediately after signup
        token_response = await auth_service.login(request.email)
        
        return AuthResponse(
            access_token=token_response["access_token"],
            token_type="bearer",
            user=token_response["user"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.post("/api/auth/login", response_model=AuthResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Login with email (password-less).
    
    PHASE 6: Email-only authentication. Returns JWT token.
    
    Args:
        request: LoginRequest with email
    
    Returns:
        AuthResponse with access_token
    
    Raises:
        401: If login fails
    """
    try:
        auth_service = get_auth_service()
        token_response = await auth_service.login(request.email)
        
        return AuthResponse(
            access_token=token_response["access_token"],
            token_type="bearer",
            user=token_response["user"]
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/api/auth/me", response_model=UserProfile, tags=["Authentication"])
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Args:
        current_user: Injected from Authorization header
    
    Returns:
        UserProfile with user info
    
    Raises:
        401: If not authenticated
    """
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        verified=current_user.get("verified", False)
    )


# ===== PHASE 5: RESEARCH API ENDPOINTS =====

class ResearchRequest(BaseModel):
    """Request model for starting a research job"""
    topic: str
    max_sections: Optional[int] = 5


class JobResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    topic: str
    status: str
    progress: dict
    result: Optional[dict] = None
    error: Optional[str] = None
    user_id: str  # PHASE 6


async def _run_research_job(job_id: str, topic: str) -> None:
    """
    Background task that runs the research orchestration
    Updates job status as it progresses
    """
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 BACKGROUND TASK STARTED for job {job_id}: {topic}")
    
    try:
        job = await get_job(job_id)
        if not job:
            logger.error(f"❌ Job {job_id} not found in get_job!")
            return
            
        logger.info(f"✅ Job {job_id} retrieved, starting orchestration...")
        await orchestrate_research(topic, job_id=job_id)
        logger.info(f"✅ Research complete for job {job_id}")
    except Exception as e:
        logger.error(f"❌ Background research job {job_id} failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")


@app.post("/api/research", response_model=JobResponse, tags=["Research"])
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a new research job.
    
    PHASE 6: Requires authentication. Jobs are user-scoped.
    The job runs asynchronously in the background.
    Use GET /api/research/{job_id} to check status.
    
    Args:
        request: ResearchRequest with topic and optional max_sections
        current_user: Injected from Authorization header
    
    Returns:
        JobResponse with job_id and initial status
    
    Raises:
        400: If topic empty or validation fails
        401: If not authenticated
        429: If rate limit exceeded
    """
    # Check rate limit
    middleware = get_auth_middleware()
    if not middleware.check_rate_limit(
        current_user["id"],
        settings.USER_RATE_LIMIT_REQUESTS,
        settings.USER_RATE_LIMIT_WINDOW_SECONDS
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {settings.USER_RATE_LIMIT_REQUESTS} requests per {settings.USER_RATE_LIMIT_WINDOW_SECONDS} seconds"
        )
    
    if not request.topic or not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    # Create job with user_id
    job = await create_job(request.topic, user_id=current_user["id"])
    
    # Queue background task
    background_tasks.add_task(_run_research_job, job.job_id, request.topic)
    
    return JobResponse(
        job_id=job.job_id,
        topic=job.topic,
        status=job.status.value,
        progress=job.progress,
        user_id=job.user_id
    )


@app.post("/api/research/start", response_model=JobResponse, tags=["Research"])
async def start_research_alias(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Alias for POST /api/research for backwards compatibility"""
    return await start_research(request, background_tasks, current_user)


@app.get("/api/research", tags=["Research"])
async def list_all_research(topic: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """
    List research jobs for the authenticated user.
    
    Args:
        topic: Optional filter by topic
        current_user: Authenticated user (from dependency)
    
    Returns:
        List of JobResponse objects owned by the user
    
    Raises:
        401: If not authenticated
    """
    # Filter jobs by user_id - only return user's own jobs
    jobs = await list_jobs(user_id=current_user["id"], topic=topic)
    return [
        JobResponse(
            job_id=j.job_id,
            topic=j.topic,
            status=j.status.value,
            progress=j.progress,
            result=j.result,
            error=j.error,
            user_id=j.user_id
        )
        for j in jobs
    ]


@app.get("/api/research/jobs", tags=["Research"])
async def list_all_research_alias(topic: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Alias for GET /api/research for backwards compatibility"""
    return await list_all_research(topic, current_user)


@app.get("/api/research/{job_id}", response_model=JobResponse, tags=["Research"])
async def get_research_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get the status and progress of a research job.
    
    Args:
        job_id: The job ID returned from POST /api/research
        current_user: Authenticated user (from dependency)
    
    Returns:
        JobResponse with current status and progress
    
    Raises:
        401: If not authenticated
        403: If user doesn't own the job
        404: If job not found
    """
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Enforce user scoping - only owner can view
    if job.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    return JobResponse(
        job_id=job.job_id,
        topic=job.topic,
        status=job.status.value,
        progress=job.progress,
        result=job.result,
        error=job.error,
        user_id=job.user_id
    )


@app.get("/api/research/{job_id}/pdf", tags=["Research"])
async def export_research_pdf(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Export research paper as PDF (PHASE 8).
    
    Args:
        job_id: The job ID to export
        current_user: Authenticated user (from dependency)
    
    Returns:
        PDF file download
    
    Raises:
        401: If not authenticated
        403: If user doesn't own the job
        404: If job not found or not complete
    """
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Enforce user scoping
    if job.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    if job.status != JobStatus.COMPLETE:
        raise HTTPException(status_code=400, detail="Job must be completed to export PDF")
    
    if not job.result or not job.result.get("final_paper"):
        raise HTTPException(status_code=404, detail="No paper content available")
    
    try:
        # Generate PDF using reportlab
        paper_content = job.result["final_paper"]
        pdf_buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Title page style
        title_page_style = ParagraphStyle(
            'TitlePage',
            parent=styles['Title'],
            fontSize=24,
            textColor='black',
            spaceAfter=60,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=28
        )
        author_style = ParagraphStyle(
            'Author',
            parent=styles['Normal'],
            fontSize=14,
            textColor='black',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Times-Roman'
        )
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='black',
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_LEFT,
            fontName='Times-Bold',
            leading=20
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='black',
            spaceAfter=12,
            spaceBefore=16,
            fontName='Times-Bold',
            leading=18
        )
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor='black',
            spaceAfter=10,
            spaceBefore=12,
            fontName='Times-Bold',
            leading=16
        )
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='black',
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            fontName='Times-Roman',
            leading=14
        )
        abstract_style = ParagraphStyle(
            'Abstract',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='black',
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leftIndent=30,
            rightIndent=30,
            fontName='Times-Italic',
            leading=14
        )
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='black',
            alignment=TA_LEFT,
            leftIndent=30,
            fontName='Times-Roman',
            leading=13,
            spaceAfter=6
        )
        reference_style = ParagraphStyle(
            'Reference',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='black',
            alignment=TA_LEFT,
            leftIndent=20,
            fontName='Times-Roman',
            leading=12,
            spaceAfter=8
        )
        
        # Parse markdown content into PDF elements
        story = []
        
        # Extract title from first # heading or use topic
        title_text = job.topic
        final_paper = paper_content
        for line in final_paper.split('\n'):
            if line.strip().startswith('# '):
                title_text = line.strip()[2:].strip()
                break
        
        # Add title page
        story.append(Spacer(1, 100))
        story.append(Paragraph(title_text, title_page_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph("ResearchAssistant AI", author_style))
        story.append(Paragraph("Independent Research", author_style))
        
        # Get current year for date
        from datetime import datetime
        year = datetime.now().year
        story.append(Paragraph(str(year), author_style))
        story.append(PageBreak())
        
        # Process remaining content
        lines = paper_content.split('\n')
        
        import re
        
        def clean_markdown(text):
            """Convert markdown formatting to reportlab XML tags"""
            # Escape XML special characters first
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            
            # Convert **bold** to <b>bold</b> (non-greedy)
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            
            # Convert *italic* to <i>italic</i> (non-greedy, avoid double-star matches)
            text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
            
            # Convert `code` to monospace
            text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
            
            # Convert [link](url) to just link text
            text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
            
            return text
        
        i = 0
        skip_first_title = True  # Skip the first # title since it's on title page
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Empty line
            if not line.strip():
                story.append(Spacer(1, 0.2*cm))
                i += 1
                continue
            
            # Horizontal rule
            if line.strip() in ['---', '***', '___']:
                story.append(Spacer(1, 0.3*cm))
                i += 1
                continue
            
            # Title (# )
            if line.startswith('# '):
                # Skip first title (it's on title page)
                if skip_first_title:
                    skip_first_title = False
                    i += 1
                    continue
                clean_text = clean_markdown(line[2:])
                story.append(Paragraph(clean_text, title_style))
                i += 1
                continue
            
            # Heading (## )
            if line.startswith('## '):
                # Check if it's "Abstract" or "Keywords" - use special formatting
                heading_text = line[3:].strip()
                if heading_text.lower() == 'abstract':
                    story.append(Paragraph('Abstract', heading_style))
                    # Treat next paragraph as abstract with special style
                    i += 1
                    # Skip empty lines
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    if i < len(lines):
                        abstract_text = clean_markdown(lines[i])
                        story.append(Paragraph(abstract_text, abstract_style))
                        i += 1
                    continue
                elif heading_text.lower().startswith('keyword'):
                    clean_text = clean_markdown(heading_text)
                    story.append(Paragraph(clean_text, heading_style))
                    i += 1
                    continue
                elif heading_text.lower().startswith('reference'):
                    # Special handling for references section
                    story.append(Paragraph('References', heading_style))
                    i += 1
                    # Process references with special formatting
                    while i < len(lines):
                        ref_line = lines[i].rstrip()
                        if ref_line.strip() and not ref_line.startswith('#'):
                            # Check if numbered list item
                            if re.match(r'^\s*\d+\.\s+', ref_line):
                                ref_text = re.sub(r'^\s*\d+\.\s+', '', ref_line)
                                clean_text = clean_markdown(ref_text)
                                story.append(Paragraph(clean_text, reference_style))
                            elif re.match(r'^\s*[-*+]\s+', ref_line):
                                ref_text = re.sub(r'^\s*[-*+]\s+', '', ref_line)
                                clean_text = clean_markdown(ref_text)
                                story.append(Paragraph(clean_text, reference_style))
                            elif ref_line.strip():
                                clean_text = clean_markdown(ref_line)
                                story.append(Paragraph(clean_text, reference_style))
                        i += 1
                    break  # Done processing references - end of document
                else:
                    clean_text = clean_markdown(heading_text)
                    story.append(Paragraph(clean_text, heading_style))
                i += 1
                continue
            
            # Subheading (### )
            if line.startswith('### '):
                clean_text = clean_markdown(line[4:])
                story.append(Paragraph(clean_text, subheading_style))
                i += 1
                continue
            
            # Bullet list item (-, *, +)
            if re.match(r'^\s*[-*+]\s+', line):
                bullet_text = re.sub(r'^\s*[-*+]\s+', '', line)
                clean_text = clean_markdown(bullet_text)
                story.append(Paragraph(f'• {clean_text}', bullet_style))
                i += 1
                continue
            
            # Numbered list item (1., 2., etc)
            if re.match(r'^\s*\d+\.\s+', line):
                num_text = re.sub(r'^\s*(\d+)\.\s+', r'\1. ', line)
                clean_text = clean_markdown(num_text)
                story.append(Paragraph(clean_text, bullet_style))
                i += 1
                continue
            
            # Block quote (>)
            if line.startswith('>'):
                quote_text = line.lstrip('>').strip()
                clean_text = clean_markdown(quote_text)
                quote_style = ParagraphStyle(
                    'Quote',
                    parent=body_style,
                    leftIndent=30,
                    fontName='Times-Italic',
                    textColor='#333333'
                )
                story.append(Paragraph(clean_text, quote_style))
                i += 1
                continue
            
            # Regular paragraph
            clean_text = clean_markdown(line)
            story.append(Paragraph(clean_text, body_style))
            i += 1
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Return PDF file
        filename = f"{job.topic.replace(' ', '_')[:50]}.pdf"
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF export failed for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/research/{job_id}/cancel", tags=["Research"])
async def cancel_research(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Cancel a pending or in-progress research job.
    
    Args:
        job_id: The job ID to cancel
        current_user: Authenticated user (from dependency)
    
    Returns:
        JobResponse with cancelled status
    
    Raises:
        401: If not authenticated
        403: If user doesn't own the job
        404: If job not found
        400: If job cannot be cancelled (already complete/error)
    """
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Enforce user scoping - only owner can cancel
    if job.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this job")
    
    if job.status not in (JobStatus.ERROR, JobStatus.PENDING, JobStatus.PLANNING):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status {job.status.value}"
        )
    
    return JobResponse(
        job_id=job.job_id,
        topic=job.topic,
        status=job.status.value,
        progress=job.progress,
        error=job.error,
        user_id=job.user_id
    )


@app.get("/api/research/stats", tags=["Research"])
async def get_research_stats(current_user: dict = Depends(get_current_user)):
    """
    Get statistics about research jobs for the authenticated user.
    
    Args:
        current_user: Authenticated user (from dependency)
    
    Returns:
        Statistics including total jobs, jobs by status, completed/failed counts for user's jobs
    
    Raises:
        401: If not authenticated
    """
    stats = get_job_stats()
    # Filter stats to only include user's jobs
    # This is a simplified approach - in production, you might want to track per-user stats separately
    return {
        "user_id": current_user["user_id"],
        "message": "Per-user job statistics endpoint - implement detailed stats storage in production",
        "stats": stats
    }


@app.get("/")

async def root():
    """Root endpoint with API information"""
    return {
        "message": "ResearchAssistant API",
        "docs": "/docs",
        "health": "/health"
    }
