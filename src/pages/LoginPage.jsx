import { useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import Notice from '../components/Notice.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function LoginPage() {
  const { user, signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/admin" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setBusy(true);
    try {
      await signIn(username, password);
      navigate(location.state?.from || '/admin', { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="auth">
      <div className="auth-side">
        <img className="auth-logo" src="/logo.png" alt="Seal of the Office of the Student Affairs and Services" />
        <h1>OSAS staff desk</h1>
        <p>Post found items, check claims against school IDs, and keep the claim history.</p>
      </div>
      <div className="auth-main">
        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>Sign in</h2>
          <p className="muted">Only OSAS staff need an account. Students can browse and send claims without signing in.</p>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Notice kind="error">{error}</Notice>
          <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
          <p className="hint">Prototype account: username osas, password osas123. The Django login replaces this later.</p>
        </form>
      </div>
    </section>
  );
}
