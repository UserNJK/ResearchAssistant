# Research Assistant Frontend

Minimal Next.js frontend for the Research Assistant application.

## Features

- **Email Authentication**: Email-only signup and login
- **Job Management**: Create research jobs and track progress
- **Real-time Status Polling**: Client-side polling for job completion
- **Markdown Rendering**: View research papers in rendered markdown format
- **Responsive Design**: Tailwind CSS for clean, minimal UI

## Tech Stack

- **Framework**: Next.js 14
- **UI**: React 18, Tailwind CSS
- **HTTP Client**: Axios
- **Markdown Rendering**: react-markdown

## Setup

### Prerequisites

- Node.js 18+ and npm
- Running backend at `http://localhost:8000` (or update `.env.local`)

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Create `.env.local`**:
   ```bash
   cp .env.example .env.local
   ```

3. **Update environment variables** in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Development

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/
│   ├── auth/              # Authentication page
│   ├── dashboard/         # Main dashboard with job creation
│   ├── jobs/
│   │   └── [id]/          # Job details with polling
│   ├── context/
│   │   └── AuthContext.tsx # Token and user state management
│   ├── utils/
│   │   └── api.ts         # API client and endpoints
│   ├── components/
│   │   └── ProtectedLayout.tsx # Route protection wrapper
│   ├── globals.css        # Tailwind CSS directives
│   ├── layout.tsx         # Root layout with AuthProvider
│   └── page.tsx           # Home page (redirects based on auth)
├── package.json
├── next.config.js
├── tailwind.config.ts
└── .env.example
```

## Key Components

### AuthContext (`app/context/AuthContext.tsx`)
- Manages JWT token and user state
- Provides `signup(email)` and `login(email)` functions
- Stores token in memory (not localStorage)
- Exports `useAuth()` hook for components

### API Client (`app/utils/api.ts`)
- Axios instance with automatic token attachment
- Typed endpoints for auth and research APIs
- `authAPI.signup()`, `authAPI.login()`
- `jobsAPI.create()`, `jobsAPI.list()`, `jobsAPI.get()`

### Pages
- **`/auth`**: Email login/signup form
- **`/dashboard`**: Create jobs, view job list
- **`/jobs/[id]`**: Job status with polling, markdown viewer

## Authentication Flow

1. User enters email on `/auth` page
2. Frontend calls `/api/auth/signup` or `/api/auth/login`
3. Backend returns JWT token
4. Token stored in React Context
5. Automatically attached to all API requests
6. Redirect to `/dashboard`

## Job Status Polling

The job details page (`/jobs/[id]`) automatically polls the backend every 5 seconds:
- Fetches job status via `GET /api/research/jobs/{job_id}`
- Stops polling when job is `completed` or `failed`
- Displays final paper markdown when ready

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## Building for Production

```bash
npm run build
npm start
```

The built app can be deployed to Vercel or any Node.js hosting.

## Vercel Deployment

### Deploy frontend

1. Push repo to GitHub.
2. In Vercel, create a new project from this repo.
3. Set **Root Directory** to `frontend`.
4. Add environment variable:

```env
NEXT_PUBLIC_API_URL=https://<your-backend-domain>
```

5. Deploy.

### Backend requirements

Deploy backend on Render/Railway/Fly/Azure and configure CORS to allow your Vercel app:

- `CORS_ORIGINS` should include your production Vercel domain.
- `CORS_ORIGIN_REGEX=https://.*\.vercel\.app` is recommended to allow preview deployments.

## Deployment Notes

- **Environment Variable**: Set `NEXT_PUBLIC_API_URL` to your production backend URL.
- **CORS**: Backend must allow requests from frontend domain and previews.
- **Token Security**: Tokens stored in memory (cleared on page refresh).
