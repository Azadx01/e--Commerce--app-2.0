import React, { useState } from 'react';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { INITIAL_USERS, UserItem } from '@/lib/mockData';
import { Users, Search, UserPlus, Filter, Shield, UserX, CheckCircle, Smartphone } from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState<UserItem[]>(INITIAL_USERS);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter.toLowerCase();
    return matchesSearch && matchesRole;
  });

  const toggleStatus = (id: number) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === id ? { ...u, status: u.status === 'active' ? 'suspended' : 'active' } : u
      )
    );
  };

  return (
    <AdminLayout
      title="User Management"
      subtitle="Manage customer profiles, technician registrations, admin roles, and account security"
    >
      <div className="glass-panel" style={{ padding: '20px 24px' }}>
        {/* Controls Toolbar */}
        <div style={styles.toolbarRow}>
          <div style={styles.searchWrapper}>
            <Search size={16} color="#6B7280" />
            <input
              type="text"
              className="input-control"
              placeholder="Search by user name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '36px' }}
            />
          </div>

          <div style={styles.filterGroup}>
            <Filter size={16} color="#9CA3AF" />
            <select
              className="input-control"
              style={{ width: '150px' }}
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="ALL">All Roles</option>
              <option value="CUSTOMER">Customer</option>
              <option value="TECHNICIAN">Technician</option>
              <option value="ADMIN">Admin</option>
            </select>

            <button className="btn btn-primary" onClick={() => alert('Add User Modal Open')}>
              <UserPlus size={16} /> Add User
            </button>
          </div>
        </div>

        {/* Users Table */}
        <div className="table-container" style={{ marginTop: '16px' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>User Details</th>
                <th>Role</th>
                <th>Status</th>
                <th>Devices</th>
                <th>Total Spent</th>
                <th>Joined</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={styles.avatarCircle}>{u.name[0]}</div>
                      <div>
                        <div style={{ fontWeight: '700', color: '#F9FAFB' }}>{u.name}</div>
                        <div style={{ fontSize: '12px', color: '#9CA3AF' }}>{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        u.role === 'admin'
                          ? 'badge-rose'
                          : u.role === 'technician'
                          ? 'badge-purple'
                          : 'badge-blue'
                      }`}
                    >
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge ${
                        u.status === 'active' ? 'badge-emerald' : 'badge-gray'
                      }`}
                    >
                      ● {u.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Smartphone size={14} color="#9CA3AF" />
                      <span>{u.deviceCount} registered</span>
                    </div>
                  </td>
                  <td style={{ fontWeight: '700' }}>${u.totalSpent.toFixed(2)}</td>
                  <td style={{ color: '#6B7280' }}>{u.joinedDate}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      className={`btn btn-sm ${u.status === 'active' ? 'btn-danger' : 'btn-success'}`}
                      onClick={() => toggleStatus(u.id)}
                    >
                      {u.status === 'active' ? 'Suspend' : 'Activate'}
                    </button>
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
    minWidth: '260px',
  },
  filterGroup: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  avatarCircle: {
    width: '34px',
    height: '34px',
    borderRadius: '50%',
    backgroundColor: '#1E293B',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#60A5FA',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '13px',
  },
};
