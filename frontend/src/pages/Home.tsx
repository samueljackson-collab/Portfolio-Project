import { useEffect, useState } from 'react'
import ContentCard from '../components/ContentCard'
import api from '../api/client'

interface Content {
  id: string
  title: string
  body?: string
  is_published: boolean
}

const Home = () => {
  const [content, setContent] = useState<Content[]>([])

  useEffect(() => {
    api
      .get<Content[]>('/content/', {
        headers: localStorage.getItem('accessToken')
          ? { Authorization: `Bearer ${localStorage.getItem('accessToken')}` }
          : undefined
      })
      .then((response) => setContent(response.data))
      .catch(() => setContent([]))
  }, [])

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Samuel Jackson · Systems Development Engineer</h1>
        <p className="text-slate-600">
          Building secure, scalable systems with a relentless focus on reliability and business impact.
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        {content.map((item) => (
          <ContentCard
            key={item.id}
            title={item.title}
            body={item.body}
            isPublished={item.is_published}
          />
        ))}
        {content.length === 0 && (
          <div className="rounded border border-dashed border-slate-300 p-6 text-center text-slate-500">
            Authenticate to view your personalized portfolio feed.
          </div>
        )}
      </div>
    </section>
  )
}

export default Home
