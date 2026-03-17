import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getMyChats } from '../../api/chats';
import useAuthStore from '../../store/authStore';

export default function Chats() {
  const { user } = useAuthStore();

  const { data, isLoading } = useQuery({
    queryKey: ['chats'],
    queryFn: getMyChats,
  });

  const rooms = data?.data || [];

  const getOtherParticipant = (room) => {
    if (user?.id === room.client_id) return room.specialist;
    return room.client;
  };

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-primary-dark mb-6">Messages</h1>
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white border border-border rounded-xl p-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-200" />
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                  <div className="h-3 bg-gray-200 rounded w-2/3" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold text-primary-dark mb-6">Messages</h1>

      {rooms.length === 0 ? (
        <div className="text-center py-16">
          <div className="text-4xl mb-3">&#128172;</div>
          <h3 className="text-lg font-semibold text-primary-dark mb-1">No conversations yet</h3>
          <p className="text-text-secondary text-sm mb-4">Start a conversation by messaging a specialist.</p>
          <Link to="/search" className="text-primary font-medium hover:underline">Browse Specialists</Link>
        </div>
      ) : (
        <div className="space-y-2">
          {rooms.map((room) => {
            const other = getOtherParticipant(room);
            return (
              <Link
                key={room.id}
                to={`/chats/${room.id}`}
                className="flex items-center gap-3 bg-white border border-border rounded-xl p-4 hover:border-primary/30 hover:shadow-sm transition-all"
              >
                {other?.avatar_url ? (
                  <img
                    src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${other.avatar_url}`}
                    alt={other.full_name}
                    className="w-10 h-10 rounded-full object-cover flex-shrink-0"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-primary-light text-primary flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {other?.full_name?.charAt(0) || '?'}
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-primary-dark truncate">{other?.full_name || 'User'}</h3>
                    {room.last_message && (
                      <span className="text-xs text-text-secondary flex-shrink-0">
                        {new Date(room.last_message.created_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-text-secondary truncate mt-0.5">
                    {room.last_message?.content || 'No messages yet'}
                  </p>
                </div>
                {room.unread_count > 0 && (
                  <span className="bg-primary text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0">
                    {room.unread_count}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
