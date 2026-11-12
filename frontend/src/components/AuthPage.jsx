import { useState } from 'react';
import { api } from '../api';

function Field({ label, ...props }) {
  return (
    <label className="block text-sm font-medium text-gray-700">
      {label}
      <input {...props} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none" />
    </label>
  );
}

export default function AuthPage({ onAuth }) {
  const [mode, setMode] = useState('login');
  const [f, setF] = useState({ name: '', email: '', password: '', confirm_password: '' });
  const [err, setErr] = useState('');
  const [ok, setOk] = useState('');
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr(''); setOk('');
    if (mode === 'register') {
      if (!f.name.trim()) return setErr('Name is required');
      if (f.password.length < 8) return setErr('Password must be at least 8 characters');
      if (f.password !== f.confirm_password) return setErr('Passwords do not match');
    }
    setLoading(true);
    try {
      const res = mode === 'login'
        ? await api.login({ email: f.email, password: f.password })
        : await api.register(f);
      setOk(mode === 'login' ? 'Welcome back!' : 'Account created!');
      onAuth(res);
    } catch (e2) { setErr(e2.message); } finally { setLoading(false); }
  };

  return (
    <div className="flex min-h-full items-center justify-center bg-gray-100 p-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4 rounded-2xl bg-white p-6 shadow">
        <h1 className="text-2xl font-bold">{mode === 'login' ? 'Sign in' : 'Create account'}</h1>
        {mode === 'register' && <Field label="Name" value={f.name} onChange={set('name')} />}
        <Field label="Email" type="email" required value={f.email} onChange={set('email')} />
        <Field label="Password" type="password" required value={f.password} onChange={set('password')} />
        {mode === 'register' && <Field label="Confirm password" type="password" required value={f.confirm_password} onChange={set('confirm_password')} />}
        {err && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{err}</p>}
        {ok && <p className="rounded bg-green-50 p-2 text-sm text-green-700">{ok}</p>}
        <button disabled={loading} className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50">
          {loading ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Register'}
        </button>
        <button type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setErr(''); }}
          className="w-full text-sm text-indigo-600 hover:underline">
          {mode === 'login' ? "No account? Register" : 'Have an account? Sign in'}
        </button>
      </form>
    </div>
  );
}
