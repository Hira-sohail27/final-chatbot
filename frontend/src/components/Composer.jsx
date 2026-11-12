import { useState } from 'react';

export default function Composer({ onSend, disabled }) {
  const [text, setText] = useState('');
  const submit = () => {
    const t = text.trim();
    if (!t || disabled) return;
    onSend(t);
    setText('');
  };
  return (
    <div className="flex gap-2 border-t bg-white p-3">
      <textarea rows={1} value={text} maxLength={4000} onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }}
        placeholder="Type a message (Enter to send, Shift+Enter for new line)"
        className="max-h-40 flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none" />
      <button onClick={submit} disabled={disabled || !text.trim()}
        className="rounded-lg bg-indigo-600 px-4 font-medium text-white hover:bg-indigo-700 disabled:opacity-50">Send</button>
    </div>
  );
}
