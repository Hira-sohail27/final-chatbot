import { useEffect, useRef } from 'react';
import Message from './Message';
import Composer from './Composer';

export default function ChatWindow({ messages, sending, failed, onSend, onRetry, onMenu }) {
  const end = useRef(null);
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, sending]);
  return (
    <main className="flex min-w-0 flex-1 flex-col bg-gray-50">
      <header className="flex items-center border-b bg-white p-3 md:hidden">
        <button onClick={onMenu} className="rounded border px-3 py-1">☰ History</button>
      </header>
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && !sending && (
          <p className="mt-20 text-center text-gray-400">Start the conversation — ask me anything about the knowledge base.</p>
        )}
        {messages.map((m) => <Message key={m.id} m={m} />)}
        {sending && <div className="w-fit animate-pulse rounded-2xl bg-white px-4 py-2 text-gray-500 shadow">Thinking…</div>}
        {failed && (
          <div className="flex items-center justify-between rounded-lg bg-red-50 p-3 text-sm text-red-700">
            <span>{failed.message}</span>
            <button onClick={onRetry} className="ml-3 rounded bg-red-600 px-3 py-1 text-white">Retry</button>
          </div>
        )}
        <div ref={end} />
      </div>
      <Composer onSend={onSend} disabled={sending} />
    </main>
  );
}
