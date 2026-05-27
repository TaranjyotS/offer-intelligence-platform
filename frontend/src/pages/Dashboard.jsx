import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  BarChart3,
  Gift,
  ListChecks,
  LockKeyhole,
  LogOut,
  ShieldCheck,
  Sparkles,
  UserRound,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { api, session } from '../api/client';
import MetricCard from '../components/MetricCard';

const initialForm = {
  member_id: 'A0F18FAA',
  transaction_type: 'GIFT',
  points_bought: 500,
  revenue_usd: 25.5,
};

const chartColors = ['#3867ff', '#28c3a4'];

function BrandLogo({ large = false }) {
  return (
    <img
      className={large ? 'brand-logo-image brand-logo-image-large' : 'brand-logo-image'}
      src="/logo-icon.png"
      alt="ML Offer Orchestrator logo"
    />
  );
}

function BrandWordmark() {
  return (
    <div className="brand-wordmark" aria-label="ML Offer Orchestrator">
      <span className="wordmark-main">ML OFFER</span>
      <span className="wordmark-sub">ORCHESTRATOR</span>
    </div>
  );
}

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState('signin');
  const [credentials, setCredentials] = useState({ username: 'admin', password: 'demo123' });
  const [authError, setAuthError] = useState('');
  const [authSuccess, setAuthSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSignup = mode === 'signup';

  function updateCredentials(event) {
    const { name, value } = event.target;
    setCredentials((current) => ({ ...current, [name]: value }));
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setAuthError('');
    setAuthSuccess('');
    setCredentials(nextMode === 'signin' ? { username: 'admin', password: 'demo123' } : { username: '', password: '' });
  }

  async function submit(event) {
    event.preventDefault();
    setAuthError('');
    setAuthSuccess('');
    setIsSubmitting(true);
    try {
      if (isSignup) {
        await api.register(credentials);
        setAuthSuccess('Account created. Please sign in to continue.');
        setMode('signin');
        return;
      }
      const auth = await api.login(credentials);
      onLogin(auth.username);
    } catch (err) {
      setAuthError(err.message || 'Authentication failed. Please check your details and try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel brand-panel">
        <BrandLogo large />
        <BrandWordmark />
        <p>
          Intelligent loyalty offer decisioning powered by member behavior signals, prediction services,
          and real-time offer assignment.
        </p>
        <div className="login-highlights">
          <span><Sparkles size={16} /> Personalized offers</span>
          <span><ShieldCheck size={16} /> Secure operator access</span>
          <span><BarChart3 size={16} /> Decision analytics</span>
        </div>
      </section>

      <section className="login-panel login-card">
        <div>
          <p className="login-kicker">{isSignup ? 'Create access' : 'Welcome back'}</p>
          <h2>{isSignup ? 'Create your operator account' : 'Sign in to the decision console'}</h2>
          <p className="muted">
            {isSignup
              ? 'First-time users can create a demo operator account and start exploring the protected console.'
              : 'Returning users can sign in with their account. Demo credentials are prefilled for portfolio review.'}
          </p>
        </div>
        <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
          <button type="button" className={mode === 'signin' ? 'active' : ''} onClick={() => switchMode('signin')}>Sign in</button>
          <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => switchMode('signup')}>Sign up</button>
        </div>
        <form onSubmit={submit}>
          <label>
            Username
            <input name="username" value={credentials.username} onChange={updateCredentials} autoComplete="username" />
          </label>
          <label>
            Password
            <input
              name="password"
              type="password"
              value={credentials.password}
              onChange={updateCredentials}
              autoComplete={isSignup ? 'new-password' : 'current-password'}
            />
          </label>
          <button type="submit" disabled={isSubmitting}>
            <LockKeyhole size={18} /> {isSubmitting ? 'Please wait...' : isSignup ? 'Create Account' : 'Sign In'}
          </button>
          {authError ? <p className="error" role="alert">{authError}</p> : null}
          {authSuccess ? <p className="success" role="status">{authSuccess}</p> : null}
        </form>
      </section>
    </main>
  );
}

export default function Dashboard() {
  const [user, setUser] = useState(() => session.getUser() || '');
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      api.me().catch(() => logout());
    }
  }, [user]);

  const chartData = useMemo(() => {
    if (!result) return [];
    return [
      { name: 'Member Value Score', value: Number(result.value_prediction.prediction.toFixed(2)) },
      { name: 'Response Rate (%)', value: Number((result.response_prediction.prediction * 100).toFixed(2)) },
    ];
  }, [result]);

  function login(username) {
    setUser(username);
  }

  function logout() {
    session.clearSession();
    setUser('');
    setResult(null);
    setHistory([]);
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: name.includes('points') || name.includes('revenue') ? Number(value) : value,
    }));
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const offer = await api.createOffer(form);
      setResult(offer);
      const memberHistory = await api.getHistory(form.member_id);
      setHistory(memberHistory.transactions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!user) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <main className="page-shell">
      <header className="top-bar">
        <BrandLogo />
        <div className="user-pill">
          <UserRound size={18} />
          <span>{user}</span>
          <button type="button" className="icon-button" onClick={logout} aria-label="Sign out"><LogOut size={16} /></button>
        </div>
      </header>

      <section className="hero centered-hero dashboard-hero">
        <BrandWordmark />
        <p className="hero-copy">
          A real-time loyalty decisioning system that analyzes member transaction history, predicts member value and response likelihood,
          then recommends the most suitable personalized offer.
        </p>
      </section>

      <section className="grid two-col">
        <form className="card form-card" onSubmit={submit}>
          <div className="section-title">
            <Sparkles />
            <h2>Generate Offer</h2>
          </div>
          <label>
            Member ID
            <input name="member_id" value={form.member_id} onChange={updateField} />
          </label>
          <label>
            Transaction Type
            <select name="transaction_type" value={form.transaction_type} onChange={updateField}>
              <option>BUY</option>
              <option>GIFT</option>
              <option>REDEEM</option>
            </select>
          </label>
          <label>
            Points Bought
            <input type="number" name="points_bought" value={form.points_bought} onChange={updateField} min="0" />
          </label>
          <label>
            Revenue USD
            <input type="number" step="0.01" name="revenue_usd" value={form.revenue_usd} onChange={updateField} min="0" />
          </label>
          <button disabled={loading}>{loading ? 'Running orchestration...' : 'Assign Offer'}</button>
          {error ? <p className="error">{error}</p> : null}
        </form>

        <div className="card result-card">
          <div className="section-title">
            <ShieldCheck />
            <h2>Decision Output</h2>
          </div>
          {result ? (
            <>
              <div className="offer-banner">
                <Gift />
                <div>
                  <p>{result.offer.priority.toUpperCase()} PRIORITY OFFER</p>
                  <strong>{result.offer.offer_label}</strong>
                  <span>{result.offer.reason}</span>
                </div>
              </div>
              <div className="metrics-grid">
                <MetricCard
                  label="Member Value Score"
                  value={result.value_prediction.prediction.toFixed(2)}
                  hint={result.value_prediction.confidence + ' confidence'}
                />
                <MetricCard
                  label="Response Rate"
                  value={`${(result.response_prediction.prediction * 100).toFixed(1)}%`}
                  hint={result.response_prediction.confidence + ' confidence'}
                />
                <MetricCard label="History Before Write" value={result.history_count_before_write} />
                <MetricCard label="Transactions Used" value={result.features.transaction_count} />
              </div>
              <div className="chart-box">
                <ResponsiveContainer width="100%" height={230}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
                    <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 12 }} />
                    <YAxis tick={{ fill: '#475569', fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="value" radius={[12, 12, 0, 0]}>
                      {chartData.map((entry, index) => <Cell key={entry.name} fill={chartColors[index % chartColors.length]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <ListChecks />
              <p>Submit a transaction to see prediction scores, feature signals, and the selected offer.</p>
            </div>
          )}
        </div>
      </section>

      <section className="card">
        <div className="section-title">
          <Activity />
          <h2>Member Transaction History</h2>
        </div>
        {history.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Timestamp</th><th>Type</th><th>Points</th><th>Revenue</th></tr></thead>
              <tbody>
                {history.map((tx, index) => (
                  <tr key={`${tx.transaction_utc_ts}-${index}`}>
                    <td>{new Date(tx.transaction_utc_ts).toLocaleString()}</td>
                    <td>{tx.transaction_type}</td>
                    <td>{tx.points_bought}</td>
                    <td>${tx.revenue_usd}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="muted">No transactions loaded yet.</p>}
      </section>
    </main>
  );
}
