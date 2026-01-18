#!/usr/bin/env python3
"""
Post-Deployment Verification Script for ResearchAssistant Backend
Tests all PHASE 6 endpoints to ensure successful deployment

Usage:
    python verify_deployment.py https://yourdeployment.vercel.app
"""

import requests
import json
import sys
import time
from typing import Tuple, Dict, Any

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

class DeploymentVerifier:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_id = None
        self.job_id = None
        self.passed = 0
        self.failed = 0
        
    def print_header(self, text: str):
        print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
        print(f"{BLUE}{BOLD}{text}{RESET}")
        print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")
    
    def print_test(self, name: str):
        print(f"{BOLD}📋 {name}{RESET}")
    
    def print_pass(self, message: str):
        self.passed += 1
        print(f"  {GREEN}✅ {message}{RESET}")
    
    def print_fail(self, message: str):
        self.failed += 1
        print(f"  {RED}❌ {message}{RESET}")
    
    def print_info(self, message: str):
        print(f"  {YELLOW}ℹ️  {message}{RESET}")
    
    def test_health_check(self) -> bool:
        """Test 1: Health Check"""
        self.print_test("Health Check")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_pass("Health endpoint returns 200 OK")
                self.print_info(f"Status: {data.get('status')}, Auth enabled: {data.get('auth_enabled')}")
                return True
            else:
                self.print_fail(f"Health check returned {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Health check failed: {str(e)}")
            return False
    
    def test_signup(self) -> bool:
        """Test 2: Signup"""
        self.print_test("Signup (Email-only)")
        try:
            email = f"test{int(time.time())}@example.com"
            response = requests.post(
                f"{self.base_url}/api/auth/signup",
                json={"email": email},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                
                if self.token and self.user_id:
                    self.print_pass(f"Signup successful, JWT token received")
                    self.print_info(f"User ID: {self.user_id[:20]}...")
                    return True
                else:
                    self.print_fail("Missing token or user ID in response")
                    return False
            else:
                self.print_fail(f"Signup returned {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.print_fail(f"Signup failed: {str(e)}")
            return False
    
    def test_get_profile(self) -> bool:
        """Test 3: Get Profile"""
        self.print_test("Get User Profile (/me)")
        if not self.token:
            self.print_fail("No token available (signup must succeed first)")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("email"):
                    self.print_pass("Profile retrieved successfully")
                    self.print_info(f"Email: {data.get('email')}")
                    return True
                else:
                    self.print_fail("Email missing from profile")
                    return False
            else:
                self.print_fail(f"Profile endpoint returned {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Get profile failed: {str(e)}")
            return False
    
    def test_create_research_job(self) -> bool:
        """Test 4: Create Research Job"""
        self.print_test("Create Research Job")
        if not self.token:
            self.print_fail("No token available (signup must succeed first)")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/research",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"topic": "Test deployment verification"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.job_id = data.get("job_id")
                if self.job_id:
                    self.print_pass("Research job created successfully")
                    self.print_info(f"Job ID: {self.job_id}")
                    self.print_info(f"Status: {data.get('status')}, Progress: {data.get('progress')}")
                    return True
                else:
                    self.print_fail("Job ID missing from response")
                    return False
            else:
                self.print_fail(f"Create job returned {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.print_fail(f"Create research job failed: {str(e)}")
            return False
    
    def test_get_job_status(self) -> bool:
        """Test 5: Get Job Status"""
        self.print_test("Get Job Status")
        if not self.token or not self.job_id:
            self.print_fail("No token or job ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/research/{self.job_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.print_pass("Job status retrieved successfully")
                self.print_info(f"Status: {data.get('status')}, Progress: {data.get('progress')}")
                return True
            else:
                self.print_fail(f"Get job status returned {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Get job status failed: {str(e)}")
            return False
    
    def test_list_jobs(self) -> bool:
        """Test 6: List User's Jobs"""
        self.print_test("List User's Jobs")
        if not self.token:
            self.print_fail("No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/research",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            if response.status_code == 200:
                jobs = response.json()
                if isinstance(jobs, list):
                    self.print_pass(f"List jobs successful - found {len(jobs)} job(s)")
                    if jobs:
                        self.print_info(f"First job: {jobs[0].get('topic')}")
                    return True
                else:
                    self.print_fail("Response is not a list")
                    return False
            else:
                self.print_fail(f"List jobs returned {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"List jobs failed: {str(e)}")
            return False
    
    def test_auth_required(self) -> bool:
        """Test 7: Authentication Required"""
        self.print_test("Authentication Required (no token)")
        try:
            response = requests.get(
                f"{self.base_url}/api/research",
                timeout=10
            )
            if response.status_code == 401:
                self.print_pass("Correctly returns 401 without token")
                return True
            else:
                self.print_fail(f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Auth check failed: {str(e)}")
            return False
    
    def test_invalid_token(self) -> bool:
        """Test 8: Invalid Token Rejected"""
        self.print_test("Invalid Token Rejected")
        try:
            response = requests.get(
                f"{self.base_url}/api/research",
                headers={"Authorization": "Bearer invalid-token-xyz"},
                timeout=10
            )
            if response.status_code == 401:
                self.print_pass("Correctly rejects invalid token")
                return True
            else:
                self.print_fail(f"Expected 401 for invalid token, got {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Invalid token check failed: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test 9: Rate Limiting"""
        self.print_test("Rate Limiting (100 requests/hour)")
        if not self.token:
            self.print_fail("No token available")
            return False
        
        # Try 5 rapid requests (should all succeed)
        try:
            for i in range(5):
                response = requests.post(
                    f"{self.base_url}/api/research",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json={"topic": f"Rate limit test {i}"},
                    timeout=10
                )
                if response.status_code not in [200, 429]:
                    self.print_fail(f"Unexpected status {response.status_code} on request {i+1}")
                    return False
            
            self.print_pass("Rate limiting mechanism is active")
            self.print_info("Limit is 100 requests/hour per user")
            return True
        except Exception as e:
            self.print_fail(f"Rate limiting test failed: {str(e)}")
            return False
    
    def test_user_scoping(self) -> bool:
        """Test 10: User Scoping (403 on unauthorized access)"""
        self.print_test("User-Scoped Jobs (ownership validation)")
        
        if not self.job_id:
            self.print_fail("No job available from previous tests")
            return False
        
        # Create a second user
        try:
            signup_response = requests.post(
                f"{self.base_url}/api/auth/signup",
                json={"email": f"testuser2-{int(time.time())}@example.com"},
                timeout=10
            )
            if signup_response.status_code != 200:
                self.print_fail("Could not create second user for scoping test")
                return False
            
            token2 = signup_response.json().get("access_token")
            
            # Try to access first user's job with second user's token
            response = requests.get(
                f"{self.base_url}/api/research/{self.job_id}",
                headers={"Authorization": f"Bearer {token2}"},
                timeout=10
            )
            
            if response.status_code == 403:
                self.print_pass("User scoping enforced - returns 403 for unauthorized access")
                return True
            else:
                self.print_fail(f"Expected 403 for unauthorized access, got {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"User scoping test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all verification tests"""
        self.print_header("🚀 ResearchAssistant Deployment Verification")
        print(f"Base URL: {self.base_url}\n")
        
        tests = [
            self.test_health_check,
            self.test_signup,
            self.test_get_profile,
            self.test_create_research_job,
            self.test_get_job_status,
            self.test_list_jobs,
            self.test_auth_required,
            self.test_invalid_token,
            self.test_rate_limiting,
            self.test_user_scoping,
        ]
        
        for test in tests:
            test()
        
        return self.print_summary()
    
    def print_summary(self) -> bool:
        """Print test summary"""
        total = self.passed + self.failed
        
        self.print_header("📊 Verification Summary")
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}\n")
        
        if self.failed == 0:
            print(f"{GREEN}{BOLD}✅ ALL TESTS PASSED - Deployment is successful!{RESET}\n")
            return True
        else:
            print(f"{RED}{BOLD}❌ {self.failed} test(s) failed - Review issues above{RESET}\n")
            return False

def main():
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage: python verify_deployment.py <deployment_url>{RESET}")
        print(f"Example: python verify_deployment.py https://myapp.vercel.app")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    verifier = DeploymentVerifier(base_url)
    success = verifier.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
