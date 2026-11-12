import { groupConvs } from '../groupConvs';

export default function Sidebar({ user, convs, activeId, onNew, onOpen, onRename, onDelete, onLogout, open, onClose }) {
  const groups = groupConvs(convs);
  return (
    <>
      {open && <div className="fixed inset-0 z-10 bg-black/40 md:hidden" onClick={onClose} />}
      <aside className={`fixed inset-y-0 left-0 z-20 flex w-72 flex-col bg-gray-900 text-gray-100 transition-transform md:static md:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <button onClick={onNew} className="m-3 rounded-lg border border-gray-600 px-3 py-2 text-left hover:bg-gray-800">+ New Chat</button>
        <nav className="flex-1 overflow-y-auto px-2">
          {groups.length === 0 && <p className="p-3 text-sm text-gray-400">No conversations yet. Start a new chat!</p>}
          {groups.map(([label, items]) => (
            <div key={label} className="mb-3">
              <h3 className="px-2 py-1 text-xs font-semibold uppercase text-gray-400">{label}</h3>
              {items.map((c) => (
                <div key={c.id} className={`group flex items-center rounded-lg px-2 py-2 text-sm hover:bg-gray-800 ${c.id === activeId ? 'bg-gray-800' : ''}`}>
                  <button onClick={() => onOpen(c.id)} className="min-w-0 flex-1 text-left">
                    <span className="block truncate">{c.title}</span>
                    <span className="text-xs text-gray-500">{new Date(c.last_message_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </button>
                  <button title="Rename" onClick={() => onRename(c)} className="px-1 text-gray-400 hover:text-white">✎</button>
                  <button title="Delete" onClick={() => onDelete(c)} className="px-1 text-gray-400 hover:text-red-400">🗑</button>
                </div>
              ))}
            </div>
          ))}
        </nav>
        <div className="flex items-center justify-between border-t border-gray-700 p-3 text-sm">
          <span className="truncate">{user.name}</span>
          <button onClick={onLogout} className="rounded bg-gray-700 px-2 py-1 hover:bg-gray-600">Logout</button>
        </div>
      </aside>
    </>
  );
}
