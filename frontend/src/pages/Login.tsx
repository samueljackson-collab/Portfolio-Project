import { FormEvent, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await login(email, password);
      const redirectTo = (location.state as { from?: Location })?.from?.pathname || '/dashboard';
      navigate(redirectTo);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  const handleRegister = async () => {
    // Registration reuses the login helper so the dashboard opens automatically.
    try {
      await api.post('/auth/register', { email, password });
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Registration failed');
    }
  };

  return (
    <section className="max-w-md mx-auto bg-white shadow rounded p-6 space-y-4">
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold text-primary">Sign in</h2>
        <p className="text-sm text-gray-600">Access the portfolio content dashboard.</p>
      </header>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            className="mt-1 w-full border rounded px-3 py-2"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            className="mt-1 w-full border rounded px-3 py-2"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex items-center justify-between">
          <button type="submit" className="bg-primary text-white px-4 py-2 rounded">
            Login
          </button>
          <button type="button" onClick={handleRegister} className="text-sm text-primary">
            Register instead
          </button>
        </div>
      </form>
    </section>
  );
}

export default Login;
