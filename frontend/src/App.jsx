import { useCallback, useEffect, useState } from 'react';
import { api } from './api';
import AuthPage from './components/AuthPage';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [convs, setConvs] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sending, setSending] = useState(false);
  const [failed, setFailed] = useState(null);
  const [drawer, setDrawer] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem('token')) { setReady(true); return; }
    api.me().then(setUser).catch(() => localStorage.removeItem('token')).finally(() => setReady(true));
  }, []);

  const refresh = useCallback(() => api.listConvs().then(setConvs).catch(() => {}), []);
  useEffect(() => { if (user) refresh(); }, [user, refresh]);

  const onAuth = ({ access_token, user }) => { localStorage.setItem('token', access_token); setUser(user); };
  const logout = async () => {
    try { await api.logout(); } catch { /* ignore */ }
    localStorage.removeItem('token');
    setUser(null); setConvs([]); setActiveId(null); setMessages([]); setFailed(null);
  };

  const open = async (id) => {
    setActiveId(id); setFailed(null); setDrawer(false);
    try { setMessages((await api.getConv(id)).messages); } catch { setMessages([]); }
  };
  const newChat = async () => {
    const c = await api.createConv();
    setConvs((p) => [c, ...p]); setActiveId(c.id); setMessages([]); setFailed(null); setDrawer(false);
  };
  const rename = async (c) => {
    const t = window.prompt('Rename conversation', c.title);
    if (t && t.trim()) { await api.rename(c.id, t.trim()); refresh(); }
  };
  const remove = async (c) => {
    if (!window.confirm(`Delete "${c.title}"? This cannot be undone.`)) return;
    await api.remove(c.id);
    if (c.id === activeId) { setActiveId(null); setMessages([]); }
    refresh();
  };

  const send = async (text, retryId = null) => {
    if (sending) return;
    setSending(true); setFailed(null);
    try {
      let id = activeId;
      if (!id) { const c = await api.createConv(); id = c.id; setActiveId(id); setConvs((p) => [c, ...p]); }
      if (!retryId) setMessages((m) => [...m.filter((x) => x.id !== 'tmp'), { id: 'tmp', role: 'user', content: text, created_at: new Date().toISOString() }]);
      const r = await api.send(id, text, retryId);
      setMessages((m) => [...m.filter((x) => x.id !== 'tmp' && x.id !== r.user_message.id), r.user_message, r.assistant_message]);
      refresh();
    } catch (e) {
      const um = e.data?.user_message;
      if (um) setMessages((m) => [...m.filter((x) => x.id !== 'tmp' && x.id !== um.id), um]);
      setFailed({ text, retryId: um?.id || null, message: e.message });
    } finally { setSending(false); }
  };

  if (!ready) return <p className="p-6">Loading…</p>;
  if (!user) return <AuthPage onAuth={onAuth} />;
  return (
    <div className="flex h-full">
      <Sidebar user={user} convs={convs} activeId={activeId} onNew={newChat} onOpen={open} onRename={rename}
        onDelete={remove} onLogout={logout} open={drawer} onClose={() => setDrawer(false)} />
      <ChatWindow messages={messages} sending={sending} failed={failed} onSend={(t) => send(t)}
        onRetry={() => send(failed.text, failed.retryId)} onMenu={() => setDrawer(true)} />
    </div>
  );
}
