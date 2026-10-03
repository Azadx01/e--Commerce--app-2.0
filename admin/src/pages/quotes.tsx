import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { INITIAL_QUOTES, QuoteItem } from '@/lib/mockData';
import { FileSpreadsheet, Search, ShieldCheck, Lock, AlertCircle } from 'lucide-react';

export default function QuotesPage() {
  const [quotes, setQuotes] = useState<QuoteItem[]>(INITIAL_QUOTES);
  const [search, setSearch] = useState('');

  const filtered = quotes.filter(
    (q) =>
      q.repairCode.toLowerCase().includes(search.toLowerCase()) ||
      q.device.toLowerCase().includes(search.toLowerCase()) ||
      q.technician.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AdminLayout
      title="Repair Quotes & Price Integrity"
      subtitle="Inspect itemized cost breakdowns, supplemental change requests, and verified customer approval audit logs"
    >
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={styles.topInfoBox}>
          <Lock size={18} color="#10B981" />
          <div style={styles.topInfoText}>
            <strong>Price Integrity Protocol:</strong> Technicians cannot increase the final price without issuing a Version 2+ change request and securing formal customer authorization.
          </div>
        </div>

        <div style={styles.toolbarRow}>
          <div style={styles.searchWrapper}>
            <Search size={16} color="#6B7280" />
            <input
              type="text"
              className="input-control"
              placeholder="Search quote by ticket #, device, or technician..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px', maxWidth: '380px' }}
            />
          </div>
        </div>

        <div className="table-container" style={{ marginTop: '18px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Ticket & Version</th>
                <th>Device</th>
                <th>Specialist</th>
                <th>Labor</th>
                <th>Parts</th>
                <th>Fees</th>
                <th>Total Price</th>
                <th>Warranty</th>
                <th>Customer Approval</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((q) => (
                <tr key={q.id}>
                  <td>
                    <div>
                      <span className="font-mono" style={{ fontWeight: '800', color: '#60A5FA' }}>
                        #{q.repairCode}
                      </span>
                      <span
                        style={{
                          marginLeft: '6px',
                          fontSize: '11px',
                          color: '#A78BFA',
                          fontWeight: '700',
                        }}
                      >
                        v{q.version} {q.isChangeRequest && '(Change Req)'}
                      </span>
                    </div>
                  </td>
                  <td style={{ fontWeight: '600' }}>{q.device}</td>
                  <td style={{ fontSize: '12px', color: '#D1D5DB' }}>{q.technician}</td>
                  <td>${q.laborCost.toFixed(2)}</td>
                  <td>${q.partsCost.toFixed(2)}</td>
                  <td>${q.otherFees.toFixed(2)}</td>
                  <td>
                    <strong style={{ color: '#F9FAFB', fontSize: '15px' }}>
                      ${q.totalAmount.toFixed(2)}
                    </strong>
                  </td>
                  <td>
                    <span style={{ fontSize: '12px', color: '#9CA3AF' }}>{q.warranty}</span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        q.status === 'APPROVED'
                          ? 'badge-emerald'
                          : q.status === 'PENDING'
                          ? 'badge-amber'
                          : q.status === 'REJECTED'
                          ? 'badge-rose'
                          : 'badge-gray'
                      }`}
                    >
                      {q.status}
                    </span>
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
  topInfoBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    border: '1px solid rgba(16, 185, 129, 0.25)',
    borderRadius: '10px',
    padding: '12px 16px',
    marginBottom: '20px',
  },
  topInfoText: {
    fontSize: '13px',
    color: '#D1FAE5',
    lineHeight: '1.4',
  },
  toolbarRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  searchWrapper: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    flex: 1,
  },
};
