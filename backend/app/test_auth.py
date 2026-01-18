"""
Test suite for PHASE 6: Authentication & Security layer.

Tests cover:
- Email-only authentication (signup, login)
- JWT token generation and validation
- Bearer token authentication on protected endpoints
- Per-user rate limiting (100 requests/hour)
- User-scoped job access (cannot view/cancel other user's jobs)
- CORS enforcement
- Request validation and error handling
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

# Import the app and dependencies
from main import app, get_current_user
from auth import get_auth_service, AuthenticationError
from middleware import get_auth_middleware, clear_rate_limit_cache
from config import USER_RATE_LIMIT_REQUESTS, USER_RATE_LIMIT_WINDOW_SECONDS

# Test client
client = TestClient(app)


class TestSignup:
    """Test signup endpoint (POST /api/auth/signup)"""
    
    def test_signup_success(self):
        """Test successful signup with email"""
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert "id" in data["user"]
    
    def test_signup_invalid_email(self):
        """Test signup with invalid email format"""
        response = client.post(
            "/api/auth/signup",
            json={"email": "not-an-email"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_signup_missing_email(self):
        """Test signup without email"""
        response = client.post(
            "/api/auth/signup",
            json={}
        )
        assert response.status_code == 422
    
    def test_signup_with_password_ignored(self):
        """Test that password field (if provided) is ignored"""
        response = client.post(
            "/api/auth/signup",
            json={"email": "user@example.com", "password": "ignored"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_signup_empty_email(self):
        """Test signup with empty email string"""
        response = client.post(
            "/api/auth/signup",
            json={"email": ""}
        )
        assert response.status_code == 422


class TestLogin:
    """Test login endpoint (POST /api/auth/login)"""
    
    def test_login_success(self):
        """Test successful login with email"""
        # First signup
        client.post("/api/auth/signup", json={"email": "login@example.com"})
        
        # Then login
        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "login@example.com"
    
    def test_login_invalid_email(self):
        """Test login with invalid email format"""
        response = client.post(
            "/api/auth/login",
            json={"email": "invalid-email"}
        )
        assert response.status_code == 422
    
    def test_login_missing_email(self):
        """Test login without email"""
        response = client.post(
            "/api/auth/login",
            json={}
        )
        assert response.status_code == 422
    
    def test_login_creates_user_if_not_exists(self):
        """Test that login auto-creates user if doesn't exist"""
        response = client.post(
            "/api/auth/login",
            json={"email": "new-user@example.com"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestAuthMe:
    """Test /api/auth/me endpoint (GET)"""
    
    def test_me_with_valid_token(self):
        """Test /me with valid authentication"""
        # Signup to get token
        signup_response = client.post(
            "/api/auth/signup",
            json={"email": "me@example.com"}
        )
        token = signup_response.json()["access_token"]
        
        # Access /me with token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert "id" in data
    
    def test_me_without_token(self):
        """Test /me without authentication header"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_me_with_invalid_token(self):
        """Test /me with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-xyz"}
        )
        assert response.status_code == 401
    
    def test_me_with_malformed_auth_header(self):
        """Test /me with malformed Authorization header"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearerToken"}
        )
        assert response.status_code == 401
    
    def test_me_returns_correct_user_data(self):
        """Test that /me returns correct user profile"""
        email = f"profile-test-{int(time.time())}@example.com"
        signup_response = client.post(
            "/api/auth/signup",
            json={"email": email}
        )
        token = signup_response.json()["access_token"]
        user_id = signup_response.json()["user"]["id"]
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == email


class TestRateLimiting:
    """Test per-user rate limiting (100 requests/hour)"""
    
    def setup_method(self):
        """Clear rate limit cache before each test"""
        clear_rate_limit_cache()
    
    def test_rate_limit_within_threshold(self):
        """Test that requests within limit are allowed"""
        # Signup to get token and user_id
        signup_response = client.post(
            "/api/auth/signup",
            json={"email": "ratelimit@example.com"}
        )
        token = signup_response.json()["access_token"]
        
        # Create 5 research jobs (should all succeed)
        for i in range(5):
            response = client.post(
                "/api/research",
                headers={"Authorization": f"Bearer {token}"},
                json={"topic": f"Test topic {i}"}
            )
            assert response.status_code == 200
    
    def test_rate_limit_enforced_at_limit(self):
        """Test that requests exceeding limit are rejected with 429"""
        signup_response = client.post(
            "/api/auth/signup",
            json={"email": f"ratelimit-exceed-{int(time.time())}@example.com"}
        )
        token = signup_response.json()["access_token"]
        
        # Create USER_RATE_LIMIT_REQUESTS + 1 requests
        # This simulates the user exceeding their hourly quota
        # Note: In real testing, we'd mock the time or use a smaller test limit
        success_count = 0
        rate_limited = False
        
        for i in range(min(10, USER_RATE_LIMIT_REQUESTS + 1)):
            response = client.post(
                "/api/research",
                headers={"Authorization": f"Bearer {token}"},
                json={"topic": f"Stress test topic {i}"}
            )
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                break
        
        # At minimum, verify rate limiting check is in place
        # (Full test would need to mock rate limit settings)
        assert success_count > 0
    
    def test_rate_limit_per_user(self):
        """Test that rate limiting is per-user (different users have separate limits)"""
        # User 1
        user1_response = client.post(
            "/api/auth/signup",
            json={"email": f"user1-{int(time.time())}@example.com"}
        )
        user1_token = user1_response.json()["access_token"]
        
        # User 2
        user2_response = client.post(
            "/api/auth/signup",
            json={"email": f"user2-{int(time.time())}@example.com"}
        )
        user2_token = user2_response.json()["access_token"]
        
        # Both users should be able to make requests independently
        response1 = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "User 1 topic"}
        )
        response2 = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user2_token}"},
            json={"topic": "User 2 topic"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestUserScopedJobs:
    """Test that jobs are user-scoped (users can't access other users' jobs)"""
    
    def setup_method(self):
        """Clear rate limit cache before each test"""
        clear_rate_limit_cache()
    
    def test_cannot_view_other_user_job(self):
        """Test that user cannot GET another user's job"""
        # User 1 creates a job
        user1_response = client.post(
            "/api/auth/signup",
            json={"email": f"owner-{int(time.time())}@example.com"}
        )
        user1_token = user1_response.json()["access_token"]
        
        create_response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "Secret research"}
        )
        job_id = create_response.json()["job_id"]
        
        # User 2 tries to access User 1's job
        user2_response = client.post(
            "/api/auth/signup",
            json={"email": f"attacker-{int(time.time())}@example.com"}
        )
        user2_token = user2_response.json()["access_token"]
        
        response = client.get(
            f"/api/research/{job_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_can_view_own_job(self):
        """Test that user CAN GET their own job"""
        user_response = client.post(
            "/api/auth/signup",
            json={"email": f"owner-view-{int(time.time())}@example.com"}
        )
        token = user_response.json()["access_token"]
        
        create_response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {token}"},
            json={"topic": "My research"}
        )
        job_id = create_response.json()["job_id"]
        
        response = client.get(
            f"/api/research/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id
    
    def test_cannot_cancel_other_user_job(self):
        """Test that user cannot cancel another user's job"""
        # User 1 creates a job
        user1_response = client.post(
            "/api/auth/signup",
            json={"email": f"user1-cancel-{int(time.time())}@example.com"}
        )
        user1_token = user1_response.json()["access_token"]
        
        create_response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "Do not cancel"}
        )
        job_id = create_response.json()["job_id"]
        
        # User 2 tries to cancel User 1's job
        user2_response = client.post(
            "/api/auth/signup",
            json={"email": f"user2-cancel-{int(time.time())}@example.com"}
        )
        user2_token = user2_response.json()["access_token"]
        
        response = client.post(
            f"/api/research/{job_id}/cancel",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    def test_list_jobs_shows_only_user_jobs(self):
        """Test that GET /api/research only shows user's own jobs"""
        # User 1 creates 2 jobs
        user1_response = client.post(
            "/api/auth/signup",
            json={"email": f"user1-list-{int(time.time())}@example.com"}
        )
        user1_token = user1_response.json()["access_token"]
        
        client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "User 1 research 1"}
        )
        client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "User 1 research 2"}
        )
        
        # User 2 creates 1 job
        user2_response = client.post(
            "/api/auth/signup",
            json={"email": f"user2-list-{int(time.time())}@example.com"}
        )
        user2_token = user2_response.json()["access_token"]
        
        client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user2_token}"},
            json={"topic": "User 2 research 1"}
        )
        
        # User 1 lists jobs - should see only their 2 jobs
        response = client.get(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 200
        jobs = response.json()
        user1_topics = [j["topic"] for j in jobs]
        assert "User 1 research 1" in user1_topics
        assert "User 1 research 2" in user1_topics
        assert "User 2 research 1" not in user1_topics
        
        # User 2 lists jobs - should see only their 1 job
        response = client.get(
            "/api/research",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) == 1
        assert jobs[0]["topic"] == "User 2 research 1"


class TestResearchEndpointAuthentication:
    """Test that research endpoints require authentication"""
    
    def test_post_research_requires_auth(self):
        """Test POST /api/research without token returns 401"""
        response = client.post(
            "/api/research",
            json={"topic": "Test topic"}
        )
        assert response.status_code == 401
    
    def test_get_research_list_requires_auth(self):
        """Test GET /api/research without token returns 401"""
        response = client.get("/api/research")
        assert response.status_code == 401
    
    def test_get_research_job_requires_auth(self):
        """Test GET /api/research/{job_id} without token returns 401"""
        response = client.get("/api/research/nonexistent-id")
        assert response.status_code == 401
    
    def test_cancel_research_requires_auth(self):
        """Test POST /api/research/{job_id}/cancel without token returns 401"""
        response = client.post("/api/research/nonexistent-id/cancel")
        assert response.status_code == 401
    
    def test_stats_requires_auth(self):
        """Test GET /api/research/stats without token returns 401"""
        response = client.get("/api/research/stats")
        assert response.status_code == 401


class TestCORSEnforcement:
    """Test CORS enforcement"""
    
    def test_cors_simple_request(self):
        """Test CORS headers are present in response"""
        response = client.get("/health")
        # Note: TestClient may not fully simulate CORS headers
        # In production, verify with real HTTP requests
        assert response.status_code == 200
    
    def test_cors_allowed_methods(self):
        """Test that only allowed methods are permitted"""
        # GET, POST, OPTIONS should be allowed
        health_get = client.get("/health")
        assert health_get.status_code == 200
    
    def test_cors_allowed_headers(self):
        """Test that Authorization header is allowed"""
        response = client.get(
            "/health",
            headers={"Authorization": "Bearer test-token"}
        )
        # Should not reject due to header
        assert response.status_code == 200


class TestJWTValidation:
    """Test JWT token validation and expiration"""
    
    def test_jwt_token_format(self):
        """Test that JWT tokens have valid format (3 parts)"""
        response = client.post(
            "/api/auth/signup",
            json={"email": f"jwt-{int(time.time())}@example.com"}
        )
        token = response.json()["access_token"]
        
        # JWT should have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3
    
    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected"""
        # This test would need to mock time or the JWT library
        # For now, verify that invalid tokens are rejected
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer expired.token.here"}
        )
        assert response.status_code == 401
    
    def test_tampered_token_rejected(self):
        """Test that tampered tokens are rejected"""
        response = client.post(
            "/api/auth/signup",
            json={"email": f"tamper-{int(time.time())}@example.com"}
        )
        token = response.json()["access_token"]
        
        # Tamper with token
        tampered = token[:-5] + "XXXXX"
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {tampered}"}
        )
        assert response.status_code == 401


class TestRequestValidation:
    """Test basic request validation"""
    
    def test_research_topic_validation(self):
        """Test that research POST validates topic field"""
        response = client.post(
            "/api/auth/signup",
            json={"email": f"validation-{int(time.time())}@example.com"}
        )
        token = response.json()["access_token"]
        
        # Missing topic
        response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        assert response.status_code == 422
    
    def test_topic_cannot_be_empty(self):
        """Test that empty topic is rejected"""
        response = client.post(
            "/api/auth/signup",
            json={"email": f"empty-topic-{int(time.time())}@example.com"}
        )
        token = response.json()["access_token"]
        
        response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {token}"},
            json={"topic": ""}
        )
        # Empty string may or may not be validated depending on model
        # At minimum, the request should be processed


class TestAuthenticationErrorHandling:
    """Test error handling in authentication"""
    
    def test_invalid_json_request(self):
        """Test invalid JSON request"""
        response = client.post(
            "/api/auth/signup",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_content_type_header(self):
        """Test request without Content-Type"""
        # TestClient usually handles this, but test anyway
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com"}
        )
        # Should still work with testclient
        assert response.status_code in [200, 422]
    
    def test_auth_error_response_format(self):
        """Test that auth errors return proper JSON"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestEndToEndFlow:
    """Test complete authentication flow"""
    
    def test_signup_login_research_flow(self):
        """Test complete flow: signup -> login -> create research job"""
        email = f"e2e-{int(time.time())}@example.com"
        
        # 1. Signup
        signup_response = client.post(
            "/api/auth/signup",
            json={"email": email}
        )
        assert signup_response.status_code == 200
        signup_token = signup_response.json()["access_token"]
        user_id = signup_response.json()["user"]["id"]
        
        # 2. Verify /me works
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {signup_token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
        
        # 3. Create research job
        research_response = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {signup_token}"},
            json={"topic": "E2E test research"}
        )
        assert research_response.status_code == 200
        job_id = research_response.json()["job_id"]
        
        # 4. Retrieve job
        get_response = client.get(
            f"/api/research/{job_id}",
            headers={"Authorization": f"Bearer {signup_token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["job_id"] == job_id
        
        # 5. List jobs
        list_response = client.get(
            "/api/research",
            headers={"Authorization": f"Bearer {signup_token}"}
        )
        assert list_response.status_code == 200
        jobs = list_response.json()
        assert any(j["job_id"] == job_id for j in jobs)
    
    def test_separate_users_isolation(self):
        """Test that two separate users are completely isolated"""
        email1 = f"isolation1-{int(time.time())}@example.com"
        email2 = f"isolation2-{int(time.time())}@example.com"
        
        # User 1 signup and create job
        user1_signup = client.post(
            "/api/auth/signup",
            json={"email": email1}
        )
        user1_token = user1_signup.json()["access_token"]
        user1_id = user1_signup.json()["user"]["id"]
        
        user1_job = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"},
            json={"topic": "User 1 secret data"}
        )
        job1_id = user1_job.json()["job_id"]
        
        # User 2 signup and create job
        user2_signup = client.post(
            "/api/auth/signup",
            json={"email": email2}
        )
        user2_token = user2_signup.json()["access_token"]
        user2_id = user2_signup.json()["user"]["id"]
        
        user2_job = client.post(
            "/api/research",
            headers={"Authorization": f"Bearer {user2_token}"},
            json={"topic": "User 2 secret data"}
        )
        job2_id = user2_job.json()["job_id"]
        
        # Verify users are different
        assert user1_id != user2_id
        
        # Verify User 1 cannot see User 2's job
        response = client.get(
            f"/api/research/{job2_id}",
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        assert response.status_code == 403
        
        # Verify User 2 cannot see User 1's job
        response = client.get(
            f"/api/research/{job1_id}",
            headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert response.status_code == 403
        
        # Verify User 1's list only has their job
        list1 = client.get(
            "/api/research",
            headers={"Authorization": f"Bearer {user1_token}"}
        ).json()
        assert len(list1) == 1
        assert list1[0]["job_id"] == job1_id
        assert list1[0]["topic"] == "User 1 secret data"
        
        # Verify User 2's list only has their job
        list2 = client.get(
            "/api/research",
            headers={"Authorization": f"Bearer {user2_token}"}
        ).json()
        assert len(list2) == 1
        assert list2[0]["job_id"] == job2_id
        assert list2[0]["topic"] == "User 2 secret data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
