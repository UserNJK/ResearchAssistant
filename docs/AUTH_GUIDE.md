# Authentication Implementation Guide

## Overview
Simple email-based authentication using Supabase Auth for a controlled academic environment (10-20 users).

## Design Decisions (FINAL)

### ✅ What We're Using:
- **Supabase Auth** - Built-in authentication system
- **Email-based login** - Simple email entry (no password required initially)
- **Auto-user creation** - If email doesn't exist, create user automatically
- **Session/JWT tokens** - Standard Supabase session management
- **No email verification** - Disabled in Supabase project settings

### ❌ What We're NOT Using:
- ~~NextAuth.js~~ - Removed
- ~~SMTP/Email verification~~ - Disabled
- ~~OTP/Magic links~~ - Not needed
- ~~OAuth (Google, GitHub, etc.)~~ - Not needed
- ~~Password authentication~~ - Optional, simplified

## Implementation Plan (PHASE 6)

### Frontend (Next.js)

#### 1. Install Supabase Client
```bash
npm install @supabase/supabase-js
```

#### 2. Create Supabase Client (`lib/supabase.ts`)
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

#### 3. Login Page (`app/login/page.tsx`)
```typescript
'use client'
import { useState } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Attempt to sign in or sign up
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: true, // Auto-create if doesn't exist
        }
      })

      if (error) throw error

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (error) {
      console.error('Login error:', error)
      alert('Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter your email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Login'}
      </button>
    </form>
  )
}
```

#### 4. Auth Context (`contexts/AuthContext.tsx`)
```typescript
'use client'
import { createContext, useContext, useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { User, Session } from '@supabase/supabase-js'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  loading: true,
  signOut: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signOut = async () => {
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{ user, session, loading, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

#### 5. Protected Route Middleware (`middleware.ts`)
```typescript
import { createMiddlewareClient } from '@supabase/auth-helpers-nextjs'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(req: NextRequest) {
  const res = NextResponse.next()
  const supabase = createMiddlewareClient({ req, res })

  const {
    data: { session },
  } = await supabase.auth.getSession()

  // Redirect to login if not authenticated
  if (!session && req.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  return res
}

export const config = {
  matcher: ['/dashboard/:path*'],
}
```

### Backend (FastAPI)

#### 1. JWT Verification Dependency (`app/auth.py`)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from .config import settings
import httpx

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """
    Verify Supabase JWT token and extract user info
    """
    token = credentials.credentials
    
    try:
        # Verify JWT with Supabase
        # Supabase uses RS256 algorithm
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,  # Add to config
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return {"id": user_id, "email": email}
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
```

#### 2. Protected Endpoint Example
```python
from fastapi import APIRouter, Depends
from .auth import get_current_user

router = APIRouter()

@router.post("/research/start")
async def start_research(
    topic: str,
    current_user: dict = Depends(get_current_user)
):
    """Create research job - requires authentication"""
    user_id = current_user["id"]
    # ... implementation
```

### Supabase Configuration

#### 1. Disable Email Confirmation
In Supabase Dashboard:
1. Go to **Authentication** → **Settings**
2. Set **Enable email confirmations**: `OFF`
3. Set **Enable sign ups**: `ON`
4. Set **Require email confirmation**: `OFF`

#### 2. Configure Email Templates (Optional)
Since we're not using email verification, templates are minimal:
- Welcome email (optional)
- Password reset (if needed later)

#### 3. RLS Policies (PHASE 9)
```sql
-- Users can only access their own data
CREATE POLICY "Users can view own data"
ON research_jobs
FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own data"
ON research_jobs
FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

## Environment Variables

### Backend `.env`
```bash
# Add JWT secret for token verification
SUPABASE_JWT_SECRET=your_jwt_secret_from_supabase_settings
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing Checklist

- [ ] User can enter email and access system
- [ ] New email creates user automatically
- [ ] Existing email logs in successfully
- [ ] Session persists across page reloads
- [ ] Protected routes require authentication
- [ ] Logout clears session
- [ ] Backend validates JWT tokens
- [ ] Users can only access their own data

## Security Considerations

1. **Controlled Environment**: 10-20 known users (academic setting)
2. **No Public Access**: Application not publicly accessible
3. **JWT Expiration**: Default Supabase session timeout (1 hour)
4. **RLS Enabled**: Row-level security enforces user isolation
5. **HTTPS Required**: In production (Vercel handles this)

## Migration from Current Plan

### Remove:
- ❌ All NextAuth dependencies
- ❌ OAuth provider configurations
- ❌ Email verification flows
- ❌ Magic link implementations

### Keep:
- ✅ Supabase client setup
- ✅ Session management
- ✅ Protected routes
- ✅ User context

## Benefits of This Approach

1. **Simplicity**: Single authentication provider (Supabase)
2. **Zero Configuration**: No SMTP, OAuth apps, or external services
3. **Fast Onboarding**: Users just enter email and start
4. **Unified Stack**: Same DB handles auth and data
5. **Built-in Security**: Supabase handles token management
6. **Academic-Friendly**: Matches controlled environment use case

---

**Status**: Design locked, ready for PHASE 6 implementation
**Dependencies**: Supabase project with auth enabled
**Complexity**: Low (compared to NextAuth + OAuth)
