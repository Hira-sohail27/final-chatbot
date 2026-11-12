export default function Message({ m }) {
  const mine = m.role === 'user';
  return (
    <div className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] whitespace-pre-wrap break-words rounded-2xl px-4 py-2 md:max-w-[70%] ${mine ? 'bg-indigo-600 text-white' : 'bg-white text-gray-900 shadow'}`}>
        {m.content}
        {m.sources?.length > 0 && (
          <p className="mt-2 border-t pt-1 text-xs text-gray-500">Sources: {m.sources.map((s) => `${s.source}#${s.chunk_id}`).join(', ')}</p>
        )}
      </div>
    </div>
  );
}
