import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { INITIAL_REPAIRS, RepairItem } from '@/lib/mockData';
import { Hammer, Search, Filter, Clock, ChevronRight, DollarSign, CheckCircle2 } from 'lucide-react';

const ALL_STATUSES = [
  'ALL',
  'REQUESTED',
  'TECHNICIAN_ASSIGNED',
  'DEVICE_RECEIVED',
  'DIAGNOSIS_PENDING',
  'QUOTE_PENDING',
  'CUSTOMER_APPROVED',
  'PARTS_PENDING',
  'REPAIR_IN_PROGRESS',
  'QUALITY_CHECK',
  'READY_FOR_DELIVERY',
  'DELIVERED',
  'CANCELLED',
  'DISPUTED',
];

export default function RepairsPage() {
  const [repairs, setRepairs] = useState<RepairItem[]>(INITIAL_REPAIRS);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredRepairs = repairs.filter((r) => {
    const matchesSearch =
      r.code.toLowerCase().includes(search.toLowerCase()) ||
      r.customerName.toLowerCase().includes(search.toLowerCase()) ||
      r.device.toLowerCase().includes(search.toLowerCase()) ||
      r.technician.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const advanceStatus = (id: number) => {
    const progression = [
      'REQUESTED',
      'TECHNICIAN_ASSIGNED',
      'DEVICE_RECEIVED',
      'DIAGNOSIS_PENDING',
      'QUOTE_PENDING',
      'CUSTOMER_APPROVED',
      'PARTS_PENDING',
      'REPAIR_IN_PROGRESS',
      'QUALITY_CHECK',
      'READY_FOR_DELIVERY',
      'DELIVERED',
    ];

    setRepairs((prev) =>
      prev.map((r) => {
        if (r.id === id) {
          const currIdx = progression.indexOf(r.status);
          if (currIdx >= 0 && currIdx < progression.length - 1) {
            const nextStatus = progression[currIdx + 1];
            return { ...r, status: nextStatus, stageNumber: currIdx + 2 };
          }
        }
        return r;
      })
    );
  };

  return (
    <AdminLayout
      title="Master Repair Pipeline"
      subtitle="Monitor and transition repair work orders across all 11 verified workflow milestones"
    >
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={styles.toolbarRow}>
          <div style={styles.searchWrapper}>
            <Search size={16} color="#6B7280" />
            <input
              type="text"
              className="input-control"
              placeholder="Search by ticket code, customer, device, or technician..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px', maxWidth: '420px' }}
            />
          </div>

          <div style={styles.filterGroup}>
            <Filter size={16} color="#9CA3AF" />
            <select
              className="input-control"
              style={{ width: '200px' }}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              {ALL_STATUSES.map((st) => (
                <option key={st} value={st}>
                  {st.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="table-container" style={{ marginTop: '18px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Order Ticket</th>
                <th>Customer</th>
                <th>Device</th>
                <th>Specialist</th>
                <th>Workflow Stage</th>
                <th>Quote</th>
                <th>Turnaround</th>
                <th style={{ textAlign: 'right' }}>Pipeline Control</th>
              </tr>
            </thead>
            <tbody>
              {filteredRepairs.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="font-mono" style={{ fontWeight: '800', color: '#60A5FA' }}>
                      #{r.code}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: '600' }}>{r.customerName}</div>
                  </td>
                  <td>{r.device}</td>
                  <td>
                    <div style={{ fontSize: '12px', color: '#D1D5DB' }}>{r.technician}</div>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        r.status === 'DELIVERED'
                          ? 'badge-emerald'
                          : r.status === 'REPAIR_IN_PROGRESS'
                          ? 'badge-blue'
                          : r.status === 'CUSTOMER_APPROVED'
                          ? 'badge-purple'
                          : r.status === 'CANCELLED'
                          ? 'badge-rose'
                          : 'badge-amber'
                      }`}
                    >
                      {r.stageNumber}/11 {r.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>
                    <strong style={{ color: '#F9FAFB' }}>${r.quoteAmount.toFixed(2)}</strong>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#9CA3AF' }}>
                      <Clock size={12} />
                      <span>{r.expectedTurnaround}</span>
                    </div>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    {r.status !== 'DELIVERED' && r.status !== 'CANCELLED' ? (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() => advanceStatus(r.id)}
                      >
                        Advance Stage <ChevronRight size={14} />
                      </button>
                    ) : (
                      <span style={{ fontSize: '12px', color: '#10B981', fontWeight: '700' }}>
                        ✓ Finalized
                      </span>
                    )}
                  </td>
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
  toolbarRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '16px',
    flexWrap: 'wrap',
  },
  searchWrapper: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    flex: 1,
  },
  filterGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
};
