import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { INITIAL_DEVICES, DeviceItem } from '@/lib/mockData';
import { Smartphone, Laptop, Search, Filter, ShieldCheck, ScrollText } from 'lucide-react';

export default function DevicesPage() {
  const [devices, setDevices] = useState<DeviceItem[]>(INITIAL_DEVICES);
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('ALL');

  const filtered = devices.filter((d) => {
    const matchesSearch =
      d.brand.toLowerCase().includes(search.toLowerCase()) ||
      d.model.toLowerCase().includes(search.toLowerCase()) ||
      d.ownerName.toLowerCase().includes(search.toLowerCase());
    const matchesCat = catFilter === 'ALL' || d.category === catFilter.toLowerCase();
    return matchesSearch && matchesCat;
  });

  return (
    <AdminLayout
      title="Registered Device Fleet"
      subtitle="Catalog of customer hardware, digital passports, diagnostic logs, and service lifecycles"
    >
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={styles.toolbarRow}>
          <div style={styles.searchWrapper}>
            <Search size={16} color="#6B7280" />
            <input
              type="text"
              className="input-control"
              placeholder="Search by brand, model, or customer name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px', maxWidth: '380px' }}
            />
          </div>

          <div style={styles.filterGroup}>
            <Filter size={16} color="#9CA3AF" />
            <select
              className="input-control"
              style={{ width: '160px' }}
              value={catFilter}
              onChange={(e) => setCatFilter(e.target.value)}
            >
              <option value="ALL">All Categories</option>
              <option value="SMARTPHONE">Smartphones</option>
              <option value="LAPTOP">Laptops</option>
            </select>
          </div>
        </div>

        <div className="table-container" style={{ marginTop: '18px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Device Specifications</th>
                <th>Category</th>
                <th>Registered Owner</th>
                <th>Condition</th>
                <th>Status</th>
                <th>Digital Passport</th>
                <th>Registered Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr key={d.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={styles.deviceIconBox}>
                        {d.category === 'laptop' ? (
                          <Laptop size={18} color="#60A5FA" />
                        ) : (
                          <Smartphone size={18} color="#A78BFA" />
                        )}
                      </div>
                      <div>
                        <div style={{ fontWeight: '800', color: '#F9FAFB' }}>
                          {d.brand} {d.model}
                        </div>
                        <div style={{ fontSize: '11px', color: '#6B7280', fontFamily: 'monospace' }}>
                          ID: #DEV-00{d.id}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-gray">{d.category}</span>
                  </td>
                  <td>
                    <div>
                      <div style={{ fontWeight: '600', color: '#E5E7EB' }}>{d.ownerName}</div>
                      <div style={{ fontSize: '12px', color: '#9CA3AF' }}>{d.ownerEmail}</div>
                    </div>
                  </td>
                  <td>
                    <span style={{ fontSize: '13px', color: '#D1D5DB' }}>{d.condition}</span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        d.status === 'active'
                          ? 'badge-emerald'
                          : d.status === 'repair'
                          ? 'badge-amber'
                          : 'badge-blue'
                      }`}
                    >
                      ● {d.status}
                    </span>
                  </td>
                  <td>
                    {d.hasPassport ? (
                      <span className="badge badge-purple" style={{ cursor: 'pointer' }}>
                        <ScrollText size={12} /> DPP Active
                      </span>
                    ) : (
                      <span className="badge badge-gray">Not Generated</span>
                    )}
                  </td>
                  <td style={{ color: '#6B7280' }}>{d.registeredDate}</td>
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
  deviceIconBox: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    backgroundColor: '#1E293B',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
};
