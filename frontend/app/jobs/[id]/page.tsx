'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { jobsAPI, ResearchJob } from '@/utils/api'
import ReactMarkdown from 'react-markdown'
import Link from 'next/link'

export default function JobDetailsPage() {
  const params = useParams()
  const jobId = params.id as string
  const [job, setJob] = useState<ResearchJob | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isPolling, setIsPolling] = useState(false)
  const { token } = useAuth()
  const router = useRouter()

  // Redirect to auth if no token
  useEffect(() => {
    if (!token) {
      router.push('/auth')
    }
  }, [token, router])

  // Load job details
  useEffect(() => {
    if (token && jobId) {
      loadJob()
    }
  }, [token, jobId])

  // Poll for updates if job is still running
  useEffect(() => {
    if (!job || job.status === 'complete' || job.status === 'completed' || job.status === 'error' || job.status === 'failed') {
      return
    }

    setIsPolling(true)
    const interval = setInterval(() => {
      loadJob()
    }, 5000) // Poll every 5 seconds

    return () => {
      clearInterval(interval)
      setIsPolling(false)
    }
  }, [job?.job_id, job?.id, job?.status, token])

  const loadJob = async () => {
    try {
      const response = await jobsAPI.get(jobId)
      setJob(response.data)
      setError('')
    } catch (err: any) {
      setError('Failed to load job details')
    } finally {
      setIsLoading(false)
    }
  }

  const downloadMarkdown = () => {
    if (!finalPaper) return
    const blob = new Blob([finalPaper], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${job?.topic.replace(/[^a-z0-9]/gi, '_')}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadPDF = async () => {
    if (!jobId || !token) return
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/research/${jobId}/pdf`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) throw new Error('PDF export failed')
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${job?.topic.replace(/[^a-z0-9]/gi, '_')}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download PDF')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'complete':
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'planning':
      case 'searching':
      case 'summarizing':
      case 'analyzing':
      case 'formatting':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusMessage = (status: string) => {
    switch (status) {
      case 'complete':
      case 'completed':
        return 'Research completed successfully'
      case 'error':
      case 'failed':
        return 'Research failed'
      case 'pending':
      case 'planning':
      case 'searching':
      case 'summarizing':
      case 'analyzing':
      case 'formatting':
        return 'Research in progress...'
      default:
        return 'Unknown status'
    }
  }

  if (!token) {
    return null
  }

  // Extract final_paper from result if nested (after null checks)
  const finalPaper = job?.final_paper || job?.result?.final_paper

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div>Loading job details...</div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Job not found</p>
          <Link href="/dashboard" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/dashboard" className="text-blue-600 hover:underline">
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Job Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{job.topic}</h1>
              {job.created_at && (
                <p className="text-gray-600">
                  Created: {new Date(job.created_at).toLocaleString()}
                </p>
              )}
              {job.completed_at && (
                <p className="text-gray-600">
                  Completed: {new Date(job.completed_at).toLocaleString()}
                </p>
              )}
            </div>
            <div className="text-right">
              <span className={`inline-block px-4 py-2 rounded-full font-medium ${getStatusColor(job.status)}`}>
                {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
              </span>
              {isPolling && (
                <p className="text-sm text-gray-600 mt-2">Checking for updates...</p>
              )}
            </div>
          </div>
        </div>

        {/* Status Message */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <p className="text-center text-gray-700">{getStatusMessage(job.status)}</p>
        </div>

        {/* Paper Content */}
        {finalPaper && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Research Paper</h2>
              <button
                onClick={downloadPDF}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Download PDF
              </button>
            </div>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{finalPaper}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* No Paper Yet */}
        {!finalPaper && job.status !== 'complete' && job.status !== 'completed' && (
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-center">
              Paper will appear here once research is complete.
            </p>
          </div>
        )}

        {/* Error state */}
        {job.error && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold mb-4 text-red-600">Error</h2>
            <p className="text-gray-700">{job.error}</p>
          </div>
        )}
      </main>
    </div>
  )
}
