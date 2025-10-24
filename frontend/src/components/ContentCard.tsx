import { Content } from '../pages/Dashboard';

type Props = {
  content: Content;
  onEdit?: (content: Content) => void;
  onDelete?: (content: Content) => void;
};

function ContentCard({ content, onEdit, onDelete }: Props) {
  // Provide small management affordances for each portfolio entry.
  return (
    <div className="bg-white rounded shadow p-4 space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-primary">{content.title}</h3>
        <span className="text-xs uppercase tracking-wide text-gray-500">
          {content.is_published ? 'Published' : 'Draft'}
        </span>
      </div>
      <p className="text-sm text-gray-700">{content.body}</p>
      <div className="flex space-x-2 text-sm">
        {onEdit && (
          <button onClick={() => onEdit(content)} className="text-blue-500">
            Edit
          </button>
        )}
        {onDelete && (
          <button onClick={() => onDelete(content)} className="text-red-500">
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

export default ContentCard;
