'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'
import { authAPI, setAuthToken } from '@/utils/api'

interface AuthContextType {
  token: string | null
  user: any | null
  isLoading: boolean
  signup: (email: string) => Promise<void>
  login: (email: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<any | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const signup = useCallback(async (email: string) => {
    setIsLoading(true)
    try {
      const response = await authAPI.signup(email)
      const { access_token, user } = response.data
      setToken(access_token)
      setUser(user)
      setAuthToken(access_token)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const login = useCallback(async (email: string) => {
    setIsLoading(true)
    try {
      const response = await authAPI.login(email)
      const { access_token, user } = response.data
      setToken(access_token)
      setUser(user)
      setAuthToken(access_token)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    setAuthToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, user, isLoading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
