import { FormEvent, useEffect, useState } from 'react'
import ContentCard from '../components/ContentCard'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

interface Content {
  id: string
  title: string
  body?: string
  is_published: boolean
}

const Dashboard = () => {
  const [content, setContent] = useState<Content[]>([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const { logout } = useAuth()

  const headers = {
    Authorization: `Bearer ${localStorage.getItem('accessToken')}`
  }

  const loadContent = async () => {
    const response = await api.get<Content[]>('/content/', { headers })
    setContent(response.data)
  }

  useEffect(() => {
    loadContent().catch(() => logout())
  }, [])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    await api.post(
      '/content/',
      { title, body, is_published: isPublished },
      { headers }
    )
    setTitle('')
    setBody('')
    setIsPublished(false)
    await loadContent()
  }

  const handleDelete = async (id: string) => {
    await api.delete(`/content/${id}`, { headers })
    await loadContent()
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4 rounded border border-slate-200 bg-white p-4 shadow">
        <h2 className="text-xl font-semibold text-slate-900">Create Content</h2>
        <div>
          <label className="block text-sm font-medium text-slate-700">Title</label>
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Body</label>
          <textarea
            value={body}
            onChange={(event) => setBody(event.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2"
            rows={4}
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" checked={isPublished} onChange={(event) => setIsPublished(event.target.checked)} />
          Publish immediately
        </label>
        <button type="submit" className="rounded bg-primary px-4 py-2 font-semibold text-white">
          Save
        </button>
      </form>

      <div className="grid gap-4 md:grid-cols-2">
        {content.map((item) => (
          <ContentCard
            key={item.id}
            title={item.title}
            body={item.body}
            isPublished={item.is_published}
            onDelete={() => handleDelete(item.id)}
          />
        ))}
        {content.length === 0 && <p className="text-slate-500">No content yet. Create your first entry.</p>}
      </div>
    </div>
  )
}

export default Dashboard
