import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getTaskRequests } from '../../api/requests';
import useAuthStore from '../../store/authStore';
import RequestCard from '../../components/RequestCard';

export default function Requests() {
  const { user } = useAuthStore();
  const isClient = user?.role === 'client';

  const { data, isLoading, isError } = useQuery({
    queryKey: ['taskRequests'],
    queryFn: () => getTaskRequests(),
  });

  const requests = data?.data || [];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-primary-dark">
            {isClient ? 'My Requests' : 'Available Requests'}
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            {isClient
              ? 'Track your task requests and view proposals from specialists.'
              : 'Browse open requests matching your expertise and submit proposals.'}
          </p>
        </div>
        {isClient && (
          <Link
            to="/requests/create"
            className="bg-primary text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors flex-shrink-0"
          >
            New Request
          </Link>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="h-32 bg-white border border-border rounded-xl animate-pulse"
            />
          ))}
        </div>
      ) : isError ? (
        <div className="bg-white border border-border rounded-xl p-12 text-center">
          <p className="text-text-secondary text-sm mb-2">Failed to load requests.</p>
          <p className="text-text-secondary text-xs">
            Please check your connection and try refreshing the page.
          </p>
        </div>
      ) : requests.length === 0 ? (
        <div className="bg-white border border-border rounded-xl p-12 text-center">
          <div className="text-4xl mb-3">{isClient ? '\uD83D\uDCDD' : '\uD83D\uDD0D'}</div>
          <p className="text-text-primary font-medium mb-2">
            {isClient ? 'No requests yet' : 'No matching requests'}
          </p>
          <p className="text-text-secondary text-sm mb-4">
            {isClient
              ? 'Create your first task request to find the right specialist.'
              : 'No open requests match your profile domains. Check back later or update your domains.'}
          </p>
          {isClient ? (
            <Link
              to="/requests/create"
              className="inline-block bg-primary text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors"
            >
              Create Request
            </Link>
          ) : (
            <Link
              to="/dashboard/specialist"
              className="inline-block text-primary text-sm font-medium hover:underline"
            >
              Update your profile domains
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {requests.map((req) => (
            <RequestCard key={req.id} request={req} />
          ))}
        </div>
      )}
    </div>
  );
}
