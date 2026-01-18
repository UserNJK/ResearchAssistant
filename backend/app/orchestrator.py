"""
PHASE 4-5: Orchestration Layer with Database Integration
Sequential research pipeline with job status tracking and Supabase persistence.

Pure orchestrator function that sequences agents:
  1. Plan research outline
  2. For each section: search, summarize, format
  3. Extract insights from all summaries
  4. Generate final formatted paper
  5. Persist results to Supabase (PHASE 5)
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from app.utils.openrouter import OpenRouterError
from app.agents.planner import plan_research
from app.agents.search_agent import search_for_section
from app.agents.summarizer import summarize_content
from app.agents.insight_agent import extract_insights
from app.agents.formatter import format_section, format_complete_paper
from app.db import db

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Research job lifecycle states."""
    PENDING = "pending"
    PLANNING = "planning"
    SEARCHING = "searching"
    SUMMARIZING = "summarizing"
    ANALYZING = "analyzing"
    FORMATTING = "formatting"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ResearchJob:
    """Represents a single research request and its current state."""
    job_id: str
    topic: str
    user_id: str  # PHASE 6: User scoping
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: Dict[str, Any] = field(default_factory=lambda: {
        "current_step": "not_started",
        "total_sections": 0,
        "completed_sections": 0,
        "current_section": None,
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "topic": self.topic,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
        }


# In-memory job cache (primary store for in-flight jobs, backed by Supabase)
_jobs: Dict[str, ResearchJob] = {}


async def create_job(topic: str, user_id: str) -> ResearchJob:
    """
    Create a new research job.
    
    PHASE 5: Persists to Supabase if available, falls back to in-memory.
    PHASE 6: User-scoped jobs - each job linked to user_id.
    """
    job_id = str(uuid.uuid4())
    job = ResearchJob(job_id=job_id, topic=topic, user_id=user_id)
    _jobs[job_id] = job
    
    # Persist to database
    await db.store_job(
        job_id=job_id,
        topic=topic,
        user_id=user_id,
        status=job.status.value,
        progress=job.progress
    )
    
    logger.info(f"Created job {job_id} for user {user_id}, topic: {topic}")
    return job


async def get_job(job_id: str) -> Optional[ResearchJob]:
    """
    Retrieve a job by ID.
    
    PHASE 5: Checks memory first, falls back to Supabase.
    """
    # Check in-memory cache first
    if job_id in _jobs:
        return _jobs[job_id]
    
    # Try database
    job_data = await db.retrieve_job(job_id)
    if job_data:
        logger.info(f"Retrieved job {job_id} from Supabase")
        # Reconstruct ResearchJob from database data
        try:
            job = ResearchJob(
                job_id=job_data.get("job_id", job_id),
                topic=job_data.get("topic", ""),
                status=JobStatus(job_data.get("status", "pending")),
                result=job_data.get("result"),
                error=job_data.get("error"),
                progress=job_data.get("progress", {})
            )
            _jobs[job_id] = job  # Cache it
            return job
        except Exception as e:
            logger.warning(f"Failed to reconstruct job {job_id}: {str(e)}")
            return None
    
    return None


async def list_jobs(user_id: Optional[str] = None, topic: Optional[str] = None) -> List[ResearchJob]:
    """
    List all jobs, optionally filtered by user and/or topic.
    
    PHASE 5: Combines in-memory and Supabase jobs.
    PHASE 6: Filter by user_id to enforce user scoping.
    """
    # Start with in-memory jobs
    jobs = list(_jobs.values())
    
    # Try to fetch from database (may include persisted jobs not in memory)
    try:
        db_jobs_data = await db.list_jobs(limit=100)
        for job_data in db_jobs_data:
            job_id = job_data.get("job_id")
            if job_id not in _jobs:  # Avoid duplicates
                try:
                    job = ResearchJob(
                        job_id=job_id,
                        topic=job_data.get("topic", ""),
                        user_id=job_data.get("user_id", ""),
                        status=JobStatus(job_data.get("status", "pending")),
                        result=job_data.get("result"),
                        error=job_data.get("error"),
                        progress=job_data.get("progress", {})
                    )
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"Failed to reconstruct job {job_id}: {str(e)}")
    except Exception as e:
        logger.debug(f"Could not fetch jobs from Supabase: {str(e)}")
    
    # Filter by user if specified (PHASE 6 - enforce user scoping)
    if user_id:
        jobs = [j for j in jobs if j.user_id == user_id]
    
    # Filter by topic if specified
    if topic:
        jobs = [j for j in jobs if j.topic.lower() == topic.lower()]
    
    return jobs


async def _update_job_status(job: ResearchJob, status: JobStatus, progress_update: Optional[Dict[str, Any]] = None) -> None:
    """
    Update job status and timestamp.
    
    PHASE 5: Persists to Supabase.
    """
    job.status = status
    job.updated_at = datetime.now()
    if progress_update:
        job.progress.update(progress_update)
    _jobs[job.job_id] = job
    
    # Persist to database
    try:
        await db.store_job(
            job_id=job.job_id,
            topic=job.topic,
            status=status.value,
            progress=job.progress,
            result=job.result,
            error=job.error
        )
    except Exception as e:
        logger.warning(f"Failed to persist job {job.job_id} to database: {str(e)}")
    
    logger.info(f"Job {job.job_id} status: {status.value}")


def _handle_job_error(job: ResearchJob, stage: str, error: Exception) -> None:
    """Handle error and update job state."""
    error_msg = f"Error during {stage}: {str(error)}"
    job.error = error_msg
    job.status = JobStatus.ERROR
    job.updated_at = datetime.now()
    _jobs[job.job_id] = job
    logger.error(f"Job {job.job_id} failed: {error_msg}")


async def orchestrate_research(topic: str, job_id: Optional[str] = None) -> ResearchJob:
    """
    Execute complete research pipeline for a topic.

    Pipeline:
      1. Create/retrieve job
      2. Plan research outline
      3. For each section: search → summarize → format
      4. Extract insights from summaries
      5. Generate final paper
      6. Update job with result

    Args:
        topic: Research topic
        job_id: Optional existing job ID (for resuming)

    Returns:
        ResearchJob with complete result or error

    Raises:
        ValueError: If topic is empty
        Exception: Caught and logged, job marked as ERROR
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")

    # Create or retrieve job
    if job_id:
        job = await get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
    else:
        job = await create_job(topic)

    try:
        # Stage 1: Planning
        logger.info(f"Job {job.job_id}: Starting research planning for '{topic}'")
        await _update_job_status(job, JobStatus.PLANNING, {"current_step": "planning"})

        sections = await plan_research(topic, max_sections=5)
        logger.info(f"Job {job.job_id}: Planned {len(sections)} sections")
        _update_job_status(
            job,
            JobStatus.PLANNING,
            {
                "current_step": "planning_complete",
                "total_sections": len(sections),
            }
        )

        # Stage 2: Search & Summarize & Format per section
        logger.info(f"Job {job.job_id}: Starting content retrieval for {len(sections)} sections")
        _update_job_status(job, JobStatus.SEARCHING)

        formatted_sections: Dict[str, str] = {}
        summaries: Dict[str, str] = {}

        for idx, section in enumerate(sections, 1):
            try:
                # Search
                logger.info(f"Job {job.job_id}: Searching for section {idx}/{len(sections)}: {section}")
                _update_job_status(
                    job,
                    JobStatus.SEARCHING,
                    {
                        "current_section": section,
                        "completed_sections": idx - 1,
                        "current_step": f"searching_{idx}",
                    }
                )
                content = await search_for_section(section, topic)

                # Summarize
                logger.info(f"Job {job.job_id}: Summarizing section {idx}: {section}")
                _update_job_status(
                    job,
                    JobStatus.SUMMARIZING,
                    {"current_step": f"summarizing_{idx}"}
                )
                summary = await summarize_content(content, section, max_length=300)
                summaries[section] = summary

                # Format
                logger.info(f"Job {job.job_id}: Formatting section {idx}: {section}")
                _update_job_status(
                    job,
                    JobStatus.FORMATTING,
                    {"current_step": f"formatting_{idx}"}
                )
                formatted = await format_section(section, summary, idx)
                formatted_sections[section] = formatted

                # Mark progress
                _update_job_status(
                    job,
                    JobStatus.FORMATTING,
                    {"completed_sections": idx}
                )

            except OpenRouterError as e:
                logger.warning(
                    f"Job {job.job_id}: LLM error on section {idx} ({section}), "
                    f"using fallback content: {str(e)}"
                )
                # Gracefully continue with fallback
                summary = f"[Content not available: {str(e)}]"
                summaries[section] = summary
                formatted = f"## {section}\n\n{summary}"
                formatted_sections[section] = formatted

            except Exception as e:
                logger.warning(
                    f"Job {job.job_id}: Unexpected error on section {idx} ({section}), "
                    f"continuing with next section: {str(e)}"
                )
                # Gracefully continue
                summaries[section] = f"[Section processing failed: {str(e)}]"
                formatted_sections[section] = f"## {section}\n\n[Processing failed]"

        if not summaries:
            raise RuntimeError("No sections could be processed")

        # Stage 3: Extract insights
        logger.info(f"Job {job.job_id}: Extracting insights from {len(summaries)} summaries")
        _update_job_status(job, JobStatus.ANALYZING, {"current_step": "analyzing"})

        try:
            insights = await extract_insights(summaries, topic)
        except OpenRouterError as e:
            logger.warning(f"Job {job.job_id}: Failed to extract insights: {str(e)}, using empty insights")
            insights = {
                "trends": [],
                "gaps": [],
                "conclusions": [],
                "key_concepts": [],
            }
        except Exception as e:
            logger.warning(f"Job {job.job_id}: Unexpected error extracting insights: {str(e)}")
            insights = {
                "trends": [],
                "gaps": [],
                "conclusions": [],
                "key_concepts": [],
            }

        # Stage 4: Format complete paper
        logger.info(f"Job {job.job_id}: Generating final formatted paper")
        await _update_job_status(job, JobStatus.FORMATTING, {"current_step": "formatting_final_paper"})

        try:
            title = f"Research Report: {topic}"
            keywords = insights.get("key_concepts", [])[:5]
            final_paper = await format_complete_paper(title, formatted_sections, insights, keywords)
        except OpenRouterError as e:
            logger.warning(f"Job {job.job_id}: Failed to format final paper: {str(e)}, using raw sections")
            final_paper = "\n\n".join(formatted_sections.values())
        except Exception as e:
            logger.warning(f"Job {job.job_id}: Unexpected error formatting final paper: {str(e)}")
            final_paper = "\n\n".join(formatted_sections.values())

        # Success: Store result
        result = {
            "topic": topic,
            "sections": sections,
            "summaries": summaries,
            "insights": insights,
            "final_paper": final_paper,
        }
        job.result = result
        await _update_job_status(job, JobStatus.COMPLETE, {"current_step": "complete"})
        logger.info(f"Job {job.job_id}: Research complete")
        return job

    except ValueError as e:
        # Validation error
        _handle_job_error(job, "validation", e)
        raise

    except Exception as e:
        # Unexpected error - mark as failed but continue
        logger.error(f"Job {job.job_id}: Orchestration failed: {str(e)}", exc_info=True)
        _handle_job_error(job, "orchestration", e)
        return job


async def cancel_job(job_id: str) -> Optional[ResearchJob]:
    """Cancel a pending or in-progress job."""
    job = await get_job(job_id)
    if not job:
        return None

    if job.status in (JobStatus.COMPLETE, JobStatus.ERROR):
        logger.warning(f"Cannot cancel job {job_id} with status {job.status.value}")
        return job

    job.error = "Job cancelled by user"
    job.status = JobStatus.ERROR
    job.updated_at = datetime.now()
    _jobs[job_id] = job
    
    # Persist cancellation
    try:
        await db.store_job(
            job_id=job_id,
            topic=job.topic,
            status=job.status.value,
            error=job.error,
            progress=job.progress
        )
    except Exception as e:
        logger.warning(f"Failed to persist cancellation for job {job_id}: {str(e)}")
    
    logger.info(f"Job {job_id} cancelled")
    return job


def clear_all_jobs() -> int:
    """Clear all jobs from memory (for testing)."""
    count = len(_jobs)
    _jobs.clear()
    logger.info(f"Cleared {count} jobs from memory")
    return count


def get_job_stats() -> Dict[str, Any]:
    """Get statistics about all jobs."""
    if not _jobs:
        return {
            "total_jobs": 0,
            "by_status": {},
            "total_completed": 0,
            "total_failed": 0,
        }

    by_status = {}
    for job in _jobs.values():
        status = job.status.value
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "total_jobs": len(_jobs),
        "by_status": by_status,
        "total_completed": by_status.get("complete", 0),
        "total_failed": by_status.get("error", 0),
    }
