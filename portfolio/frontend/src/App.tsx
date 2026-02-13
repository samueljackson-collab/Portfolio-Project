import { FormEvent, useEffect, useMemo, useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { createProject, listProjects, login, Project } from './lib/api';

function LoginPage({ onAuthenticated }: { onAuthenticated: (token: string) => void }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('changeme');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const response = await login(username, password);
      onAuthenticated(response.access_token);
    } catch (err) {
      setError('Login failed. Check credentials.');
      console.error(err);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900">
      <form className="space-y-4 rounded bg-slate-800 p-8 shadow-lg" onSubmit={handleSubmit}>
        <h1 className="text-2xl font-semibold">Sign in</h1>
        {error && <p className="text-sm text-red-400">{error}</p>}
        <label className="block">
          <span className="text-sm">Username</span>
          <input
            className="mt-1 w-full rounded border border-slate-600 bg-slate-900 p-2 focus:outline-none"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
        </label>
        <label className="block">
          <span className="text-sm">Password</span>
          <input
            className="mt-1 w-full rounded border border-slate-600 bg-slate-900 p-2 focus:outline-none"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button
          type="submit"
          className="w-full rounded bg-indigo-500 px-4 py-2 font-semibold text-white hover:bg-indigo-400"
        >
          Log in
        </button>
      </form>
    </div>
  );
}

function Dashboard({ token, onLogout }: { token: string; onLogout: () => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState('Portfolio Demo');
  const [description, setDescription] = useState('Hello world project');

  const fetchProjects = useMemo(
    () => async () => {
      const results = await listProjects(token);
      setProjects(results);
    },
    [token]
  );

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await createProject(token, { title, description });
    setTitle('');
    setDescription('');
    await fetchProjects();
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6 text-slate-100">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Portfolio Projects</h1>
        <button
          className="rounded bg-slate-700 px-3 py-1 text-sm"
          onClick={onLogout}
        >
          Log out
        </button>
      </header>
      <section className="mb-8 rounded bg-slate-800 p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold">Create Project</h2>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleCreate}>
          <div className="md:col-span-1">
            <label className="block text-sm">Title</label>
            <input
              className="mt-1 w-full rounded border border-slate-600 bg-slate-900 p-2"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
            />
          </div>
          <div className="md:col-span-1">
            <label className="block text-sm">Description</label>
            <input
              className="mt-1 w-full rounded border border-slate-600 bg-slate-900 p-2"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          <div className="md:col-span-2">
            <button className="rounded bg-indigo-500 px-4 py-2 font-semibold text-white hover:bg-indigo-400">
              Create
            </button>
          </div>
        </form>
      </section>
      <section className="rounded bg-slate-800 p-6 shadow">
        <h2 className="mb-4 text-xl font-semibold">My Projects</h2>
        <ul className="space-y-3">
          {projects.map((project) => (
            <li key={project.id} className="rounded border border-slate-700 p-4">
              <h3 className="text-lg font-semibold">{project.title}</h3>
              <p className="text-sm text-slate-300">{project.description}</p>
              <p className="mt-2 text-xs text-slate-500">Updated: {new Date(project.updated_at).toLocaleString()}</p>
            </li>
          ))}
          {projects.length === 0 && <li className="text-sm text-slate-400">No projects yet.</li>}
        </ul>
      </section>
    </div>
  );
}

export default function App() {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(null);

  const handleAuthenticated = (newToken: string) => {
    setToken(newToken);
    navigate('/dashboard');
  };

  const handleLogout = () => {
    setToken(null);
    navigate('/');
  };

  return (
    <Routes>
      <Route path="/" element={<LoginPage onAuthenticated={handleAuthenticated} />} />
      <Route
        path="/dashboard"
        element={
          token ? <Dashboard token={token} onLogout={handleLogout} /> : <LoginPage onAuthenticated={handleAuthenticated} />
        }
      />
    </Routes>
  );
}
