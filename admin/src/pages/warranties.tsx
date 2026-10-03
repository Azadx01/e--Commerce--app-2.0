import React, { useState } from 'react';
import Head from 'next/head';
import {
  ShieldCheck,
  Search,
  Calendar,
  Clock,
  User,
  Smartphone,
  CheckCircle,
  AlertTriangle,
  FileText,
  Building2,
  Filter
} from 'lucide-react';
import { INITIAL_WARRANTIES, WarrantyItem } from '../lib/mockData';

export default function WarrantiesPage() {
  const [warranties, setWarranties] = useState<WarrantyItem[]>(INITIAL_WARRANTIES);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = warranties.filter(w => {
    const matchesSearch =
      w.passportId.toLowerCase().includes(search.toLowerCase()) ||
      w.device.toLowerCase().includes(search.toLowerCase()) ||
      w.customerName.toLowerCase().includes(search.toLowerCase()) ||
      w.provider.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || w.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleClaim = (id: number) => {
    if (confirm('Register a guarantee warranty claim under this Passport certificate?')) {
      setWarranties(prev =>
        prev.map(w => (w.id === id ? { ...w, status: 'CLAIMED' } : w))
      );
    }
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    ACTIVE: { label: 'Active Coverage', class: 'badge-emerald' },
    EXPIRED: { label: 'Expired', class: 'badge-slate' },
    CLAIMED: { label: 'Claim in Progress', class: 'badge-amber' }
  };

  return (
    <>
      <Head>
        <title>Warranties & Guarantees | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <ShieldCheck className="w-7 h-7 text-indigo-400" />
              Device Warranty & Digital Guarantee Vault
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Active repair guarantee terms, manufacturer backing, and cryptographically verified passport certificates.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Registered Warranties</div>
            <div className="text-xl font-bold text-white mt-1">{warranties.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Active Coverage</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              {warranties.filter(w => w.status === 'ACTIVE').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Claims Filed</div>
            <div className="text-xl font-bold text-amber-400 mt-1">
              {warranties.filter(w => w.status === 'CLAIMED').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Avg Coverage Window</div>
            <div className="text-xl font-bold text-cyan-400 mt-1">195 Days</div>
          </div>
        </div>

        {/* Filters */}
        <div className="glass-panel p-4 rounded-xl flex flex-col sm:flex-row gap-4 justify-between items-stretch sm:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by Passport ID, customer, device, provider..."
              className="input pl-10"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            {['ALL', 'ACTIVE', 'CLAIMED', 'EXPIRED'].map(st => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  statusFilter === st
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {st === 'ALL' ? 'All Warranties' : st}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Passport ID & Customer</th>
                <th>Covered Hardware</th>
                <th>Service Provider</th>
                <th>Duration Terms</th>
                <th>Validity Window</th>
                <th>Days Remaining</th>
                <th>Status</th>
                <th className="text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <div>
                      <div className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40 inline-block">
                        {item.passportId}
                      </div>
                      <div className="text-xs text-slate-300 mt-1">{item.customerName}</div>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5 font-semibold text-white text-sm">
                      <Smartphone className="w-4 h-4 text-indigo-400" />
                      {item.device}
                    </div>
                  </td>
                  <td>
                    <span className="text-xs text-slate-300">{item.provider}</span>
                  </td>
                  <td>
                    <span className="text-xs font-medium text-slate-200 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                      {item.duration}
                    </span>
                  </td>
                  <td>
                    <div className="text-xs text-slate-400">
                      <div>From: {item.startDate}</div>
                      <div className="text-slate-300 font-medium">To: {item.expiryDate}</div>
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1 text-sm font-bold text-emerald-400 font-mono">
                      <Clock className="w-3.5 h-3.5" />
                      {item.daysRemaining} days
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${statusBadges[item.status]?.class}`}>
                      {statusBadges[item.status]?.label}
                    </span>
                  </td>
                  <td className="text-right">
                    {item.status === 'ACTIVE' && (
                      <button
                        onClick={() => handleClaim(item.id)}
                        className="btn btn-secondary text-xs py-1 px-2.5 hover:border-amber-500/50"
                      >
                        File Claim
                      </button>
                    )}
                    {item.status === 'CLAIMED' && (
                      <span className="text-xs text-amber-400 font-semibold inline-flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" /> In Review
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No warranty certificates found matching the search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
