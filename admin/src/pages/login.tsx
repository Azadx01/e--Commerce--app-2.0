import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/context/AuthContext';
import { ShieldCheck, Lock, Mail, AlertCircle, ArrowRight, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { loginAsAdmin, isAdmin } = useAuth();

  const [email, setEmail] = useState('admin@revivo.internal');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If already logged in as admin, redirect to dashboard
  React.useEffect(() => {
    if (isAdmin) {
      router.push('/');
    }
  }, [isAdmin, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const success = await loginAsAdmin(email, password);
      if (success) {
        router.push('/');
      } else {
        setError('Invalid admin credentials or insufficient role privileges. Only ADMIN role can access this portal.');
      }
    } catch {
      setError('An error occurred during authentication. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillQuickAdmin = () => {
    setEmail('admin@revivo.internal');
    setPassword('password123');
  };

  return (
    <div style={styles.loginContainer}>
      <div style={styles.loginCard} className="glass-panel">
        <div style={styles.loginHeader}>
          <div style={styles.logoBadge}>
            <ShieldCheck size={32} color="#3B82F6" />
          </div>
          <h1 style={styles.loginTitle}>ReVivo Admin Portal</h1>
          <p style={styles.loginSubtitle}>
            Restricted Enterprise Access • <strong>ADMIN ONLY</strong>
          </p>
        </div>

        {error && (
          <div style={styles.errorBanner}>
            <AlertCircle size={18} color="#FB7185" />
            <span style={styles.errorText}>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Admin Email</label>
            <div style={styles.inputWrapper}>
              <Mail size={16} color="#9CA3AF" style={styles.inputIcon} />
              <input
                type="email"
                required
                className="input-control"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@revivo.internal"
                style={{ paddingLeft: '38px' }}
              />
            </div>
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <div style={styles.inputWrapper}>
              <Lock size={16} color="#9CA3AF" style={styles.inputIcon} />
              <input
                type="password"
                required
                className="input-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                style={{ paddingLeft: '38px' }}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={styles.submitBtn}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to Command Center'}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        {/* Quick Demo Fill Helper */}
        <div style={styles.demoHelperBox}>
          <div style={styles.demoHeader}>
            <Sparkles size={14} color="#F59E0B" />
            <span>Developer / Master Demo Credentials</span>
          </div>
          <p style={styles.demoText}>
            Click below to auto-fill the authorized administrator credentials:
          </p>
          <button style={styles.quickFillBtn} onClick={fillQuickAdmin} type="button">
            Auto-fill admin@revivo.internal
          </button>
        </div>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  loginContainer: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0B0F17',
    padding: '20px',
    backgroundImage: 'radial-gradient(circle at 50% 10%, rgba(59, 130, 246, 0.12) 0%, transparent 60%)',
  },
  loginCard: {
    width: '100%',
    maxWidth: '440px',
    padding: '36px',
    borderRadius: '24px',
    backgroundColor: 'rgba(15, 23, 42, 0.85)',
  },
  loginHeader: {
    textAlign: 'center',
    marginBottom: '28px',
  },
  logoBadge: {
    width: '64px',
    height: '64px',
    borderRadius: '20px',
    backgroundColor: 'rgba(59, 130, 246, 0.12)',
    border: '1px solid rgba(59, 130, 246, 0.3)',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '16px',
  },
  loginTitle: {
    fontSize: '22px',
    fontWeight: '800',
    color: '#F9FAFB',
    letterSpacing: '-0.4px',
  },
  loginSubtitle: {
    fontSize: '13px',
    color: '#9CA3AF',
    marginTop: '4px',
  },
  errorBanner: {
    backgroundColor: 'rgba(244, 63, 94, 0.15)',
    border: '1px solid rgba(244, 63, 94, 0.3)',
    borderRadius: '10px',
    padding: '12px 14px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '20px',
  },
  errorText: {
    fontSize: '12px',
    color: '#FB7185',
    lineHeight: '1.4',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '18px',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '12px',
    fontWeight: '600',
    color: '#D1D5DB',
  },
  inputWrapper: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  inputIcon: {
    position: 'absolute',
    left: '12px',
    zIndex: 2,
  },
  submitBtn: {
    width: '100%',
    padding: '12px',
    marginTop: '8px',
    fontSize: '14px',
  },
  demoHelperBox: {
    marginTop: '24px',
    paddingTop: '20px',
    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
  },
  demoHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '11px',
    fontWeight: '700',
    color: '#F59E0B',
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    marginBottom: '6px',
  },
  demoText: {
    fontSize: '12px',
    color: '#9CA3AF',
    marginBottom: '10px',
    lineHeight: '1.4',
  },
  quickFillBtn: {
    width: '100%',
    padding: '8px 12px',
    backgroundColor: '#1E293B',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '8px',
    color: '#60A5FA',
    fontSize: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background 0.15s ease',
  },
};
