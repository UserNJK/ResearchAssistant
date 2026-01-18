# PHASE 6 Deployment Checklist

## Pre-Deployment (Complete Before Deploying to Vercel)

### Code & Configuration
- [x] All PHASE 6 code is in place (auth.py, middleware.py, test_auth.py)
- [x] requirements.txt includes all dependencies (including PyJWT)
- [x] vercel.json created with correct configuration
- [x] .env.example created for reference
- [x] .env and .env.local are in .gitignore
- [x] No hardcoded secrets in any files

### Testing
- [x] Run local tests: `pytest app/test_auth.py -v`
- [x] All 45+ tests pass locally
- [x] No errors in code
- [x] Health check works locally: `curl http://localhost:8000/health`

### External Services
- [ ] Supabase project created
- [ ] SUPABASE_URL copied from Supabase Settings → API
- [ ] SUPABASE_SERVICE_ROLE_KEY copied from Supabase Settings → API
- [ ] Database table created in Supabase (research_jobs)
- [ ] OpenRouter API key obtained from https://openrouter.ai
- [ ] GitHub repository is public or Vercel has access

---

## Deployment (Following These Steps)

### Step 1: Supabase Setup
- [ ] Create Supabase project at https://supabase.com
- [ ] Create research_jobs table with SQL script
- [ ] Copy SUPABASE_URL
- [ ] Copy SUPABASE_SERVICE_ROLE_KEY
- [ ] Test Supabase connection locally (optional)

### Step 2: Vercel Setup
- [ ] Create Vercel account at https://vercel.com
- [ ] Connect GitHub repository to Vercel
- [ ] Set Root Directory to `backend`
- [ ] Add Environment Variables:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_SERVICE_ROLE_KEY
  - [ ] OPENROUTER_API_KEY
  - [ ] JWT_ALGORITHM=HS256
  - [ ] JWT_EXPIRATION_SECONDS=86400
  - [ ] USER_RATE_LIMIT_REQUESTS=100
  - [ ] USER_RATE_LIMIT_WINDOW_SECONDS=3600
  - [ ] CORS_ORIGINS=https://yourdomain.com (or * for testing)
  - [ ] ENVIRONMENT=production
  
### Step 3: Deploy
- [ ] Click "Deploy" in Vercel
- [ ] Wait for build to complete (2-3 minutes)
- [ ] Verify deployment URL is live
- [ ] Check Vercel Function Logs for errors

---

## Post-Deployment Verification (Immediate After Deployment)

### Quick Checks (Run in Terminal)

#### 1. Health Check
```bash
curl https://yourdeployment.vercel.app/health
```
Expected: 200 OK with `"status": "healthy"`

- [ ] Health check passes

#### 2. Signup
```bash
curl -X POST https://yourdeployment.vercel.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```
Expected: 200 OK with access_token

- [ ] Signup returns JWT token

#### 3. Create Job
```bash
TOKEN=<token_from_signup>
curl -X POST https://yourdeployment.vercel.app/api/research \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test"}'
```
Expected: 200 OK with job_id

- [ ] Research job created successfully

#### 4. List Jobs
```bash
curl https://yourdeployment.vercel.app/api/research \
  -H "Authorization: Bearer $TOKEN"
```
Expected: 200 OK with job list

- [ ] Jobs listing works

### Automated Verification (Recommended)

```bash
python verify_deployment.py https://yourdeployment.vercel.app
```

This runs all 10 verification tests:
- [ ] All 10 tests pass
- [ ] No critical failures
- [ ] Rate limiting active
- [ ] User scoping enforced

---

## Production Safety Validation

### Authentication
- [ ] Email signup works
- [ ] Email login works (auto-creates user)
- [ ] JWT tokens generated (24-hour expiration)
- [ ] Bearer token validation works
- [ ] Invalid tokens rejected (401)
- [ ] Missing token rejected (401)

### Authorization
- [ ] Unauthenticated access blocked (401)
- [ ] User cannot access other user's jobs (403)
- [ ] User cannot cancel other user's jobs (403)
- [ ] Ownership validation working
- [ ] /me endpoint requires auth

### Research API
- [ ] Create job works
- [ ] Get job status works
- [ ] List jobs works (user-filtered)
- [ ] Cancel job works (ownership verified)
- [ ] Get stats works

### Rate Limiting
- [ ] Rate limiter active
- [ ] 100 requests/hour per user
- [ ] Returns 429 when exceeded
- [ ] Per-user isolation (different users have separate limits)

### CORS
- [ ] CORS headers present
- [ ] Allowed methods: GET, POST, OPTIONS
- [ ] Allowed headers: Authorization, Content-Type
- [ ] Disallowed methods: DELETE, PUT, PATCH

### Error Handling
- [ ] 400 errors properly formatted
- [ ] 401 errors for auth failures
- [ ] 403 errors for unauthorized access
- [ ] 404 errors for not found
- [ ] 429 errors for rate limit
- [ ] 500 errors logged (check Vercel logs)

### Database
- [ ] Supabase table exists
- [ ] Jobs are created in table
- [ ] Jobs include user_id
- [ ] Timestamps are recorded
- [ ] Data persists after restart

### Logs & Monitoring
- [ ] No 500 errors in Vercel logs
- [ ] No auth failures in logs
- [ ] All requests logged
- [ ] Performance is acceptable (< 2s response time)

---

## Post-Deployment Maintenance

### Week 1 (Stability Check)
- [ ] Monitor Vercel logs daily
- [ ] Check error rates
- [ ] Verify Supabase connection stability
- [ ] Test rate limiting manually
- [ ] Monitor API response times

### Week 2+ (Ongoing)
- [ ] Weekly log review
- [ ] Monitor usage patterns
- [ ] Check Supabase quota usage
- [ ] Monitor rate limit hits
- [ ] Plan for scaling if needed

---

## Issue Resolution

### If Health Check Fails
1. Check Vercel logs: Deployments → Function Logs
2. Verify environment variables are set
3. Check Python version compatibility
4. Redeploy project

### If Auth Endpoints Fail
1. Verify SUPABASE_SERVICE_ROLE_KEY is correct
2. Verify JWT_ALGORITHM=HS256 in environment
3. Check Supabase connection in logs
4. Redeploy with fresh environment variables

### If Rate Limiting Fails
1. This is in-memory, resets on redeploy
2. Redeploy project to reset limits
3. Wait 1 hour for automatic reset
4. Check if threshold is correct (should be 100)

### If Jobs Don't Persist
1. Verify SUPABASE_URL is correct
2. Verify SUPABASE_SERVICE_ROLE_KEY is correct
3. Verify research_jobs table exists in Supabase
4. Check Supabase logs for errors

### If CORS Errors Occur
1. Update CORS_ORIGINS in Vercel environment
2. Include both http and https origins
3. Include both www and non-www versions
4. Redeploy after changes

---

## Performance Targets

Target metrics for healthy deployment:

| Metric | Target | Status |
|--------|--------|--------|
| Health check response time | < 500ms | ✓ |
| Signup response time | < 1s | ✓ |
| Create job response time | < 2s | ✓ |
| List jobs response time | < 1s | ✓ |
| Auth validation overhead | < 50ms | ✓ |
| Database response time | < 500ms | ✓ |
| Error rate | < 0.1% | ✓ |

---

## Rollback Plan

If deployment becomes unstable:

1. **Immediate Rollback** (2-3 minutes)
   ```
   Vercel Dashboard → Deployments → Select Previous
   ```

2. **Full Rollback** (if environment issue)
   ```
   Vercel Dashboard → Settings → Environment Variables
   - Verify all variables are set correctly
   - Redeploy current version
   ```

3. **Emergency Pause**
   ```
   Vercel Dashboard → Settings → Git
   - Disable automatic deployments
   - Investigate issue
   - Re-enable when fixed
   ```

---

## What NOT to Do After Deployment

❌ Do NOT modify PHASE 6 auth logic
❌ Do NOT add OAuth or refresh tokens (PHASE 7)
❌ Do NOT add frontend to this backend
❌ Do NOT change database schema without migration
❌ Do NOT commit .env files
❌ Do NOT use hardcoded credentials
❌ Do NOT reduce rate limit below 100 req/hour
❌ Do NOT disable CORS enforcement
❌ Do NOT modify JWT_EXPIRATION_SECONDS

---

## Deployment Success Criteria

✅ **Deployment is successful if:**
1. All health checks pass
2. Auth endpoints work (signup, login, /me)
3. Research endpoints require authentication
4. Rate limiting enforces 100 requests/hour
5. User scoping prevents cross-user access
6. No 500 errors in logs
7. All critical endpoints respond < 2s
8. Supabase persistence working
9. CORS configured correctly
10. No hardcoded secrets exposed

✅ **Safe to proceed if all above are true**

---

## Documentation References

- **Architecture Details**: See PHASE_6_COMPLETE.md
- **API Reference**: See PHASE_6_COMPLETE.md → API Endpoint Reference
- **Troubleshooting**: See DEPLOYMENT_GUIDE.md → Troubleshooting
- **Configuration**: See .env.example

---

## Deployment Timeline

| Step | Time | Status |
|------|------|--------|
| Supabase setup | 5-10 min | ⏳ |
| Vercel setup | 3-5 min | ⏳ |
| Deploy | 2-3 min | ⏳ |
| Verification | 5-10 min | ⏳ |
| **Total** | **15-30 min** | ⏳ |

---

## Sign-Off

- [ ] All pre-deployment checks completed
- [ ] All deployment steps followed
- [ ] All post-deployment verification passed
- [ ] No critical issues found
- [ ] Ready for production use

**Deployment Date:** _______________
**Deployment URL:** _______________
**Verified By:** _______________

---

**Status: READY FOR DEPLOYMENT** ✅

Do NOT proceed beyond PHASE 6. Deployment is complete when all checks above pass.
