export default function ChatWindow({ roomId }) {
  return (
    <div className="flex flex-col h-full bg-white border border-border rounded-lg">
      <div className="p-4 border-b border-border">
        <h3 className="text-lg font-semibold text-primary-dark">Chat</h3>
      </div>
      <div className="flex-1 p-4 overflow-y-auto" />
      <div className="p-4 border-t border-border">
        <input
          type="text"
          placeholder="Type a message..."
          className="w-full border border-border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
        />
      </div>
    </div>
  );
}
