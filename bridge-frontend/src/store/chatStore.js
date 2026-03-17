import { create } from 'zustand';

const useChatStore = create((set) => ({
  unreadCount: 0,
  activeRoomId: null,

  setUnreadCount: (count) => set({ unreadCount: count }),
  incrementUnread: () => set((state) => ({ unreadCount: state.unreadCount + 1 })),
  setActiveRoom: (roomId) => set({ activeRoomId: roomId }),
  clearActiveRoom: () => set({ activeRoomId: null }),
}));

export default useChatStore;
