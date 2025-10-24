import { FormEvent, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

const Login = () => {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    try {
      const response = await api.post('/auth/login', { email, password })
      login(response.data.access_token, response.data.refresh_token)
      const redirect = (location.state as { from?: Location })?.from?.pathname || '/dashboard'
      navigate(redirect, { replace: true })
    } catch (err) {
      setError('Invalid credentials. Please try again.')
    }
  }

  return (
    <div className="mx-auto max-w-md rounded-lg border border-slate-200 bg-white p-6 shadow">
      <h2 className="text-2xl font-semibold text-slate-900">Welcome back</h2>
      <p className="mt-2 text-sm text-slate-600">Sign in to manage your portfolio content.</p>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button type="submit" className="w-full rounded bg-primary px-4 py-2 font-semibold text-white">
          Login
        </button>
      </form>
    </div>
  )
}

export default Login
