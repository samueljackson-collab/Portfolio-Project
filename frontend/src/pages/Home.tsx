/**
 * Home Page
 *
 * Landing page with public content display
 */

import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { contentService, type Content } from '../api'
import { ContentCard } from '../components'

export const Home: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [metrics, setMetrics] = useState({
    total: 0,
    published: 0,
    drafts: 0,
  })

  const publishedCount = metrics.published
  const draftCount = metrics.drafts
  const highlightedContents = contents.slice(0, 3)

  useEffect(() => {
    const fetchContents = async () => {
      try {
        setIsLoading(true)
        const data = await contentService.getAll(0, 10)
        const publishedItems = data.filter(item => item.is_published)
        setContents(publishedItems)
        setMetrics({
          total: data.length,
          published: publishedItems.length,
          drafts: Math.max(data.length - publishedItems.length, 0),
        })
      } catch (err) {
        setError('Failed to load content')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchContents()
  }, [])

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-50">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-10 top-0 h-64 w-64 rounded-full bg-primary-500/20 blur-3xl"></div>
        <div className="absolute right-20 top-20 h-72 w-72 rounded-full bg-fuchsia-500/10 blur-3xl"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.04),transparent_35%)]"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        {/* Hero Section */}
        <section className="pt-16 lg:pt-20 grid gap-12 lg:grid-cols-[1.1fr_0.9fr] items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary-100 shadow-lg">
              AI Studio-inspired workspace
            </div>
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl font-bold leading-tight text-white">
                Launch a drive-like portfolio experience
              </h1>
              <p className="text-lg text-slate-200/80 max-w-2xl">
                Build and review your published work in a clean, glassmorphic shell with gradient accents inspired by the requested AI Studio reference.
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary-300 via-primary-500 to-fuchsia-500 px-6 py-3 text-base font-semibold text-slate-950 shadow-2xl shadow-primary-500/40 transition hover:translate-y-[-2px] hover:shadow-primary-400/50"
              >
                Launch workspace
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 px-6 py-3 text-base font-semibold text-slate-100 transition hover:border-primary-300 hover:text-white"
              >
                Sign in to manage
              </Link>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Published</p>
                <p className="mt-2 text-3xl font-semibold text-white">{publishedCount}</p>
                <p className="text-xs text-slate-400">Live to your audience</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Drafts</p>
                <p className="mt-2 text-3xl font-semibold text-white">{draftCount}</p>
                <p className="text-xs text-slate-400">Ready for polish</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Workspace</p>
                <p className="mt-2 text-3xl font-semibold text-white">{metrics.total}</p>
                <p className="text-xs text-slate-400">Items curated</p>
              </div>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-2xl">
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary-500/15 via-transparent to-fuchsia-500/10" />
            <div className="relative space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-primary-100/80">Live preview</p>
                  <h2 className="text-2xl font-semibold text-white">Workspace stream</h2>
                </div>
                <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-100">
                  Synced
                </span>
              </div>

              {isLoading && (
                <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <div className="h-3 w-3 animate-ping rounded-full bg-primary-300"></div>
                  <p className="text-sm text-slate-200">Retrieving your portfolio feed...</p>
                </div>
              )}

              {!isLoading && highlightedContents.length === 0 && (
                <div className="rounded-2xl border border-dashed border-white/20 bg-white/5 px-4 py-6 text-center">
                  <p className="text-sm text-slate-300">No published items yet — your workspace will populate here.</p>
                </div>
              )}

              {!isLoading && highlightedContents.length > 0 && (
                <div className="space-y-3">
                  {highlightedContents.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 transition hover:border-primary-300/60"
                    >
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-white line-clamp-1">{item.title}</p>
                        <p className="text-xs text-slate-300 line-clamp-1">
                          {item.body ?? 'No description provided yet.'}
                        </p>
                      </div>
                      <span
                        className="inline-flex shrink-0 items-center gap-2 rounded-full border border-primary-400/30 bg-primary-400/10 px-3 py-1 text-xs font-semibold text-primary-100"
                        aria-label="Published item"
                      >
                        <span className="h-2 w-2 rounded-full bg-primary-300" />
                        Published
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-4">
                <div className="flex items-center justify-between text-sm text-slate-200">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-300" />
                    Published entries
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-amber-300" />
                    Draft-ready ideas
                  </span>
                </div>
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10">
                  <div
                    className="h-full bg-gradient-to-r from-primary-400 via-primary-500 to-fuchsia-500"
                    style={{ width: `${metrics.total ? (publishedCount / metrics.total) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Content Section */}
        <section className="mt-14 space-y-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-primary-100/80">Content feed</p>
              <h2 className="text-3xl font-bold text-white">Latest content</h2>
              <p className="text-slate-300">Review your curated items in a drive-like grid.</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <button type="button" className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300 transition hover:bg-white/20 hover:text-white">Grid</button>
              <button type="button" className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300 transition hover:bg-white/20 hover:text-white">Cards</button>
            </div>
          </div>

          {isLoading && (
            <div className="flex justify-center py-12">
              <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-primary-300"></div>
            </div>
          )}

          {error && (
            <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-100">
              {error}
            </div>
          )}

          {!isLoading && !error && contents.length === 0 && (
            <div className="rounded-2xl border border-dashed border-white/20 bg-white/5 px-6 py-10 text-center">
              <p className="text-lg text-slate-200">
                No content available yet. Be the first to create some!
              </p>
            </div>
          )}

          {!isLoading && !error && contents.length > 0 && (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {contents.map((content) => (
                <ContentCard key={content.id} content={content} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
