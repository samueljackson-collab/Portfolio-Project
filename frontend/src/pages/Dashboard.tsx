import { FormEvent, useEffect, useState } from 'react';
import api from '../api/client';
import ContentCard from '../components/ContentCard';

export type Content = {
  id: string;
  title: string;
  body: string;
  is_published: boolean;
};

const defaultFormState = { title: '', body: '', is_published: false };

function Dashboard() {
  const [items, setItems] = useState<Content[]>([]);
  const [formState, setFormState] = useState(defaultFormState);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadContent = async () => {
    // Load data from the API and keep a friendly message handy on failure.
    try {
      const response = await api.get<Content[]>('/content/');
      setItems(response.data);
    } catch (err) {
      setError('Failed to load content');
    }
  };

  useEffect(() => {
    loadContent();
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await api.put(`/content/${editingId}`, formState);
      } else {
        await api.post('/content/', formState);
      }
      setFormState(defaultFormState);
      setEditingId(null);
      loadContent();
    } catch (err) {
      setError('Unable to save content');
    }
  };

  const handleEdit = (content: Content) => {
    // Switch the form into update mode for the selected record.
    setEditingId(content.id);
    setFormState({ title: content.title, body: content.body, is_published: content.is_published });
  };

  const handleDelete = async (content: Content) => {
    // Delete the record and refresh so the grid reflects the change.
    await api.delete(`/content/${content.id}`);
    loadContent();
  };

  return (
    <section className="space-y-6">
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold text-secondary">Content Dashboard</h2>
        <p className="text-sm text-gray-600">Manage portfolio case studies and showcase entries.</p>
      </header>
      <form onSubmit={handleSubmit} className="bg-white shadow rounded p-4 space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium text-gray-700">
            Title
            <input
              className="mt-1 w-full border rounded px-3 py-2"
              value={formState.title}
              onChange={(event) => setFormState({ ...formState, title: event.target.value })}
              required
            />
          </label>
          <label className="text-sm font-medium text-gray-700">
            Published
            <input
              type="checkbox"
              className="ml-2"
              checked={formState.is_published}
              onChange={(event) => setFormState({ ...formState, is_published: event.target.checked })}
            />
          </label>
        </div>
        <label className="text-sm font-medium text-gray-700">
          Body
          <textarea
            className="mt-1 w-full border rounded px-3 py-2"
            rows={4}
            value={formState.body}
            onChange={(event) => setFormState({ ...formState, body: event.target.value })}
          />
        </label>
        {error && <p className="text-sm text-red-500">{error}</p>}
        <button type="submit" className="bg-primary text-white px-4 py-2 rounded">
          {editingId ? 'Update content' : 'Create content'}
        </button>
      </form>
      <div className="grid gap-4 md:grid-cols-2">
        {items.map((item) => (
          <ContentCard key={item.id} content={item} onEdit={handleEdit} onDelete={handleDelete} />
        ))}
        {items.length === 0 && <p className="text-sm text-gray-500">No content yet. Create your first entry above.</p>}
      </div>
    </section>
  );
}

export default Dashboard;
