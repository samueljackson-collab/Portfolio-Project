import { PropsWithChildren } from 'react'

function Layout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="border-b border-slate-700 bg-slate-800 py-4">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4">
          <h1 className="text-xl font-bold">Portfolio Platform</h1>
          <span className="text-xs uppercase tracking-wide text-slate-400">Demo Stack</span>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">{children}</main>
      <footer className="border-t border-slate-700 bg-slate-800 py-4 text-center text-xs text-slate-400">
        © {new Date().getFullYear()} Portfolio Monorepo
      </footer>
    </div>
  )
}

export default Layout
