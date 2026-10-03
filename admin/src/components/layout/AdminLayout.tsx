import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuth } from '@/context/AuthContext';
import { ShieldAlert, Lock } from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children, title, subtitle }) => {
  const { user, loading, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAdmin && router.pathname !== '/login') {
      router.push('/login');
    }
  }, [loading, isAdmin, router]);

  if (loading) {
    return (
      <div style={styles.centerBox}>
        <div style={styles.loadingSpinner} />
        <p style={styles.loadingText}>Verifying Administrator Credentials...</p>
      </div>
    );
  }

  // If unauthenticated or non-admin, render access denied guard
  if (!isAdmin && router.pathname !== '/login') {
    return (
      <div style={styles.accessDeniedBox}>
        <div style={styles.deniedIcon}>
          <Lock size={48} color="#F43F5E" />
        </div>
        <h2 style={styles.deniedTitle}>Access Restricted — Administrators Only</h2>
        <p style={styles.deniedSubtitle}>
          You must be authenticated with the <strong>ADMIN</strong> role to view the command dashboard.
        </p>
        <button
          className="btn btn-primary"
          onClick={() => router.push('/login')}
          style={{ marginTop: '20px' }}
        >
          Go to Admin Login
        </button>
      </div>
    );
  }

  return (
    <div style={styles.layoutRoot}>
      <Sidebar />
      <div style={styles.mainContentWrapper}>
        <Header title={title} subtitle={subtitle} />
        <main style={styles.pageContent}>
          {children}
        </main>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  layoutRoot: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#0B0F17',
  },
  mainContentWrapper: {
    marginLeft: 'var(--sidebar-width)',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    minWidth: 0,
  },
  pageContent: {
    flex: 1,
    padding: '28px',
    backgroundColor: '#0B0F17',
  },
  centerBox: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0B0F17',
  },
  loadingSpinner: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    border: '3px solid rgba(59, 130, 246, 0.2)',
    borderTopColor: '#3B82F6',
    animation: 'spin 0.8s linear infinite',
  },
  loadingText: {
    marginTop: '16px',
    fontSize: '14px',
    color: '#9CA3AF',
    fontWeight: '500',
  },
  accessDeniedBox: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0B0F17',
    padding: '24px',
    textAlign: 'center',
  },
  deniedIcon: {
    width: '80px',
    height: '80px',
    borderRadius: '24px',
    backgroundColor: 'rgba(244, 63, 94, 0.12)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '20px',
    border: '1px solid rgba(244, 63, 94, 0.3)',
  },
  deniedTitle: {
    fontSize: '24px',
    fontWeight: '800',
    color: '#F9FAFB',
    marginBottom: '8px',
  },
  deniedSubtitle: {
    fontSize: '14px',
    color: '#9CA3AF',
    maxWidth: '440px',
    lineHeight: '1.5',
  },
};
