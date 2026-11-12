const BASE = '/api';
export class ApiError extends Error {
  constructor(message, status, data) { super(message); this.status = status; this.data = data; }
}
async function req(path, { method = 'GET', body } = {}) {
  const token = localStorage.getItem('token');
  let res;
  try {
    res = await fetch(BASE + path, {
      method,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch { throw new ApiError('Network error. Check your connection.', 0, null); }
  let data = null;
  try { data = await res.json(); } catch { /* 204 */ }
  if (!res.ok) {
    const d = data?.detail;
    const msg = typeof d === 'string' ? d : Array.isArray(d) ? d.map((x) => x.msg.replace('Value error, ', '')).join('; ') : data?.message || 'Request failed';
    throw new ApiError(msg, res.status, data);
  }
  return data;
}
export const api = {
  register: (b) => req('/auth/register', { method: 'POST', body: b }),
  login: (b) => req('/auth/login', { method: 'POST', body: b }),
  logout: () => req('/auth/logout', { method: 'POST' }),
  me: () => req('/auth/me'),
  listConvs: () => req('/conversations'),
  createConv: () => req('/conversations', { method: 'POST' }),
  getConv: (id) => req(`/conversations/${id}`),
  rename: (id, title) => req(`/conversations/${id}`, { method: 'PATCH', body: { title } }),
  remove: (id) => req(`/conversations/${id}`, { method: 'DELETE' }),
  send: (id, content, retry_message_id) =>
    req(`/conversations/${id}/messages`, { method: 'POST', body: { content, retry_message_id } }),
};
