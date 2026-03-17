import { Link } from 'react-router-dom';

const urgencyConfig = {
  low: { label: 'Low', className: 'bg-gray-100 text-text-secondary' },
  medium: { label: 'Medium', className: 'bg-blue-50 text-primary' },
  high: { label: 'High', className: 'bg-yellow-50 text-yellow-600' },
  urgent: { label: 'Urgent', className: 'bg-red-50 text-error' },
};

const statusConfig = {
  open: { label: 'Open', className: 'bg-green-50 text-success' },
  in_progress: { label: 'In Progress', className: 'bg-blue-50 text-primary' },
  closed: { label: 'Closed', className: 'bg-gray-100 text-text-secondary' },
};

export default function RequestCard({ request }) {
  const urgency = urgencyConfig[request?.urgency] || urgencyConfig.medium;
  const reqStatus = statusConfig[request?.status] || statusConfig.open;

  return (
    <Link
      to={`/requests/${request?.id}`}
      className="block bg-white border border-border rounded-xl p-5 hover:shadow-md hover:border-primary/30 transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="bg-primary-light text-primary text-xs font-medium px-2.5 py-0.5 rounded">
              {request?.domain}
            </span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${urgency.className}`}>
              {urgency.label}
            </span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${reqStatus.className}`}>
              {reqStatus.label}
            </span>
          </div>
          {request?.comment && (
            <p className="text-sm text-text-primary mt-2 line-clamp-2">{request.comment}</p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mt-4 pt-3 border-t border-border">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-full bg-primary-light text-primary flex items-center justify-center text-xs font-bold">
            {request?.client?.full_name?.charAt(0) || '?'}
          </div>
          <span className="text-sm text-text-secondary">{request?.client?.full_name}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-text-secondary">
          {(request?.budget_min != null || request?.budget_max != null) && (
            <span>
              ${request.budget_min || 0}-${request.budget_max || 'Any'}/hr
            </span>
          )}
          <span>
            {request?.proposal_count || 0} proposal{request?.proposal_count !== 1 ? 's' : ''}
          </span>
          <span>{new Date(request?.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    </Link>
  );
}
