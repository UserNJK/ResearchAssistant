'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { useRouter, useParams } from 'next/navigation'
import { jobsAPI, ResearchJob } from '@/utils/api'
import { useToast } from '@/components/Toast'
import ReactMarkdown from 'react-markdown'
import Link from 'next/link'

/* ───────── status helpers ───────── */
const statusCfg: Record<string, { dot: string; bg: string; text: string; label: string; ring?: boolean }> = {
  completed:   { dot: 'bg-emerald-400', bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Completed' },
  complete:    { dot: 'bg-emerald-400', bg: 'bg-emerald-50', text: 'text-emerald-700', label: 'Completed' },
  failed:      { dot: 'bg-red-400',     bg: 'bg-red-50',     text: 'text-red-700',     label: 'Failed' },
  error:       { dot: 'bg-red-400',     bg: 'bg-red-50',     text: 'text-red-700',     label: 'Failed' },
  pending:     { dot: 'bg-amber-400',   bg: 'bg-amber-50',   text: 'text-amber-700',   label: 'Pending', ring: true },
  planning:    { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Planning', ring: true },
  searching:   { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Searching', ring: true },
  summarizing: { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Summarizing', ring: true },
  analyzing:   { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Analyzing', ring: true },
  formatting:  { dot: 'bg-brand-400',   bg: 'bg-brand-50',   text: 'text-brand-700',   label: 'Formatting', ring: true },
}
const fallback = { dot: 'bg-slate-400', bg: 'bg-slate-50', text: 'text-slate-700', label: 'Unknown' }
function getStatus(s: string) { return statusCfg[s] || fallback }

const pipelineSteps = ['pending', 'planning', 'searching', 'summarizing', 'analyzing', 'formatting', 'completed']

function StepTimeline({ current }: { current: string }) {
  const idx = pipelineSteps.indexOf(current)
  const normalizedIdx = idx === -1 ? (current === 'complete' ? pipelineSteps.length - 1 : 0) : idx
  return (
    <div className="flex items-center gap-1 w-full">
      {pipelineSteps.map((step, i) => {
        const done = i < normalizedIdx || current === 'complete' || current === 'completed'
        const active = i === normalizedIdx && current !== 'complete' && current !== 'completed' && current !== 'failed' && current !== 'error'
        return (
          <div key={step} className="flex-1 flex flex-col items-center gap-1.5">
            <div
              className={`h-1.5 w-full rounded-full transition-all duration-500 ${
                done ? 'bg-emerald-400' : active ? 'bg-brand-400 animate-pulse' : 'bg-slate-200'
              }`}
            />
            <span className={`text-[10px] font-medium transition-colors ${
              done ? 'text-emerald-600' : active ? 'text-brand-600' : 'text-slate-400'
            }`}>
              {step.charAt(0).toUpperCase() + step.slice(1)}
            </span>
          </div>
        )
      })}
    </div>
  )
}

/* ───────── main page ───────── */
export default function JobDetailsPage() {
  const params = useParams()
  const jobId = params.id as string
  const [job, setJob] = useState<ResearchJob | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isPolling, setIsPolling] = useState(false)
  const { token } = useAuth()
  const router = useRouter()
  const { toast } = useToast()

  useEffect(() => { if (!token) router.push('/auth') }, [token, router])

  useEffect(() => { if (token && jobId) loadJob() }, [token, jobId])

  // Auto-poll while in-progress
  useEffect(() => {
    if (!job) return
    const done = ['complete', 'completed', 'error', 'failed'].includes(job.status)
    if (done) { setIsPolling(false); return }
    setIsPolling(true)
    const iv = setInterval(loadJob, 5000)
    return () => { clearInterval(iv); setIsPolling(false) }
  }, [job?.job_id, job?.id, job?.status, token])

  const loadJob = async () => {
    try {
      const r = await jobsAPI.get(jobId)
      setJob(r.data)
    } catch {
      toast('Failed to load job details', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const finalPaper = job?.final_paper || job?.result?.final_paper

  const copyMarkdown = async () => {
    if (!finalPaper) return
    try { await navigator.clipboard.writeText(finalPaper); toast('Copied to clipboard!', 'success') }
    catch { toast('Failed to copy', 'error') }
  }

  const downloadMarkdown = () => {
    if (!finalPaper) return
    const blob = new Blob([finalPaper], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url
    a.download = `${job?.topic.replace(/[^a-z0-9]/gi, '_')}.md`
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast('Markdown downloaded', 'success')
  }

  const downloadPDF = async () => {
    if (!jobId || !token) return
    try {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/research/${jobId}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!r.ok) throw new Error()
      const blob = await r.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a'); a.href = url
      a.download = `${job?.topic.replace(/[^a-z0-9]/gi, '_')}.pdf`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast('PDF downloaded', 'success')
    } catch {
      toast('Failed to export PDF', 'error')
    }
  }

  if (!token) return null

  /* ── Loading skeleton ── */
  if (isLoading) {
    return (
      <div className="min-h-screen mesh-gradient flex items-center justify-center">
        <div className="w-full max-w-3xl space-y-6 px-6">
          <div className="skeleton h-10 w-2/3 rounded-xl" />
          <div className="skeleton h-5 w-1/3 rounded-lg" />
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/6 rounded" />
          </div>
        </div>
      </div>
    )
  }

  /* ── Not found ── */
  if (!job) {
    return (
      <div className="min-h-screen mesh-gradient flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-slate-600 font-medium mb-2">Job not found</p>
          <Link href="/dashboard" className="text-sm text-brand-600 hover:text-brand-800 font-medium">
            &larr; Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const s = getStatus(job.status)
  const isActive = !['complete', 'completed', 'failed', 'error'].includes(job.status)

  return (
    <div className="min-h-screen mesh-gradient">
      {/* ─── Top bar ─── */}
      <header className="sticky top-0 z-30 h-14 border-b border-slate-200/50 bg-white/60 backdrop-blur-xl flex items-center px-6 gap-4">
        <Link href="/dashboard" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600 transition-colors font-medium">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Dashboard
        </Link>
        <div className="flex-1" />
        {isPolling && (
          <span className="flex items-center gap-1.5 text-xs text-brand-600">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse-dot" />
            Live updating
          </span>
        )}
        <button
          onClick={loadJob}
          className="text-xs text-slate-500 hover:text-brand-600 transition-colors"
        >
          Refresh
        </button>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10 animate-fade-in space-y-6">
        {/* ─── Title card ─── */}
        <div className="glass-card rounded-2xl p-6 shadow-lg shadow-slate-200/40">
          <div className="flex flex-col sm:flex-row sm:items-start gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight leading-tight break-words">
                {job.topic}
              </h1>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500">
                {job.created_at && (
                  <span className="flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {new Date(job.created_at).toLocaleString()}
                  </span>
                )}
                {job.completed_at && (
                  <span className="flex items-center gap-1">
                    <svg className="w-3.5 h-3.5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {new Date(job.completed_at).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
            <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-semibold ${s.bg} ${s.text} flex-shrink-0`}>
              <span className={`w-2 h-2 rounded-full ${s.dot} ${isActive ? 'animate-pulse-dot' : ''}`} />
              {s.label}
            </div>
          </div>
        </div>

        {/* ─── Pipeline timeline ─── */}
        {isActive && (
          <div className="glass-card rounded-2xl p-5">
            <StepTimeline current={job.status} />
          </div>
        )}

        {/* ─── Progress details ─── */}
        {job.progress && Object.keys(job.progress).length > 0 && (
          <div className="glass-card rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Progress Details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2">
              {Object.entries(job.progress).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center py-2 border-b border-slate-100 last:border-0">
                  <span className="text-sm text-slate-600 font-medium">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm text-slate-800 font-semibold">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ─── Error state ─── */}
        {job.error && (
          <div className="rounded-2xl p-5 bg-red-50/80 border border-red-200 flex items-start gap-3">
            <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-semibold text-red-700 text-sm">Research failed</p>
              <p className="text-sm text-red-600 mt-0.5">{job.error}</p>
            </div>
          </div>
        )}

        {/* ─── Waiting state ─── */}
        {!finalPaper && isActive && (
          <div className="glass-card rounded-2xl p-10 text-center">
            <div className="w-14 h-14 mx-auto rounded-2xl bg-brand-50 flex items-center justify-center mb-4">
              <svg className="w-7 h-7 text-brand-500 animate-spin-slow" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            </div>
            <p className="text-slate-700 font-semibold">Research in progress</p>
            <p className="text-sm text-slate-500 mt-1">Our AI agents are working on your paper. This page updates automatically.</p>
          </div>
        )}

        {/* ─── Paper content ─── */}
        {finalPaper && (
          <div className="glass-card rounded-2xl shadow-lg shadow-slate-200/40 overflow-hidden">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center gap-2 px-6 py-4 border-b border-slate-100 bg-white/60">
              <h2 className="text-lg font-bold text-slate-900 mr-auto">Research Paper</h2>
              <button onClick={copyMarkdown} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all active:scale-[0.97]">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
              <button onClick={downloadMarkdown} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-sm text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all active:scale-[0.97]">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                .md
              </button>
              <button onClick={downloadPDF} className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-brand-600 to-purple-600 text-white text-sm font-semibold hover:from-brand-700 hover:to-purple-700 shadow-md shadow-brand-500/20 transition-all active:scale-[0.97]">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                PDF
              </button>
            </div>

            {/* Rendered markdown */}
            <div className="px-6 sm:px-10 py-8">
              <div className="prose prose-slate prose-sm sm:prose-base max-w-none">
                <ReactMarkdown>{finalPaper}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
