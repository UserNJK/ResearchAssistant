# PHASE 4: Orchestration Layer - Complete

## ✅ Status: COMPLETE

**Date:** January 18, 2026  
**Scope:** Sequential research pipeline with job tracking and error handling

---

## Overview

PHASE 4 implements the **orchestrator module** that sequences all 5 agents from PHASE 3 into a complete research pipeline. The orchestrator manages job state, tracks progress, and handles errors gracefully.

**Key Responsibility:** Turn atomic agents into a cohesive research workflow.

---

## Core Components

### 1. Job Lifecycle Management

**JobStatus Enum:**
```python
PENDING → PLANNING → SEARCHING → SUMMARIZING → ANALYZING → FORMATTING → COMPLETE
                                                                  ↘ ERROR
```

**States:**
- `PENDING` - Job created, waiting to start
- `PLANNING` - Generating research outline
- `SEARCHING` - Retrieving content for sections
- `SUMMARIZING` - Condensing content
- `ANALYZING` - Extracting insights
- `FORMATTING` - Creating final output
- `COMPLETE` - Research finished successfully
- `ERROR` - Failed at any stage

### 2. ResearchJob Data Class

Represents a single research request with full state tracking:

```python
@dataclass
class ResearchJob:
    job_id: str                          # UUID
    topic: str                           # Research topic
    status: JobStatus = PENDING          # Current state
    created_at: datetime                 # Creation timestamp
    updated_at: datetime                 # Last update timestamp
    result: Optional[Dict] = None        # Final research result
    error: Optional[str] = None          # Error message if failed
    progress: Dict[str, Any] = {...}     # Detailed progress info
        - current_step: str
        - total_sections: int
        - completed_sections: int
        - current_section: str
```

### 3. Main Orchestrator Function

**Function:** `async orchestrate_research(topic: str, job_id: Optional[str] = None) -> ResearchJob`

**Pipeline:**
```
1. PLANNING STAGE
   └─ plan_research(topic) → [section titles]

2. CONTENT RETRIEVAL STAGE (per section)
   ├─ search_for_section(section, topic)
   ├─ summarize_content(raw_content, section)
   └─ format_section(section, summary, idx)

3. ANALYSIS STAGE
   └─ extract_insights(summaries, topic) → {trends, gaps, conclusions}

4. FINALIZATION STAGE
   └─ format_complete_paper(title, sections, insights) → final markdown
```

**Features:**
- Graceful error handling per section
- Continues with fallback content on LLM errors
- Tracks progress through all stages
- Returns job object with complete result or error details

**Usage:**
```python
# Start new research
job = await orchestrate_research("Artificial Intelligence")

# Or resume existing
job = await orchestrate_research("AI", job_id="existing-uuid")

# Result structure
{
    "topic": "AI",
    "sections": ["Introduction", "Key Concepts", ...],
    "summaries": {"Introduction": "...", ...},
    "insights": {
        "trends": ["AI mainstream adoption", ...],
        "gaps": ["Ethical guidelines unclear", ...],
        "conclusions": ["AI transforming industry", ...],
        "key_concepts": ["neural networks", ...]
    },
    "final_paper": "# Research Report: AI\n\n[complete formatted markdown]"
}
```

---

## Job Management Functions

### Job Creation & Retrieval

```python
# Create new job
job = create_job(topic: str) -> ResearchJob

# Get existing job
job = get_job(job_id: str) -> Optional[ResearchJob]

# List all jobs (with optional topic filter)
jobs = list_jobs(topic: Optional[str] = None) -> List[ResearchJob]

# Cancel a job
job = cancel_job(job_id: str) -> Optional[ResearchJob]

# Clear all jobs (testing only)
count = clear_all_jobs() -> int

# Get statistics
stats = get_job_stats() -> Dict[str, Any]
```

### Status Updates

Internal function `_update_job_status()` tracks progress:
- Updates job status
- Records timestamp
- Updates progress dictionary
- Stores in memory (stub)

---

## Error Handling Strategy

### Error Recovery Levels

**Level 1: Section Errors (Graceful)**
- Problem: LLM fails on individual section
- Response: Use fallback content, continue to next section
- Impact: Result includes "[Content not available]" placeholder
- Recovery: Automatic, no job failure

**Level 2: Insights Extraction (Recoverable)**
- Problem: LLM fails to extract insights
- Response: Return empty insights structure
- Impact: Insights arrays may be empty
- Recovery: Automatic, research completes with partial results

**Level 3: Final Formatting (Recoverable)**
- Problem: LLM fails to format final paper
- Response: Concatenate raw sections
- Impact: Paper lacks academic polish
- Recovery: Automatic, raw sections returned

**Level 4: Validation Errors (Fails Job)**
- Problem: Empty topic, invalid job ID
- Response: Raise ValueError immediately
- Impact: Job marked ERROR
- Recovery: Manual (user must create new job)

**Level 5: Unexpected Errors (Fails Job)**
- Problem: Unpredictable runtime exceptions
- Response: Log error, mark job as ERROR
- Impact: Job status = ERROR, error stored
- Recovery: Manual (investigate error, restart if needed)

### Error Handling Code

```python
# Per-section error handling
try:
    content = await search_for_section(section, topic)
    summary = await summarize_content(content, section)
    formatted = await format_section(section, summary, idx)
except OpenRouterError as e:
    # LLM failed - use placeholder
    summary = f"[Content not available: {str(e)}]"
    formatted = f"## {section}\n\n{summary}"
except Exception as e:
    # Unexpected error - log and continue
    logger.warning(f"Error on section {idx}: {str(e)}")
    formatted = f"## {section}\n\n[Processing failed]"
```

---

## In-Memory Job Storage

**Stub Implementation:**
```python
_jobs: Dict[str, ResearchJob] = {}  # Memory-resident job store
```

**Why Stub?**
- Sufficient for development
- Fast for testing
- No database overhead
- Production migration: Replace with Supabase queries

**Upgrade Path (PHASE 5+):**
```python
# Replace stubs with Supabase calls
async def create_job(topic: str) -> ResearchJob:
    # db.insert_job(job_id, topic, status=PENDING)
    # db.update_job_status(job_id, PLANNING)
    pass
```

---

## Progress Tracking

**Granular Progress Updates:**

```python
progress = {
    "current_step": "formatting_3",      # Which step
    "total_sections": 5,                 # Total work
    "completed_sections": 3,             # Progress
    "current_section": "Key Concepts",   # What section
}
```

**Stage Progression:**
```
planning → searching_1 → summarizing_1 → formatting_1
       → searching_2 → summarizing_2 → formatting_2
       → ...
       → analyzing
       → formatting_final_paper
       → complete
```

---

## Test Suite

**File:** `backend/test_orchestrator.py`

### Tests Included

1. **Basic Orchestration (TEST 1)**
   - Full pipeline execution
   - Validates all stages complete
   - Checks result structure

2. **Job Status Tracking (TEST 2)**
   - Job creation
   - Job retrieval
   - Status verification

3. **Multi-Job Orchestration (TEST 3)**
   - Concurrent job execution
   - Multiple topics simultaneously
   - Validates independence

4. **Job Listing & Statistics (TEST 4)**
   - List all jobs
   - Filter by topic
   - Statistics aggregation

5. **Job Cancellation (TEST 5)**
   - Cancel pending jobs
   - Verify error state
   - Status validation

6. **Error Handling (TEST 6)**
   - Invalid inputs
   - Exception recovery
   - Graceful failures

### Run Tests

```bash
cd backend
python test_orchestrator.py
```

**Expected Output:**
```
█ PHASE 4: ORCHESTRATOR TEST SUITE
█

TEST 1: Basic Research Orchestration
✅ Orchestration completed successfully
   Job ID: abc-123...
   Status: complete
   Sections planned: 5

[Additional test output...]

█ TEST SUMMARY
✅ PASS - Basic Orchestration
✅ PASS - Job Status Tracking
✅ PASS - Multi-Job Orchestration
✅ PASS - Job Listing & Stats
✅ PASS - Job Cancellation
✅ PASS - Error Handling

📊 Total: 6/6 tests passed

✅ ALL ORCHESTRATOR TESTS PASSED - PHASE 4 READY! 🎉
```

---

## Architecture

### Call Sequence Diagram

```
User Request (topic)
    ↓
create_job() → ResearchJob{status=PENDING}
    ↓
orchestrate_research()
    ├─ _update_job_status(PLANNING)
    ├─ plan_research() → sections[]
    │
    ├─ For each section:
    │  ├─ _update_job_status(SEARCHING)
    │  ├─ search_for_section() → content
    │  ├─ _update_job_status(SUMMARIZING)
    │  ├─ summarize_content() → summary
    │  ├─ _update_job_status(FORMATTING)
    │  ├─ format_section() → formatted
    │  └─ [Error handling: use fallback content]
    │
    ├─ _update_job_status(ANALYZING)
    ├─ extract_insights() → insights
    │
    ├─ _update_job_status(FORMATTING)
    ├─ format_complete_paper() → final_paper
    │
    ├─ job.result = {sections, summaries, insights, final_paper}
    ├─ _update_job_status(COMPLETE)
    └─ return job
```

### Data Flow

```
Topic Input
    ↓
Planner → Section Outline
    ↓
Search Agent → Raw Content (per section)
    ↓
Summarizer → Academic Summaries (per section)
    ↓
Formatter → Formatted Sections (per section)
    ↓
Insight Agent → Trends/Gaps/Conclusions
    ↓
Final Formatter → Complete Academic Paper
    ↓
Job Result
```

---

## Code Statistics

| File | Lines | Purpose |
|------|-------|---------|
| `app/orchestrator.py` | 450 | Core orchestration logic |
| `test_orchestrator.py` | 350 | Test suite (6 tests) |
| **Total** | **800** | **PHASE 4 implementation** |

---

## Key Features

✅ **Sequential Pipeline**
- Executes agents in order
- Passes data between stages
- No circular dependencies

✅ **Progress Tracking**
- Real-time status updates
- Granular step tracking
- Progress percentage possible

✅ **Error Resilience**
- Graceful fallback per section
- Continues on LLM failures
- Returns partial results

✅ **Job Management**
- Create, retrieve, list jobs
- Cancel pending jobs
- Statistics aggregation

✅ **Isolation**
- No API routes
- Pure orchestration logic
- Testable in isolation

---

## Constraints & Limitations

### Current (PHASE 4)
- ❌ No API routes (added in PHASE 5)
- ❌ No authentication (added in PHASE 5)
- ❌ No persistence (stubs only)
- ❌ No async cleanup/timeouts
- ❌ No concurrent job limits

### Future (PHASE 5+)
- ✅ API endpoints for job operations
- ✅ Database persistence
- ✅ Authentication checks
- ✅ Request timeouts
- ✅ Concurrent job throttling

---

## Integration Points

### Agents Used
- ✅ `plan_research()` from `agents/planner.py`
- ✅ `search_for_section()` from `agents/search_agent.py`
- ✅ `summarize_content()` from `agents/summarizer.py`
- ✅ `extract_insights()` from `agents/insight_agent.py`
- ✅ `format_section()` from `agents/formatter.py`
- ✅ `format_complete_paper()` from `agents/formatter.py`

### LLM Wrapper Used
- ✅ `call_llm()` from `utils/openrouter.py` (via agents)
- ✅ Error handling via `OpenRouterError`
- ✅ Caching and rate-limiting active

### Database Stubs
- ✅ Will integrate with `db.py` in PHASE 5
- ✅ No changes to Supabase client needed

---

## Usage Examples

### Basic Research

```python
from app.orchestrator import orchestrate_research

# Start research
job = await orchestrate_research("Quantum Computing")

# Wait for completion
while job.status != JobStatus.COMPLETE:
    print(f"Progress: {job.progress}")
    await asyncio.sleep(2)

# Access results
paper = job.result['final_paper']
insights = job.result['insights']
```

### Job Tracking

```python
from app.orchestrator import create_job, get_job, list_jobs

# Create job
job = create_job("Machine Learning")
job_id = job.job_id

# Later: Resume orchestration
job = await orchestrate_research("Machine Learning", job_id=job_id)

# List all jobs
all_jobs = list_jobs()
for job in all_jobs:
    print(f"{job.job_id}: {job.topic} - {job.status.value}")
```

### Error Scenarios

```python
# Handles gracefully:
job = await orchestrate_research("Complex Topic")
# Even if some sections fail, job continues with fallback content
# result = job.result (may have [Content not available] placeholders)

# Fails immediately:
try:
    await orchestrate_research("")  # Empty topic
except ValueError:
    print("Topic required")
```

---

## Compliance Checklist

✅ No API routes (pure orchestration)  
✅ Uses existing agents only  
✅ Sequential pipeline (no parallelization)  
✅ Job status tracking with stubs  
✅ Graceful error handling  
✅ Clear input/output contracts  
✅ Comprehensive logging  
✅ Full test coverage  

---

## Summary

**PHASE 4 delivers:**
- 450 LOC orchestrator module
- Job lifecycle management (8 states)
- Sequential agent orchestration
- Graceful error recovery
- Progress tracking
- 6 comprehensive tests
- Ready for PHASE 5 API integration

**Status:** ✅ **PHASE 4 COMPLETE**

Ready to proceed to PHASE 5: API Endpoints (when requested).

**Do NOT proceed beyond PHASE 4 per user instructions.**
