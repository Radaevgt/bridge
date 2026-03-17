import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { io } from 'socket.io-client';
import { getMyChats, getChatMessages, sendChatMessage, markChatRead } from '../../api/chats';
import useAuthStore from '../../store/authStore';
import LessonPlanPanel from '../../components/LessonPlanPanel';

export default function ChatRoom() {
  const { roomId } = useParams();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [showLessonPanel, setShowLessonPanel] = useState(false);
  const messagesEndRef = useRef(null);

  const { data, isLoading } = useQuery({
    queryKey: ['messages', roomId],
    queryFn: () => getChatMessages(roomId),
  });

  const { data: chatsData } = useQuery({
    queryKey: ['chats'],
    queryFn: getMyChats,
  });

  const currentRoom = (chatsData?.data || []).find((r) => r.id === roomId);
  const otherParticipant = currentRoom
    ? user?.id === currentRoom.client_id
      ? currentRoom.specialist
      : currentRoom.client
    : null;

  const isSpecialist = user?.role === 'specialist';

  // Load history + mark read via REST as fallback
  useEffect(() => {
    if (data?.data) {
      setMessages(data.data);
      markChatRead(roomId).then(() => {
        queryClient.invalidateQueries({ queryKey: ['chats'] });
      }).catch(() => {});
    }
  }, [data, roomId, queryClient]);

  // Socket connection
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token || !roomId) return;

    const s = io(import.meta.env.VITE_WS_URL || 'http://localhost:8000', {
      auth: { token },
      query: { token },
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    s.on('connect', () => {
      setConnected(true);
      s.emit('join_room', { room_id: roomId });
      s.emit('mark_read', { room_id: roomId });
      queryClient.invalidateQueries({ queryKey: ['chats'] });
    });

    s.on('disconnect', () => {
      setConnected(false);
    });

    s.on('connect_error', () => {
      setConnected(false);
    });

    s.on('message_received', (msg) => {
      setMessages((prev) => {
        const optimisticIdx = prev.findIndex(
          (m) =>
            m._isOptimistic &&
            m.sender_id === msg.sender_id &&
            m.content === msg.content
        );
        if (optimisticIdx !== -1) {
          const updated = [...prev];
          updated[optimisticIdx] = msg;
          return updated;
        }
        return [...prev, msg];
      });
      // Mark as read if the message is from someone else
      if (msg.sender_id !== user?.id) {
        s.emit('mark_read', { room_id: roomId });
        queryClient.invalidateQueries({ queryKey: ['chats'] });
      }
    });

    setSocket(s);
    return () => s.disconnect();
  }, [roomId]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(
    async (e) => {
      e.preventDefault();
      if (!newMessage.trim()) return;

      const content = newMessage.trim();
      setNewMessage('');

      // Optimistic update
      const optimisticMsg = {
        id: `temp_${Date.now()}`,
        room_id: roomId,
        sender_id: user?.id,
        content,
        is_read: false,
        created_at: new Date().toISOString(),
        _isOptimistic: true,
      };
      setMessages((prev) => [...prev, optimisticMsg]);

      // Try WebSocket first, fall back to REST
      if (socket?.connected) {
        socket.emit('send_message', { room_id: roomId, content });
      } else {
        try {
          const { data: saved } = await sendChatMessage(roomId, content);
          setMessages((prev) =>
            prev.map((m) => (m.id === optimisticMsg.id ? saved : m))
          );
        } catch {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === optimisticMsg.id ? { ...m, _failed: true } : m
            )
          );
        }
      }
    },
    [newMessage, roomId, socket, user?.id]
  );

  return (
    <div className="max-w-5xl mx-auto px-6 py-4 h-[calc(100vh-64px)] flex gap-4">
      {/* Chat column */}
      <div className={`flex flex-col ${showLessonPanel ? 'w-1/2' : 'w-full max-w-3xl mx-auto'} transition-all`}>
        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-border">
          <Link
            to="/chats"
            className="text-text-secondary hover:text-primary text-sm"
          >
            &larr; Back
          </Link>
          {otherParticipant?.avatar_url ? (
            <img
              src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${otherParticipant.avatar_url}`}
              alt={otherParticipant.full_name}
              className="w-8 h-8 rounded-full object-cover"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-primary-light text-primary flex items-center justify-center text-xs font-bold">
              {otherParticipant?.full_name?.charAt(0) || '?'}
            </div>
          )}
          <h1 className="text-lg font-semibold text-primary-dark">
            {otherParticipant?.full_name || 'Chat'}
          </h1>

          <div className="flex items-center gap-2 ml-auto">
            {!connected && (
              <span className="text-xs text-text-secondary">
                Reconnecting...
              </span>
            )}
            {isSpecialist && (
              <button
                onClick={() => setShowLessonPanel(!showLessonPanel)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  showLessonPanel
                    ? 'bg-primary text-white'
                    : 'bg-primary-light text-primary hover:bg-primary hover:text-white'
                }`}
              >
                ✨ Lesson Plan
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto py-4 space-y-3">
          {isLoading ? (
            <div className="text-center text-text-secondary text-sm py-8">
              Loading messages...
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center text-text-secondary text-sm py-8">
              No messages yet. Say hello!
            </div>
          ) : (
            messages.map((msg, i) => {
              const isMine = msg.sender_id === user?.id;
              return (
                <div
                  key={msg.id || i}
                  className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] px-4 py-2.5 rounded-2xl text-sm ${
                      isMine
                        ? 'bg-primary text-white rounded-br-md'
                        : 'bg-gray-100 text-text-primary rounded-bl-md'
                    } ${msg._failed ? 'opacity-50' : ''}`}
                  >
                    <p>{msg.content}</p>
                    <p
                      className={`text-xs mt-1 ${isMine ? 'text-white/70' : 'text-text-secondary'}`}
                    >
                      {msg._failed
                        ? 'Failed to send'
                        : new Date(msg.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                    </p>
                  </div>
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={sendMessage}
          className="flex items-center gap-3 pt-4 border-t border-border"
        >
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 border border-border rounded-xl px-4 py-2.5 text-sm text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            disabled={!newMessage.trim()}
            className="bg-primary text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>

      {/* Lesson Plan Panel */}
      {showLessonPanel && (
        <div className="w-1/2 overflow-y-auto">
          <LessonPlanPanel
            roomId={roomId}
            requestId={null}
            onClose={() => setShowLessonPanel(false)}
          />
        </div>
      )}
    </div>
  );
}
