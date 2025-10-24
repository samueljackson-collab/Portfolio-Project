interface Props {
  title: string
  body?: string
  isPublished: boolean
  onEdit?: () => void
  onDelete?: () => void
}

const ContentCard = ({ title, body, isPublished, onEdit, onDelete }: Props) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
    <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
    {body && <p className="mt-2 text-sm text-slate-600">{body}</p>}
    <div className="mt-4 flex items-center justify-between text-sm">
      <span className={isPublished ? 'text-green-600' : 'text-amber-600'}>
        {isPublished ? 'Published' : 'Draft'}
      </span>
      <div className="flex gap-2">
        {onEdit && (
          <button onClick={onEdit} className="text-primary hover:underline">
            Edit
          </button>
        )}
        {onDelete && (
          <button onClick={onDelete} className="text-rose-600 hover:underline">
            Delete
          </button>
        )}
      </div>
    </div>
  </div>
)

export default ContentCard
