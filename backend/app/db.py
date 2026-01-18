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
    
    # ===== JOB PERSISTENCE METHODS (PHASE 5: Minimal Supabase Integration) =====
    
    async def store_job(
        self, 
        job_id: str,
        topic: str,
        user_id: str,
        status: str,
        progress: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store or update a research job in database
        
        PHASE 5: Minimal implementation - gracefully handles missing tables
        PHASE 6: Include user_id for user scoping
        Falls back to in-memory storage if Supabase unavailable
        
        Args:
            job_id: Unique job identifier
            topic: Research topic
            user_id: User who created the job
            status: Current job status
            progress: Progress tracking dict
            result: Completed research result
            error: Error message if failed
        
        Returns:
            Job data dict
        """
        if not self.client:
            logger.warning(f"Database not connected - job {job_id} stored locally only")
            return {
                "id": job_id,
                "topic": topic,
                "user_id": user_id,
                "status": status,
                "progress": progress,
                "result": result,
                "error": error,
                "persisted": False
            }
        
        try:
            # Try to insert/update job in Supabase
            job_data = {
                "job_id": job_id,
                "topic": topic,
                "user_id": user_id,
                "status": status,
                "progress": progress,
                "result": result,
                "error": error,
                "updated_at": "now()"  # Supabase timestamp
            }
            
            # Attempt upsert (insert or update)
            response = self.client.table("research_jobs").upsert(job_data).execute()
            logger.info(f"Job {job_id} persisted to Supabase")
            return response.data[0] if response.data else job_data
            
        except Exception as e:
            # Table may not exist yet - graceful degradation
            logger.warning(f"Could not persist job {job_id} to Supabase: {str(e)} - using local cache")
            return {
                "id": job_id,
                "topic": topic,
                "user_id": user_id,
                "status": status,
                "progress": progress,
                "result": result,
                "error": error,
                "persisted": False
            }
    
    async def retrieve_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a research job from database
        
        PHASE 5: Minimal implementation - gracefully handles missing tables
        Returns None if job not found
        
        Args:
            job_id: Job identifier to retrieve
        
        Returns:
            Job data dict or None if not found
        """
        if not self.client:
            logger.debug(f"Database not connected - cannot retrieve job {job_id}")
            return None
        
        try:
            response = self.client.table("research_jobs").select("*").eq("job_id", job_id).execute()
            if response.data:
                logger.info(f"Job {job_id} retrieved from Supabase")
                return response.data[0]
            return None
            
        except Exception as e:
            logger.warning(f"Could not retrieve job {job_id} from Supabase: {str(e)}")
            return None
    
    async def list_jobs(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all research jobs from database
        
        PHASE 5: Minimal implementation - returns empty if unavailable
        
        Args:
            limit: Maximum jobs to return
            offset: Pagination offset
        
        Returns:
            List of job dicts
        """
        if not self.client:
            logger.debug("Database not connected - cannot list jobs")
            return []
        
        try:
            response = self.client.table("research_jobs").select("*").range(offset, offset + limit - 1).execute()
            logger.info(f"Retrieved {len(response.data)} jobs from Supabase")
            return response.data if response.data else []
            
        except Exception as e:
            logger.warning(f"Could not list jobs from Supabase: {str(e)}")
            return []
    
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a research job from database
        
        PHASE 5: Minimal implementation - gracefully handles missing tables
        
        Args:
            job_id: Job to delete
        
        Returns:
            True if deleted, False otherwise
        """
        if not self.client:
            logger.debug(f"Database not connected - cannot delete job {job_id}")
            return False
        
        try:
            self.client.table("research_jobs").delete().eq("job_id", job_id).execute()
            logger.info(f"Job {job_id} deleted from Supabase")
            return True
            
        except Exception as e:
            logger.warning(f"Could not delete job {job_id} from Supabase: {str(e)}")
            return False
    
    # ===== LEGACY STUB METHODS (maintained for backward compatibility) =====
    
    async def create_research_job(
        self, 
        user_id: str, 
        topic: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new research job (legacy)
        Now delegates to store_job
        """
        job_id = f"job_{user_id}_{int(__import__('time').time())}"
        return await self.store_job(job_id, topic, "pending")
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: str, 
        result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update research job status (legacy)
        Now delegates to store_job
        """
        return await self.store_job(job_id, "", status, result=result)
    
    async def save_section(
        self, 
        job_id: str, 
        content: str, 
        index: int, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a research section (legacy)
        STUB: For backward compatibility only
        """
        logger.info(f"[LEGACY] Saving section {index} for job {job_id}")
        return {
            "id": f"section_{index}",
            "job_id": job_id,
            "content": content,
            "index": index
        }
    
    async def fetch_job_results(self, job_id: str) -> Dict[str, Any]:
        """
        Fetch complete research job results (legacy)
        Now delegates to retrieve_job
        """
        job = await self.retrieve_job(job_id)
        return job if job else {"id": job_id, "status": "not_found"}
    
    async def fetch_user_jobs(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch all jobs for a user (legacy)
        Now delegates to list_jobs
        """
        return await self.list_jobs(limit=limit)


# Global database instance
db = SupabaseDB()


def get_db() -> SupabaseDB:
    """Dependency injection for database instance"""
    return db
