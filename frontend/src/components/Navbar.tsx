/**
 * Navbar Component
 *
 * Main navigation bar with authentication-aware links
 */

import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context'

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and primary nav */}
          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-300 via-primary-500 to-fuchsia-500 text-base font-semibold text-slate-950 shadow-lg shadow-primary-500/40">
                P
              </span>
              <span className="text-lg font-semibold text-white">Portfolio Drive</span>
            </Link>
            <div className="hidden items-center gap-4 sm:flex">
              <Link
                to="/"
                className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
              >
                Home
              </Link>
              <Link
                to="/enterprise-portfolio"
                className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
              >
                Portfolio Showcase
              </Link>
              {isAuthenticated && (
                <>
                  <Link
                    to="/dashboard"
                    className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/photos"
                    className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
                  >
                    Photos
                  </Link>
                  <Link
                    to="/operations"
                    className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
                  >
                    Operations
                  </Link>
                  <Link
                    to="/security-simulators"
                    className="inline-flex items-center rounded-lg px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 hover:text-white"
                  >
                    Security Sims
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Right side - auth buttons */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <span className="hidden text-sm text-slate-200 sm:inline">{user?.email}</span>
                <button
                  onClick={handleLogout}
                  className="rounded-lg border border-white/20 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-primary-300 hover:text-white"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-semibold text-slate-200 transition hover:text-white"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="rounded-lg bg-gradient-to-r from-primary-300 via-primary-500 to-fuchsia-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-lg shadow-primary-500/40 transition hover:from-primary-200 hover:via-primary-400 hover:to-fuchsia-400"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
