'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { useRouter } from 'next/navigation'
import { jobsAPI, ResearchJob } from '@/utils/api'
import { useToast } from '@/components/Toast'
import Link from 'next/link'

/* ───────── helpers ───────── */

const statusConfig: Record<string, { dot: string; bg: string; text: string; label: string }> = {
  completed: { dot: 'bg-emerald-400', bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Completed' },
  complete:  { dot: 'bg-emerald-400', bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Completed' },
  failed:    { dot: 'bg-red-400',     bg: 'bg-red-50',     text: 'text-red-700',     label: 'Failed' },
  error:     { dot: 'bg-red-400',     bg: 'bg-red-50',     text: 'text-red-700',     label: 'Failed' },
  pending:   { dot: 'bg-amber-400',   bg: 'bg-amber-50',   text: 'text-amber-700',   label: 'Pending' },
  planning:  { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Planning' },
  searching: { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Searching' },
  summarizing:{ dot: 'bg-brand-400',  bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Summarizing' },
  analyzing: { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Analyzing' },
  formatting:{ dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Formatting' },
}

const fallbackStatus = { dot: 'bg-slate-400', bg: 'bg-slate-50', text: 'text-slate-700', label: 'Unknown' }

function getStatus(s: string) { return statusConfig[s] || fallbackStatus }

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

/* ───────── skeleton ───────── */

function JobSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-4 rounded-xl">
          <div className="skeleton h-4 w-3/4 mb-2" />
          <div className="skeleton h-3 w-1/2" />
        </div>
      ))}
    </div>
  )
}

/* ───────── main page ───────── */

export default function DashboardPage() {
  const [topic, setTopic] = useState('')
  const [jobs, setJobs] = useState<ResearchJob[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { token, user, logout } = useAuth()
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => {
    if (!token) router.push('/auth')
  }, [token, router])

  useEffect(() => {
    if (token) loadJobs()
  }, [token])

  const loadJobs = async () => {
    setIsLoading(true)
    try {
      const response = await jobsAPI.list()
      setJobs(response.data || [])
    } catch {
      toast('Failed to load jobs', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault()
    const cleaned = topic.trim()
    if (!cleaned) return

    setIsCreating(true)
    try {
      const response = await jobsAPI.create(cleaned)
      setJobs([response.data, ...jobs])
      setTopic('')
      toast('Research job created successfully!', 'success')
      router.push(`/jobs/${response.data.job_id || response.data.id}`)
    } catch (err: any) {
      toast(err.response?.data?.detail || 'Failed to create job', 'error')
    } finally {
      setIsCreating(false)
    }
  }

  if (!token) return null

  const completedJobs = jobs.filter((j) => j.status === 'completed' || j.status === 'complete')
  const activeJobs    = jobs.filter((j) => j.status !== 'completed' && j.status !== 'complete' && j.status !== 'failed' && j.status !== 'error')
  const failedJobs    = jobs.filter((j) => j.status === 'failed' || j.status === 'error')

  return (
    <div className="min-h-screen mesh-gradient flex">
      {/* ════════ Sidebar ════════ */}
      <aside
        className={`${
          sidebarOpen ? 'w-80' : 'w-0 overflow-hidden'
        } transition-all duration-300 ease-out border-r border-slate-200/60 bg-white/60 backdrop-blur-xl flex flex-col`}
      >
        {/* Sidebar header */}
        <div className="px-5 pt-6 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">Research Assistant</h1>
          </div>
          <p className="text-xs text-slate-500 ml-12">AI-powered research papers</p>
        </div>

        {/* Sidebar job list */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
          {isLoading && <JobSkeleton />}

          {!isLoading && jobs.length === 0 && (
            <div className="text-center py-10 px-4">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                <svg className="w-7 h-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              </div>
              <p className="text-sm text-slate-500 font-medium">No research yet</p>
              <p className="text-xs text-slate-400 mt-1">Create your first topic to begin.</p>
            </div>
          )}

          {/* Active jobs */}
          {activeJobs.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-2 mb-2">
                In Progress ({activeJobs.length})
              </p>
              {activeJobs.map((job) => {
                const s = getStatus(job.status)
                return (
                  <Link
                    key={job.job_id || job.id}
                    href={`/jobs/${job.job_id || job.id}`}
                    className="group flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-brand-50/60 transition-all duration-200 mb-1"
                  >
                    <span className={`mt-1.5 w-2 h-2 rounded-full ${s.dot} animate-pulse-dot flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate group-hover:text-brand-700 transition-colors">
                        {job.topic}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">{s.label} · {job.created_at ? timeAgo(job.created_at) : ''}</p>
                    </div>
                  </Link>
                )
              })}
            </div>
          )}

          {/* Completed jobs */}
          {completedJobs.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-2 mb-2">
                Completed ({completedJobs.length})
              </p>
              {completedJobs.map((job) => (
                <Link
                  key={job.job_id || job.id}
                  href={`/jobs/${job.job_id || job.id}`}
                  className="group flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-emerald-50/60 transition-all duration-200 mb-1"
                >
                  <span className="mt-1.5 w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate group-hover:text-emerald-700 transition-colors">
                      {job.topic}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">{job.created_at ? timeAgo(job.created_at) : ''}</p>
                  </div>
                  <svg className="w-4 h-4 text-emerald-400 mt-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </Link>
              ))}
            </div>
          )}

          {/* Failed jobs */}
          {failedJobs.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-2 mb-2">
                Failed ({failedJobs.length})
              </p>
              {failedJobs.map((job) => (
                <Link
                  key={job.job_id || job.id}
                  href={`/jobs/${job.job_id || job.id}`}
                  className="group flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-red-50/60 transition-all duration-200 mb-1"
                >
                  <span className="mt-1.5 w-2 h-2 rounded-full bg-red-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate group-hover:text-red-700 transition-colors">
                      {job.topic}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">{job.created_at ? timeAgo(job.created_at) : ''}</p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar footer */}
        <div className="border-t border-slate-100 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 flex items-center justify-center text-xs text-white font-bold flex-shrink-0">
                {(user?.email || '?')[0].toUpperCase()}
              </div>
              <span className="text-xs text-slate-600 truncate">{user?.email || ''}</span>
            </div>
            <button
              onClick={() => { logout(); router.push('/auth') }}
              className="text-xs text-slate-400 hover:text-red-500 transition-colors flex-shrink-0"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* ════════ Main Content ════════ */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 border-b border-slate-200/50 bg-white/50 backdrop-blur-md flex items-center px-6 gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center transition-colors"
          >
            <svg className="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h2 className="text-sm font-semibold text-slate-700">New Research</h2>
          <div className="flex-1" />
          <button
            onClick={loadJobs}
            disabled={isLoading}
            className="text-xs text-slate-500 hover:text-brand-600 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Syncing...' : 'Refresh'}
          </button>
        </header>

        {/* Centered form area */}
        <main className="flex-1 flex items-start justify-center overflow-y-auto px-6 pt-16 pb-10">
          <div className="w-full max-w-2xl animate-fade-in">
            {/* Hero */}
            <div className="text-center mb-10">
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                What do you want to research?
              </h2>
              <p className="text-slate-500 mt-2 text-base">
                Enter a clear, specific topic and our AI agents will produce a comprehensive research paper.
              </p>
            </div>

            {/* Input card */}
            <form onSubmit={handleCreateJob} className="glass-card rounded-2xl p-6 shadow-lg shadow-slate-200/50">
              <div className="relative">
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  rows={3}
                  required
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white/80 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/40 focus:border-brand-400 resize-none text-[15px] transition-all"
                  placeholder="e.g., The impact of large language models on scientific research methodology..."
                />
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs text-slate-400">
                    {topic.trim().length > 0 ? `${topic.trim().length} chars` : 'Be specific for best results'}
                  </span>
                  <button
                    type="submit"
                    disabled={isCreating || !topic.trim()}
                    className="inline-flex items-center gap-2 bg-gradient-to-r from-brand-600 to-purple-600 text-white px-6 py-2.5 rounded-xl font-semibold text-sm hover:from-brand-700 hover:to-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-brand-500/25 hover:shadow-lg hover:shadow-brand-500/30 active:scale-[0.97]"
                  >
                    {isCreating ? (
                      <>
                        <svg className="w-4 h-4 animate-spin-slow" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Creating...
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Start Research
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>

            {/* Quick suggestions */}
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {[
                'Quantum computing in cryptography',
                'Climate change mitigation strategies',
                'AI ethics in healthcare',
                'Renewable energy storage solutions',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setTopic(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-200 text-slate-500 hover:border-brand-300 hover:text-brand-600 hover:bg-brand-50 transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>

            {/* Recent activity (below form) */}
            {!isLoading && jobs.length > 0 && (
              <div className="mt-14 animate-slide-up">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Recent Activity</h3>
                <div className="grid gap-3">
                  {jobs.slice(0, 5).map((job) => {
                    const s = getStatus(job.status)
                    const isActive = !['completed', 'complete', 'failed', 'error'].includes(job.status)
                    return (
                      <Link
                        key={job.job_id || job.id}
                        href={`/jobs/${job.job_id || job.id}`}
                        className="group glass-card rounded-xl px-5 py-4 flex items-center gap-4 hover:shadow-md hover:shadow-slate-200/50 transition-all duration-200"
                      >
                        <span className={`w-2.5 h-2.5 rounded-full ${s.dot} ${isActive ? 'animate-pulse-dot' : ''} flex-shrink-0`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-800 truncate group-hover:text-brand-700 transition-colors">
                            {job.topic}
                          </p>
                          <p className="text-xs text-slate-400 mt-0.5">
                            {s.label}{job.created_at ? ` · ${timeAgo(job.created_at)}` : ''}
                          </p>
                        </div>
                        <svg className="w-4 h-4 text-slate-300 group-hover:text-brand-500 transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                        </svg>
                      </Link>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
