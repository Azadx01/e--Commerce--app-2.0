import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  LayoutDashboard,
  Users,
  Wrench,
  Smartphone,
  Hammer,
  FileSpreadsheet,
  Cpu,
  RefreshCw,
  Package,
  CreditCard,
  ShieldCheck,
  Star,
  Scale,
  ScrollText,
  LogOut,
  ShieldAlert,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: string | number;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/', icon: LayoutDashboard },
  { label: 'Users', href: '/users', icon: Users },
  { label: 'Technicians', href: '/technicians', icon: Wrench, badge: '1' },
  { label: 'Devices', href: '/devices', icon: Smartphone },
  { label: 'Repairs', href: '/repairs', icon: Hammer, badge: '4' },
  { label: 'Quotes', href: '/quotes', icon: FileSpreadsheet },
  { label: 'Parts Catalog', href: '/parts', icon: Cpu },
  { label: 'Resale & Trade-in', href: '/resale', icon: RefreshCw },
  { label: 'Parts Orders', href: '/orders', icon: Package },
  { label: 'Payments', href: '/payments', icon: CreditCard },
  { label: 'Warranties', href: '/warranties', icon: ShieldCheck },
  { label: 'Reviews', href: '/reviews', icon: Star },
  { label: 'Disputes', href: '/disputes', icon: Scale, badge: '2' },
  { label: 'Audit Logs', href: '/audit-logs', icon: ScrollText },
];

export const Sidebar: React.FC = () => {
  const router = useRouter();
  const { user, logout } = useAuth();

  return (
    <aside style={styles.sidebar}>
      {/* Brand Header */}
      <div style={styles.brandContainer}>
        <div style={styles.brandLogo}>
          <ShieldAlert size={22} color="#3B82F6" />
        </div>
        <div>
          <div style={styles.brandName}>ReVivo Admin</div>
          <div style={styles.brandBadge}>Command Center</div>
        </div>
      </div>

      {/* Navigation Links */}
      <div style={styles.navScroll}>
        <div style={styles.navSectionLabel}>CORE OPERATIONS</div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = router.pathname === item.href;

          return (
            <Link key={item.href} href={item.href} style={styles.navLink}>
              <div
                style={{
                  ...styles.navItemInner,
                  ...(isActive ? styles.navItemActive : {}),
                }}
              >
                <Icon size={18} color={isActive ? '#60A5FA' : '#9CA3AF'} />
                <span
                  style={{
                    ...styles.navLabel,
                    color: isActive ? '#F9FAFB' : '#D1D5DB',
                    fontWeight: isActive ? '700' : '500',
                  }}
                >
                  {item.label}
                </span>

                {item.badge && (
                  <span
                    style={{
                      ...styles.navBadge,
                      backgroundColor: isActive ? '#3B82F6' : '#374151',
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </div>
            </Link>
          );
        })}
      </div>

      {/* Admin User Footer */}
      <div style={styles.userFooter}>
        <div style={styles.userMeta}>
          <div style={styles.userAvatar}>
            {user?.name ? user.name[0].toUpperCase() : 'A'}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <div style={styles.userName}>{user?.name || 'Administrator'}</div>
            <div style={styles.userRole}>Super Admin</div>
          </div>
        </div>
        <button style={styles.logoutBtn} onClick={logout} title="Sign Out">
          <LogOut size={16} color="#9CA3AF" />
        </button>
      </div>
    </aside>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  sidebar: {
    width: 'var(--sidebar-width)',
    height: '100vh',
    position: 'fixed',
    top: 0,
    left: 0,
    backgroundColor: '#0F172A',
    borderRight: '1px solid rgba(255, 255, 255, 0.08)',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 100,
  },
  brandContainer: {
    height: 'var(--header-height)',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '0 20px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
  },
  brandLogo: {
    width: '38px',
    height: '38px',
    borderRadius: '10px',
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
    border: '1px solid rgba(59, 130, 246, 0.3)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandName: {
    fontSize: '16px',
    fontWeight: '800',
    color: '#F9FAFB',
    letterSpacing: '-0.3px',
  },
  brandBadge: {
    fontSize: '10px',
    fontWeight: '700',
    color: '#60A5FA',
    textTransform: 'uppercase',
    letterSpacing: '0.8px',
  },
  navScroll: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  navSectionLabel: {
    fontSize: '10px',
    fontWeight: '800',
    color: '#6B7280',
    letterSpacing: '1px',
    padding: '8px 12px 4px 12px',
  },
  navLink: {
    textDecoration: 'none',
  },
  navItemInner: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 14px',
    borderRadius: '8px',
    transition: 'all 0.15s ease',
    cursor: 'pointer',
  },
  navItemActive: {
    backgroundColor: 'rgba(59, 130, 246, 0.16)',
    border: '1px solid rgba(59, 130, 246, 0.35)',
  },
  navLabel: {
    fontSize: '13px',
    flex: 1,
  },
  navBadge: {
    fontSize: '10px',
    fontWeight: '700',
    color: '#FFFFFF',
    padding: '2px 7px',
    borderRadius: '10px',
  },
  userFooter: {
    padding: '14px 16px',
    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0B0F19',
  },
  userMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    overflow: 'hidden',
  },
  userAvatar: {
    width: '34px',
    height: '34px',
    borderRadius: '50%',
    backgroundColor: '#3B82F6',
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  userName: {
    fontSize: '13px',
    fontWeight: '700',
    color: '#F9FAFB',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis',
    overflow: 'hidden',
  },
  userRole: {
    fontSize: '11px',
    color: '#9CA3AF',
  },
  logoutBtn: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '6px',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
};
