# PHASE 6 Deployment Guide - Vercel + Supabase

## Status: Ready to Deploy

All PHASE 6 backend code is production-ready. This guide walks you through deploying to Vercel.

---

## Prerequisites

- [x] GitHub account with ResearchAssistant repository
- [x] Vercel account (free tier available)
- [x] Supabase account (free tier available)
- [x] OpenRouter account with API key

---

## Step 1: Prepare Supabase

### 1.1 Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Click "New Project"
3. Select your organization and region
4. Set a strong database password
5. Wait for project to initialize (2-3 minutes)

### 1.2 Get Credentials

In Supabase Dashboard:
- **Settings → API** → Copy `Project URL` (SUPABASE_URL)
- **Settings → API** → Copy `service_role` key (SUPABASE_SERVICE_ROLE_KEY)

⚠️ Keep service_role key SECRET - never commit to git

### 1.3 Create Database Table

In Supabase SQL Editor, run:

```sql
CREATE TABLE research_jobs (
  job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  progress JSONB DEFAULT '{}'::jsonb,
  result JSONB DEFAULT NULL,
  error TEXT DEFAULT NULL,
  user_id TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_research_jobs_user_id ON research_jobs(user_id);
CREATE INDEX idx_research_jobs_status ON research_jobs(status);

ALTER TABLE research_jobs ENABLE ROW LEVEL SECURITY;
```

✅ Row Level Security is OFF at API layer (enforced via code)

---

## Step 2: Get API Keys

### 2.1 OpenRouter API Key

1. Go to [https://openrouter.ai](https://openrouter.ai)
2. Sign up or log in
3. **Settings** → Copy API key
4. Set a monthly credit limit to avoid surprises

**Why OpenRouter?** Free-tier friendly LLM routing (supports Mistral 7B free)

### 2.2 Optional: Stripe Key (for future Phase 7)

Not needed for PHASE 6 - skip for now

---

## Step 3: Deploy to Vercel

### 3.1 Connect Repository

1. Go to [https://vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository (ResearchAssistant)
4. Select `backend` as Root Directory
5. Click "Continue"

### 3.2 Configure Environment Variables

Under **Environment Variables**, add:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
OPENROUTER_API_KEY=sk-or-v1-...
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=86400
USER_RATE_LIMIT_REQUESTS=100
USER_RATE_LIMIT_WINDOW_SECONDS=3600
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVIRONMENT=production
```

- Scope: All
- Environments: Production, Preview, Development

### 3.3 Deploy

Click **Deploy** and wait for build to complete

**Expected time:** 2-3 minutes

**Success indicator:** Green checkmark + URL (e.g., `https://yourdomain.vercel.app`)

---

## Step 4: Post-Deployment Verification

### 4.1 Health Check

```bash
curl https://yourdeployment.vercel.app/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "0.2.0",
  "auth_enabled": true
}
```

### 4.2 Test Authentication (Signup)

```bash
curl -X POST https://yourdeployment.vercel.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "abc123...",
    "email": "test@example.com",
    "verified": false
  }
}
```

✅ **Save the access_token** for next test

### 4.3 Create Research Job

```bash
curl -X POST https://yourdeployment.vercel.app/api/research \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"AI in healthcare"}'
```

**Expected Response (200 OK):**
```json
{
  "job_id": "abc-123-xyz",
  "topic": "AI in healthcare",
  "status": "planning",
  "progress": 0,
  "user_id": "abc123..."
}
```

### 4.4 List Jobs

```bash
curl https://yourdeployment.vercel.app/api/research \
  -H "Authorization: Bearer <access_token>"
```

**Expected Response (200 OK):**
```json
[
  {
    "job_id": "abc-123-xyz",
    "topic": "AI in healthcare",
    "status": "planning",
    "progress": 0
  }
]
```

### 4.5 Test Rate Limiting (429 Response)

Create 101 jobs rapidly to trigger rate limit:

```bash
for i in {1..101}; do
  curl -X POST https://yourdeployment.vercel.app/api/research \
    -H "Authorization: Bearer <access_token>" \
    -H "Content-Type: application/json" \
    -d "{\"topic\":\"Test $i\"}" \
    -s -o /dev/null -w "%{http_code}\n"
done
```

**Expected:** First 100 return 200, requests 101+ return 429

### 4.6 Test User Isolation (403 Forbidden)

Create job with User A, try to access with User B:

```bash
# User A: Create job and save job_id
JOB_ID=$(curl -s -X POST https://yourdeployment.vercel.app/api/research \
  -H "Authorization: Bearer <token_a>" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Secret"}' | jq -r .job_id)

# User B: Try to access User A's job
curl https://yourdeployment.vercel.app/api/research/$JOB_ID \
  -H "Authorization: Bearer <token_b>"
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "Not authorized to access this job"
}
```

---

## Step 5: Production Safety Checklist

Run this before declaring deployment successful:

- [ ] Health check returns 200 OK
- [ ] Signup returns JWT token
- [ ] Create research job returns 200 OK
- [ ] List jobs shows only user's jobs
- [ ] 429 rate limit error after 100 requests
- [ ] 403 error when accessing other user's job
- [ ] 401 error without Bearer token
- [ ] CORS works from frontend origin
- [ ] Supabase database shows created records
- [ ] No 500 errors in Vercel logs

**To view Vercel logs:**
1. Vercel Dashboard → Project → Deployments
2. Click current deployment
3. View "Function Logs"

---

## Troubleshooting

### Issue: "Invalid Supabase credentials"

**Solution:**
1. Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in Vercel
2. Check credentials match Supabase Settings → API
3. Redeploy after fixing environment variables

### Issue: "Rate limit exceeded" immediately

**Solution:**
1. Clear rate limit cache (in-memory, resets on server restart)
2. Redeploy project to reset memory
3. Wait 1 hour for automatic reset

### Issue: "CORS error from frontend"

**Solution:**
1. Update CORS_ORIGINS in Vercel environment variables
2. Include both http and https, with and without www
3. Redeploy project

Example:
```
https://yourdomain.com,https://www.yourdomain.com,http://localhost:3000
```

### Issue: "Auth token invalid"

**Solution:**
1. Token expires after 24 hours - re-login to get new token
2. Verify token format: `Authorization: Bearer <token>`
3. Check token not truncated in headers

### Issue: Research job stuck on "planning"

**Solution:**
1. This is normal - background task may be running
2. Check Vercel function logs for errors
3. Restart by re-creating the job

---

## What's Deployed

✅ **Authentication** (PHASE 6)
- Email-only signup/login
- JWT tokens (HS256, 24-hour expiration)
- Bearer token validation
- Per-user rate limiting (100 req/hour)

✅ **Research API** (PHASES 3-5)
- Multi-agent pipeline
- Background job orchestration
- Supabase persistence
- OpenRouter LLM integration

✅ **User Scoping**
- Jobs linked to user_id
- Ownership validation
- User-filtered listings

❌ **NOT Deployed**
- Frontend (separate deployment)
- PHASE 7 features (refresh tokens, OAuth, etc.)
- Admin dashboard
- Redis caching

---

## Environment Configuration Reference

| Variable | Value | Required |
|----------|-------|----------|
| SUPABASE_URL | https://xxx.supabase.co | ✅ Yes |
| SUPABASE_SERVICE_ROLE_KEY | eyJhbGc... | ✅ Yes |
| OPENROUTER_API_KEY | sk-or-v1-... | ✅ Yes |
| JWT_ALGORITHM | HS256 | ✅ Yes |
| JWT_EXPIRATION_SECONDS | 86400 | ✅ Yes |
| USER_RATE_LIMIT_REQUESTS | 100 | ✅ Yes |
| USER_RATE_LIMIT_WINDOW_SECONDS | 3600 | ✅ Yes |
| CORS_ORIGINS | https://yourdomain.com | ✅ Yes |
| ENVIRONMENT | production | ✅ Yes |

---

## Scaling Considerations for Future

**Current Setup** (PHASE 6):
- Vercel Serverless Functions (good for MVP)
- In-memory rate limiting (resets on restart)
- Single Supabase database
- Suitable for: <100 concurrent users

**For PHASE 7+** (if needed):
- Add Redis for distributed rate limiting
- Add job queue (Bull, Celery)
- Add CDN for assets
- Add custom domain with SSL
- Monitor usage and scale as needed

---

## API Endpoints Reference

All endpoints require authentication (except /health):

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/health` | GET | ❌ | Health check |
| `/api/auth/signup` | POST | ❌ | Email signup |
| `/api/auth/login` | POST | ❌ | Email login |
| `/api/auth/me` | GET | ✅ | Get profile |
| `/api/research` | POST | ✅ | Create job |
| `/api/research` | GET | ✅ | List jobs |
| `/api/research/{job_id}` | GET | ✅ | Get job status |
| `/api/research/{job_id}/cancel` | POST | ✅ | Cancel job |
| `/api/research/stats` | GET | ✅ | Get stats |

**Full documentation:** See PHASE_6_COMPLETE.md

---

## Next Steps

1. ✅ Deploy backend using this guide
2. Deploy frontend separately (when ready)
3. Configure custom domain (optional)
4. Monitor logs and metrics
5. Scale as needed

**STOP HERE** - Do not proceed to PHASE 7 yet.

---

## Support

For issues:
1. Check Vercel logs (Deployments → Function Logs)
2. Test endpoints locally: `cd backend && uvicorn app.main:app --reload`
3. Review PHASE_6_COMPLETE.md for architecture details
4. Check environment variables are set correctly

---

**Deployment Date:** [Your deployment date]
**Deployment URL:** https://your-vercel-url.app
**Status:** ✅ Production Ready
