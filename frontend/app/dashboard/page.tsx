'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { useRouter } from 'next/navigation'
import { jobsAPI, ResearchJob } from '@/utils/api'
import Link from 'next/link'

export default function DashboardPage() {
  const [topic, setTopic] = useState('')
  const [jobs, setJobs] = useState<ResearchJob[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')
  const { token, logout } = useAuth()
  const router = useRouter()

  // Redirect to auth if no token
  useEffect(() => {
    if (!token) {
      router.push('/auth')
    }
  }, [token, router])

  // Load jobs on mount
  useEffect(() => {
    if (token) {
      loadJobs()
    }
  }, [token])

  const loadJobs = async () => {
    setIsLoading(true)
    try {
      const response = await jobsAPI.list()
      setJobs(response.data || [])
      setError('')
    } catch (err: any) {
      setError('Failed to load jobs')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!topic.trim()) return

    setIsCreating(true)
    try {
      const response = await jobsAPI.create(topic)
      setJobs([response.data, ...jobs])
      setTopic('')
      setError('')
      // Optionally redirect to job details
      // router.push(`/jobs/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job')
    } finally {
      setIsCreating(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-blue-100 text-blue-800'
    }
  }

  if (!token) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Research Assistant</h1>
          <button
            onClick={() => {
              logout()
              router.push('/auth')
            }}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
          >
            Sign Out
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Create Job Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Create New Research Job</h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleCreateJob} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Research Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Quantum computing applications in cryptography"
              />
            </div>

            <button
              type="submit"
              disabled={isCreating || !topic.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400"
            >
              {isCreating ? 'Creating...' : 'Create Research Job'}
            </button>
          </form>
        </div>

        {/* Jobs List */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold">Your Jobs</h2>
          </div>

          {isLoading && (
            <div className="p-6 text-center text-gray-600">Loading jobs...</div>
          )}

          {!isLoading && jobs.length === 0 && (
            <div className="p-6 text-center text-gray-600">
              No jobs yet. Create one to get started.
            </div>
          )}

          {!isLoading && jobs.length > 0 && (
            <div className="divide-y divide-gray-200">
              {jobs.map((job) => (
                <div key={job.job_id || job.id} className="p-6 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold">{job.topic}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {job.created_at ? `Created: ${new Date(job.created_at).toLocaleDateString()}` : ''}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                      <Link
                        href={`/jobs/${job.job_id || job.id}`}
                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm font-medium"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
