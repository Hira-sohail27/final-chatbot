// Groups are derived from last_message_at in the browser's local timezone.
export function groupConvs(convs) {
  const now = new Date();
  const sod = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const day = 86400000;
  const g = { Today: [], Yesterday: [], 'Previous 7 Days': [], Older: [] };
  for (const c of convs) {
    const t = new Date(c.last_message_at).getTime();
    const k = t >= sod ? 'Today' : t >= sod - day ? 'Yesterday' : t >= sod - 7 * day ? 'Previous 7 Days' : 'Older';
    g[k].push(c);
  }
  return Object.entries(g).filter(([, v]) => v.length);
}
