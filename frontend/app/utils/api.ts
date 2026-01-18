import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete apiClient.defaults.headers.common['Authorization']
  }
}

export interface SignupRequest {
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
  }
}

export interface CreateJobRequest {
  topic: string
}

export interface ResearchJob {
  // Backend returns job_id; keep id optional for forward compatibility
  job_id: string
  id?: string
  user_id?: string
  topic: string
  status: string
  progress?: Record<string, any> | null
  result?: Record<string, any> | null
  error?: string | null
  final_paper?: string
  created_at?: string
  completed_at?: string
}

export type JobListResponse = ResearchJob[]

// Auth endpoints
export const authAPI = {
  signup: (email: string) => apiClient.post<AuthResponse>('/api/auth/signup', { email }),
  login: (email: string) => apiClient.post<AuthResponse>('/api/auth/login', { email }),
}

// Research endpoints
export const jobsAPI = {
  create: (topic: string) => apiClient.post<ResearchJob>('/api/research/start', { topic }),
  list: () => apiClient.get<JobListResponse>('/api/research'),
  get: (jobId: string) => apiClient.get<ResearchJob>(`/api/research/${jobId}`),
}
