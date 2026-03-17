import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getMyChats } from '../../api/chats';
import useAuthStore from '../../store/authStore';

export default function Dashboard() {
  const { user } = useAuthStore();

  const { data: chatsData, isLoading } = useQuery({
    queryKey: ['chats'],
    queryFn: getMyChats,
  });

  const rooms = chatsData?.data || [];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-primary-dark">
          Welcome, {user?.full_name || 'Client'}
        </h1>
        <p className="text-text-secondary mt-1">
          Find and connect with the right experts for your needs.
        </p>
      </div>

      {/* Primary CTA */}
      <Link
        to="/requests/create"
        className="block bg-primary text-white rounded-xl p-6 hover:bg-primary-dark transition-colors mb-6"
      >
        <div className="flex items-center gap-4">
          <div className="text-3xl">{'\uD83D\uDCDD'}</div>
          <div>
            <h3 className="text-lg font-semibold">Create a New Task</h3>
            <p className="text-sm text-white/80 mt-1">
              Describe what you need and get matched with the right specialist
            </p>
          </div>
        </div>
      </Link>

      {/* Secondary quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <Link
          to="/requests"
          className="bg-white border border-border rounded-xl p-5 hover:border-primary/30 hover:shadow-sm transition-all"
        >
          <div className="text-2xl mb-2">{'\uD83D\uDCCB'}</div>
          <h3 className="text-sm font-semibold text-primary-dark">
            My Requests
          </h3>
          <p className="text-xs text-text-secondary mt-1">
            View your task requests
          </p>
        </Link>
        <Link
          to="/chats"
          className="bg-white border border-border rounded-xl p-5 hover:border-primary/30 hover:shadow-sm transition-all"
        >
          <div className="text-2xl mb-2">{'\uD83D\uDCAC'}</div>
          <h3 className="text-sm font-semibold text-primary-dark">Messages</h3>
          <p className="text-xs text-text-secondary mt-1">
            {rooms.length} conversation{rooms.length !== 1 ? 's' : ''}
          </p>
        </Link>
        <Link
          to="/search"
          className="bg-white border border-border rounded-xl p-5 hover:border-primary/30 hover:shadow-sm transition-all"
        >
          <div className="text-2xl mb-2">{'\uD83D\uDD0D'}</div>
          <h3 className="text-sm font-semibold text-primary-dark">
            Browse Specialists
          </h3>
          <p className="text-xs text-text-secondary mt-1">
            Search the directory
          </p>
        </Link>
      </div>

      {/* Recent chats */}
      <div className="bg-white border border-border rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-primary-dark">
            Recent Conversations
          </h2>
          <Link to="/chats" className="text-sm text-primary hover:underline">
            View all
          </Link>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="h-12 bg-gray-100 rounded-lg animate-pulse"
              />
            ))}
          </div>
        ) : rooms.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-text-secondary text-sm mb-3">
              No conversations yet
            </p>
            <Link
              to="/requests/create"
              className="text-primary text-sm font-medium hover:underline"
            >
              Create a task to connect with specialists
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {rooms.slice(0, 5).map((room) => {
              const other =
                user?.id === room.client_id ? room.specialist : room.client;
              return (
                <Link
                  key={room.id}
                  to={`/chats/${room.id}`}
                  className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  {other?.avatar_url ? (
                    <img
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${other.avatar_url}`}
                      alt={other.full_name}
                      className="w-9 h-9 rounded-full object-cover flex-shrink-0"
                    />
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-primary-light text-primary flex items-center justify-center text-xs font-bold flex-shrink-0">
                      {other?.full_name?.charAt(0) || '?'}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {other?.full_name}
                    </p>
                    <p className="text-xs text-text-secondary truncate">
                      {room.last_message?.content || 'No messages'}
                    </p>
                  </div>
                  {room.unread_count > 0 && (
                    <span className="bg-primary text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                      {room.unread_count}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
