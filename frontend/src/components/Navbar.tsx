import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Navbar = () => {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white shadow-sm">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-xl font-semibold text-primary">
          Portfolio Platform
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-sm font-medium text-slate-700 hover:text-primary">
            Home
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-sm font-medium text-slate-700 hover:text-primary">
                Dashboard
              </Link>
              <button
                onClick={handleLogout}
                className="rounded bg-primary px-4 py-2 text-sm font-semibold text-white"
              >
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="rounded border border-primary px-4 py-2 text-sm text-primary">
              Login
            </Link>
          )}
        </div>
      </nav>
    </header>
  )
}

export default Navbar
