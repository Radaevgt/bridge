import api from './axios';

export const getMyChats = () => api.get('/chats/');
export const getChatMessages = (roomId) => api.get(`/chats/${roomId}/messages`);
export const createChat = (specialistId) => api.post('/chats/', { specialist_id: specialistId });
export const sendChatMessage = (roomId, content) =>
  api.post(`/chats/${roomId}/messages`, { content });
export const markChatRead = (roomId) => api.patch(`/chats/${roomId}/read`);
