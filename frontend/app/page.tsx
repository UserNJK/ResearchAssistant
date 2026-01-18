'use client'

import { useEffect } from 'react'
import { useAuth } from './context/AuthContext'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const { token } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (token) {
      router.push('/dashboard')
    } else {
      router.push('/auth')
    }
  }, [token, router])

  return null
}
