import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import {
  Users,
  Hammer,
  CheckCircle2,
  Wrench,
  RefreshCw,
  DollarSign,
  Scale,
  TrendingUp,
  ArrowUpRight,
  ShieldCheck,
  AlertTriangle,
  Clock,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import Link from 'next/link';
import {
  INITIAL_REPAIRS,
  INITIAL_USERS,
  INITIAL_TECHNICIANS,
  INITIAL_DISPUTES,
  INITIAL_RESALE,
} from '@/lib/mockData';

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState('30d');

  // Computed metrics from core systems
  const totalUsersCount = 14820;
  const activeRepairsCount = INITIAL_REPAIRS.filter(
    (r) => !['DELIVERED', 'CLOSED', 'CANCELLED'].includes(r.status)
  ).length + 45;
  const completedRepairsCount = 1294;
  const verifiedTechniciansCount = INITIAL_TECHNICIANS.filter((t) => t.isVerified).length + 84;
  const resaleRequestsCount = INITIAL_RESALE.length + 109;
  const totalRevenueAmount = 184920.0;
  const openDisputesCount = INITIAL_DISPUTES.filter((d) => d.status === 'OPEN' || d.status === 'UNDER_REVIEW').length;

  return (
    <AdminLayout
      title="Platform Operations Overview"
      subtitle="Real-time performance metrics, repair workflows, revenue, and security telemetry"
    >
      {/* ── 7 Core Dashboard KPI Cards ─────────────────────────────────── */}
      <div style={styles.metricsGrid}>
        {/* Metric 1: Users */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(59, 130, 246, 0.15)' }}>
              <Users size={20} color="#60A5FA" />
            </div>
            <span style={styles.metricTrendPos}>+12.4%</span>
          </div>
          <div style={styles.metricValue}>{totalUsersCount.toLocaleString()}</div>
          <div style={styles.metricLabel}>Total Users</div>
          <div style={styles.metricSub}>Active customers & staff accounts</div>
        </div>

        {/* Metric 2: Active Repairs */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(245, 158, 11, 0.15)' }}>
              <Hammer size={20} color="#FBBF24" />
            </div>
            <span style={styles.metricLiveBadge}>
              <span style={styles.livePulse} /> LIVE
            </span>
          </div>
          <div style={styles.metricValue}>{activeRepairsCount}</div>
          <div style={styles.metricLabel}>Active Repairs</div>
          <div style={styles.metricSub}>In diagnostics, quote or workbench</div>
        </div>

        {/* Metric 3: Completed Repairs */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(16, 185, 129, 0.15)' }}>
              <CheckCircle2 size={20} color="#34D399" />
            </div>
            <span style={styles.metricTrendPos}>+8.9%</span>
          </div>
          <div style={styles.metricValue}>{completedRepairsCount.toLocaleString()}</div>
          <div style={styles.metricLabel}>Completed Repairs</div>
          <div style={styles.metricSub}>99.4% first-time fix rate</div>
        </div>

        {/* Metric 4: Technicians */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(139, 92, 246, 0.15)' }}>
              <Wrench size={20} color="#A78BFA" />
            </div>
            <span style={styles.metricVerifiedPill}>Verified</span>
          </div>
          <div style={styles.metricValue}>{verifiedTechniciansCount}</div>
          <div style={styles.metricLabel}>Verified Technicians</div>
          <div style={styles.metricSub}>3 pending background approval</div>
        </div>

        {/* Metric 5: Resale Requests */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(6, 182, 212, 0.15)' }}>
              <RefreshCw size={20} color="#22D3EE" />
            </div>
            <span style={styles.metricTrendPos}>+24.1%</span>
          </div>
          <div style={styles.metricValue}>{resaleRequestsCount}</div>
          <div style={styles.metricLabel}>Resale Requests</div>
          <div style={styles.metricSub}>Automated decision valuations</div>
        </div>

        {/* Metric 6: Revenue */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(16, 185, 129, 0.2)' }}>
              <DollarSign size={20} color="#10B981" />
            </div>
            <span style={styles.metricTrendPos}>+18.7%</span>
          </div>
          <div style={styles.metricValue}>${totalRevenueAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
          <div style={styles.metricLabel}>Total Revenue</div>
          <div style={styles.metricSub}>Platform GMV & commission split</div>
        </div>

        {/* Metric 7: Disputes */}
        <div style={styles.metricCard} className="glass-panel">
          <div style={styles.metricTop}>
            <div style={{ ...styles.metricIconBox, backgroundColor: 'rgba(244, 63, 94, 0.15)' }}>
              <Scale size={20} color="#FB7185" />
            </div>
            <span style={openDisputesCount > 0 ? styles.metricAlertPill : styles.metricOkPill}>
              {openDisputesCount > 0 ? 'Action Req.' : 'Clear'}
            </span>
          </div>
          <div style={{ ...styles.metricValue, color: openDisputesCount > 0 ? '#FB7185' : '#F9FAFB' }}>
            {openDisputesCount}
          </div>
          <div style={styles.metricLabel}>Open Disputes</div>
          <div style={styles.metricSub}>Customer & technician mediation</div>
        </div>
      </div>

      {/* ── Visual Analytics & Status Distribution ──────────────────────── */}
      <div style={styles.chartsGrid}>
        {/* Repair Pipeline Breakdown */}
        <div style={styles.pipelineCard} className="glass-panel">
          <div style={styles.cardHeaderRow}>
            <div>
              <h2 style={styles.cardTitle}>Live Repair Pipeline Status</h2>
              <p style={styles.cardSub}>Work orders currently progressing across all 11 lifecycle stages</p>
            </div>
            <Link href="/repairs" style={styles.viewAllLink}>
              View All Repairs <ArrowUpRight size={14} />
            </Link>
          </div>

          <div style={styles.pipelineBarsContainer}>
            <div style={styles.pipelineStageItem}>
              <div style={styles.stageMeta}>
                <span>1. Request Created</span>
                <strong>12 Orders</strong>
              </div>
              <div style={styles.progressBarTrack}>
                <div style={{ ...styles.progressBarFill, width: '25%', backgroundColor: '#3B82F6' }} />
              </div>
            </div>

            <div style={styles.pipelineStageItem}>
              <div style={styles.stageMeta}>
                <span>4. Diagnosis & Inspection</span>
                <strong>9 Orders</strong>
              </div>
              <div style={styles.progressBarTrack}>
                <div style={{ ...styles.progressBarFill, width: '18%', backgroundColor: '#F59E0B' }} />
              </div>
            </div>

            <div style={styles.pipelineStageItem}>
              <div style={styles.stageMeta}>
                <span>5. Quote & Approval</span>
                <strong>14 Orders</strong>
              </div>
              <div style={styles.progressBarTrack}>
                <div style={{ ...styles.progressBarFill, width: '29%', backgroundColor: '#8B5CF6' }} />
              </div>
            </div>

            <div style={styles.pipelineStageItem}>
              <div style={styles.stageMeta}>
                <span>8. Repair In Progress</span>
                <strong>8 Orders</strong>
              </div>
              <div style={styles.progressBarTrack}>
                <div style={{ ...styles.progressBarFill, width: '16%', backgroundColor: '#06B6D4' }} />
              </div>
            </div>

            <div style={styles.pipelineStageItem}>
              <div style={styles.stageMeta}>
                <span>9. Quality & Delivery Ready</span>
                <strong>5 Orders</strong>
              </div>
              <div style={styles.progressBarTrack}>
                <div style={{ ...styles.progressBarFill, width: '12%', backgroundColor: '#10B981' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Command Shortcuts */}
        <div style={styles.shortcutsCard} className="glass-panel">
          <h2 style={styles.cardTitle}>Admin Action Quick Launcher</h2>
          <p style={styles.cardSub}>Direct operational controls</p>

          <div style={styles.shortcutsList}>
            <Link href="/technicians" style={styles.shortcutItem}>
              <div style={styles.shortcutIconWrap}>
                <ShieldCheck size={18} color="#10B981" />
              </div>
              <div style={styles.shortcutTextWrap}>
                <div style={styles.shortcutTitle}>Verify New Technicians</div>
                <div style={styles.shortcutDesc}>Review credentials & cleanroom audit</div>
              </div>
              <ChevronRight size={16} color="#6B7280" />
            </Link>

            <Link href="/parts" style={styles.shortcutItem}>
              <div style={styles.shortcutIconWrap}>
                <Hammer size={18} color="#3B82F6" />
              </div>
              <div style={styles.shortcutTextWrap}>
                <div style={styles.shortcutTitle}>Manage Spare Parts Catalog</div>
                <div style={styles.shortcutDesc}>Update inventory & OEM compatibility</div>
              </div>
              <ChevronRight size={16} color="#6B7280" />
            </Link>

            <Link href="/disputes" style={styles.shortcutItem}>
              <div style={styles.shortcutIconWrap}>
                <AlertTriangle size={18} color="#F43F5E" />
              </div>
              <div style={styles.shortcutTextWrap}>
                <div style={styles.shortcutTitle}>Mediate Open Disputes</div>
                <div style={styles.shortcutDesc}>Resolve claims & issue zero-cost warranties</div>
              </div>
              <ChevronRight size={16} color="#6B7280" />
            </Link>

            <Link href="/audit-logs" style={styles.shortcutItem}>
              <div style={styles.shortcutIconWrap}>
                <Clock size={18} color="#A78BFA" />
              </div>
              <div style={styles.shortcutTextWrap}>
                <div style={styles.shortcutTitle}>Security Audit Logs</div>
                <div style={styles.shortcutDesc}>Inspect price change requests & admin actions</div>
              </div>
              <ChevronRight size={16} color="#6B7280" />
            </Link>
          </div>
        </div>
      </div>

      {/* ── Recent Repair Activity Table ───────────────────────────────── */}
      <div style={{ marginTop: '24px' }} className="glass-panel">
        <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={styles.cardTitle}>Recent Repair Work Orders</h2>
            <p style={styles.cardSub}>Latest customer requests moving through the ReVivo ecosystem</p>
          </div>
          <Link href="/repairs" className="btn btn-secondary btn-sm">
            View All Repairs
          </Link>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Order Code</th>
                <th>Customer</th>
                <th>Device</th>
                <th>Assigned Specialist</th>
                <th>Status</th>
                <th>Quote Amount</th>
                <th>Turnaround</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {INITIAL_REPAIRS.map((repair) => (
                <tr key={repair.id}>
                  <td className="font-mono" style={{ color: '#60A5FA', fontWeight: '700' }}>
                    #{repair.code}
                  </td>
                  <td style={{ fontWeight: '600' }}>{repair.customerName}</td>
                  <td>{repair.device}</td>
                  <td>{repair.technician}</td>
                  <td>
                    <span
                      className={`badge ${
                        repair.status === 'DELIVERED'
                          ? 'badge-emerald'
                          : repair.status === 'REPAIR_IN_PROGRESS'
                          ? 'badge-blue'
                          : repair.status === 'CUSTOMER_APPROVED'
                          ? 'badge-purple'
                          : 'badge-amber'
                      }`}
                    >
                      {repair.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td style={{ fontWeight: '700' }}>${repair.quoteAmount.toFixed(2)}</td>
                  <td style={{ color: '#9CA3AF' }}>{repair.expectedTurnaround}</td>
                  <td style={{ color: '#6B7280' }}>{repair.createdAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AdminLayout>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '16px',
    marginBottom: '24px',
  },
  metricCard: {
    padding: '20px',
  },
  metricTop: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '14px',
  },
  metricIconBox: {
    width: '40px',
    height: '40px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  metricTrendPos: {
    fontSize: '11px',
    fontWeight: '700',
    color: '#34D399',
    backgroundColor: 'rgba(16, 185, 129, 0.12)',
    padding: '3px 7px',
    borderRadius: '6px',
  },
  metricLiveBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    fontSize: '10px',
    fontWeight: '800',
    color: '#FBBF24',
    backgroundColor: 'rgba(245, 158, 11, 0.15)',
    padding: '3px 8px',
    borderRadius: '12px',
  },
  livePulse: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    backgroundColor: '#F59E0B',
  },
  metricVerifiedPill: {
    fontSize: '10px',
    fontWeight: '700',
    color: '#A78BFA',
    backgroundColor: 'rgba(139, 92, 246, 0.15)',
    padding: '3px 8px',
    borderRadius: '10px',
  },
  metricAlertPill: {
    fontSize: '10px',
    fontWeight: '700',
    color: '#FB7185',
    backgroundColor: 'rgba(244, 63, 94, 0.15)',
    padding: '3px 8px',
    borderRadius: '10px',
  },
  metricOkPill: {
    fontSize: '10px',
    fontWeight: '700',
    color: '#34D399',
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    padding: '3px 8px',
    borderRadius: '10px',
  },
  metricValue: {
    fontSize: '26px',
    fontWeight: '800',
    color: '#F9FAFB',
    letterSpacing: '-0.6px',
  },
  metricLabel: {
    fontSize: '13px',
    fontWeight: '700',
    color: '#D1D5DB',
    marginTop: '4px',
  },
  metricSub: {
    fontSize: '11px',
    color: '#6B7280',
    marginTop: '2px',
  },
  chartsGrid: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '20px',
  },
  pipelineCard: {
    padding: '24px',
  },
  shortcutsCard: {
    padding: '24px',
  },
  cardHeaderRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '20px',
  },
  cardTitle: {
    fontSize: '16px',
    fontWeight: '700',
    color: '#F9FAFB',
  },
  cardSub: {
    fontSize: '12px',
    color: '#9CA3AF',
    marginTop: '2px',
  },
  viewAllLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '12px',
    fontWeight: '600',
    color: '#60A5FA',
    textDecoration: 'none',
  },
  pipelineBarsContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  pipelineStageItem: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  stageMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
    color: '#D1D5DB',
  },
  progressBarTrack: {
    height: '8px',
    backgroundColor: '#1F2937',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: '4px',
  },
  shortcutsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginTop: '16px',
  },
  shortcutItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px',
    backgroundColor: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid rgba(255, 255, 255, 0.06)',
    borderRadius: '10px',
    textDecoration: 'none',
    transition: 'all 0.15s ease',
  },
  shortcutIconWrap: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    backgroundColor: '#1E293B',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  shortcutTextWrap: {
    flex: 1,
  },
  shortcutTitle: {
    fontSize: '13px',
    fontWeight: '700',
    color: '#F9FAFB',
  },
  shortcutDesc: {
    fontSize: '11px',
    color: '#9CA3AF',
    marginTop: '1px',
  },
};
