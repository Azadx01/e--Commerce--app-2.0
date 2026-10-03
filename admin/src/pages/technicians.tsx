import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { INITIAL_TECHNICIANS, TechnicianItem } from '@/lib/mockData';
import { Wrench, ShieldCheck, ShieldAlert, Star, MapPin, Check, X, Search } from 'lucide-react';

export default function TechniciansPage() {
  const [techs, setTechs] = useState<TechnicianItem[]>(INITIAL_TECHNICIANS);
  const [search, setSearch] = useState('');

  const verifyTechnician = (id: number) => {
    setTechs((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isVerified: true, status: 'active' } : t))
    );
  };

  const rejectTechnician = (id: number) => {
    setTechs((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isVerified: false, status: 'suspended' } : t))
    );
  };

  const filteredTechs = techs.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.businessName.toLowerCase().includes(search.toLowerCase()) ||
      t.serviceArea.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AdminLayout
      title="Technician Network & Verification"
      subtitle="Review workshop applications, verify credentials, manage service areas, and monitor ratings"
    >
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        <div style={styles.toolbarRow}>
          <div style={styles.searchWrapper}>
            <Search size={16} color="#6B7280" />
            <input
              type="text"
              className="input-control"
              placeholder="Search technician, workshop or service area..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px', maxWidth: '400px' }}
            />
          </div>

          <div style={styles.statsRow}>
            <div style={styles.statPill}>
              <span style={{ color: '#10B981', fontWeight: '800' }}>
                {techs.filter((t) => t.isVerified).length}
              </span>{' '}
              Verified
            </div>
            <div style={styles.statPill}>
              <span style={{ color: '#F59E0B', fontWeight: '800' }}>
                {techs.filter((t) => !t.isVerified).length}
              </span>{' '}
              Pending
            </div>
          </div>
        </div>

        <div className="table-container" style={{ marginTop: '18px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Specialist & Workshop</th>
                <th>Service Area</th>
                <th>Specializations / Skills</th>
                <th>Rating & Reviews</th>
                <th>Active Jobs</th>
                <th>Verification</th>
                <th style={{ textAlign: 'right' }}>Admin Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredTechs.map((tech) => (
                <tr key={tech.id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: '800', color: '#F9FAFB' }}>
                        {tech.businessName}
                      </div>
                      <div style={{ fontSize: '12px', color: '#9CA3AF' }}>
                        {tech.name} • {tech.email}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px' }}>
                      <MapPin size={14} color="#60A5FA" />
                      <span>{tech.serviceArea}</span>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', maxWidth: '280px' }}>
                      {tech.skills.map((skill, sIdx) => (
                        <span key={sIdx} style={styles.skillBadge}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Star size={14} color="#F59E0B" fill="#F59E0B" />
                      <strong style={{ color: '#FBBF24' }}>{tech.rating.toFixed(1)}</strong>
                      <span style={{ color: '#6B7280', fontSize: '12px' }}>
                        ({tech.totalReviews})
                      </span>
                    </div>
                  </td>
                  <td>
                    <span style={{ fontWeight: '700', color: '#60A5FA' }}>
                      {tech.activeRepairs} active
                    </span>
                  </td>
                  <td>
                    {tech.isVerified ? (
                      <span className="badge badge-emerald">
                        <ShieldCheck size={12} /> Verified Pro
                      </span>
                    ) : (
                      <span className="badge badge-amber">
                        <ShieldAlert size={12} /> Pending Review
                      </span>
                    )}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    {!tech.isVerified ? (
                      <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                        <button
                          className="btn btn-sm btn-success"
                          onClick={() => verifyTechnician(tech.id)}
                        >
                          <Check size={14} /> Approve
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => rejectTechnician(tech.id)}
                        >
                          <X size={14} /> Reject
                        </button>
                      </div>
                    ) : (
                      <button
                        className="btn btn-sm btn-secondary"
                        onClick={() => rejectTechnician(tech.id)}
                      >
                        Revoke Badge
                      </button>
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
  statsRow: {
    display: 'flex',
    gap: '10px',
  },
  statPill: {
    backgroundColor: '#1E293B',
    padding: '6px 14px',
    borderRadius: '10px',
    fontSize: '13px',
    color: '#D1D5DB',
    border: '1px solid rgba(255, 255, 255, 0.08)',
  },
  skillBadge: {
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    color: '#93C5FD',
    border: '1px solid rgba(59, 130, 246, 0.2)',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '11px',
    fontWeight: '500',
  },
};
