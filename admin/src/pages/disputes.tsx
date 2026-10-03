import React, { useState } from 'react';
import Head from 'next/head';
import {
  AlertOctagon,
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  ShieldAlert,
  User,
  Wrench,
  DollarSign,
  ArrowRight
} from 'lucide-react';
import { INITIAL_DISPUTES, DisputeItem } from '../lib/mockData';

export default function DisputesPage() {
  const [disputes, setDisputes] = useState<DisputeItem[]>(INITIAL_DISPUTES);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const filtered = disputes.filter(d => {
    const matchesSearch =
      d.caseNumber.toLowerCase().includes(search.toLowerCase()) ||
      d.repairCode.toLowerCase().includes(search.toLowerCase()) ||
      d.customerName.toLowerCase().includes(search.toLowerCase()) ||
      d.technicianName.toLowerCase().includes(search.toLowerCase()) ||
      d.issueReason.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || d.status === statusFilter;
    const matchesPriority = priorityFilter === 'ALL' || d.priority === priorityFilter;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const handleResolve = (id: number, resolution: 'RESOLVED' | 'REFUNDED') => {
    setDisputes(prev =>
      prev.map(d => (d.id === id ? { ...d, status: resolution } : d))
    );
  };

  const priorityBadges: Record<string, { label: string; class: string }> = {
    HIGH: { label: 'High Priority', class: 'badge-rose' },
    MEDIUM: { label: 'Medium', class: 'badge-amber' },
    LOW: { label: 'Low', class: 'badge-slate' }
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    OPEN: { label: 'Open Case', class: 'badge-rose' },
    UNDER_REVIEW: { label: 'Under Admin Review', class: 'badge-amber' },
    RESOLVED: { label: 'Resolved (Warranty Re-service)', class: 'badge-emerald' },
    REFUNDED: { label: 'Resolved (Refunded)', class: 'badge-blue' }
  };

  return (
    <>
      <Head>
        <title>Disputes & Mediation | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <AlertOctagon className="w-7 h-7 text-rose-400" />
              Disputes & Mediation Tribunal
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Arbitrate conflicts between customers and service workshops, inspect repair evidence, and issue rulings.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Disputes</div>
            <div className="text-xl font-bold text-white mt-1">{disputes.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Active / Open</div>
            <div className="text-xl font-bold text-rose-400 mt-1">
              {disputes.filter(d => d.status === 'OPEN' || d.status === 'UNDER_REVIEW').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Escrow at Stake</div>
            <div className="text-xl font-bold text-amber-400 mt-1">
              ${disputes.reduce((sum, d) => sum + d.amount, 0).toFixed(2)}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Resolution Rate</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">100% SLA</div>
          </div>
        </div>

        {/* Filters */}
        <div className="glass-panel p-4 rounded-xl flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search case #, repair code, customer, reason..."
              className="input pl-10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Priority:</span>
              {['ALL', 'HIGH', 'MEDIUM', 'LOW'].map(prio => (
                <button
                  key={prio}
                  onClick={() => setPriorityFilter(prio)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold ${
                    priorityFilter === prio
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {prio === 'ALL' ? 'All' : prio}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Status:</span>
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="input py-1 px-2.5 text-xs h-8"
              >
                <option value="ALL">All Cases</option>
                <option value="OPEN">Open</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="RESOLVED">Resolved</option>
                <option value="REFUNDED">Refunded</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Case Number</th>
                <th>Work Order</th>
                <th>Parties Involved</th>
                <th>Claim Reason & Summary</th>
                <th>Escrow Amount</th>
                <th>Priority</th>
                <th>Status</th>
                <th className="text-right">Arbitration Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <span className="font-mono text-xs font-bold text-rose-400 bg-rose-950/40 px-2 py-1 rounded border border-rose-800/40">
                      {item.caseNumber}
                    </span>
                  </td>
                  <td>
                    <span className="font-mono text-xs text-indigo-400">{item.repairCode}</span>
                  </td>
                  <td>
                    <div className="text-xs space-y-0.5">
                      <div className="text-slate-200 font-medium flex items-center gap-1">
                        <User className="w-3 h-3 text-slate-400" />
                        {item.customerName}
                      </div>
                      <div className="text-slate-400 flex items-center gap-1">
                        <Wrench className="w-3 h-3 text-indigo-400" />
                        {item.technicianName}
                      </div>
                    </div>
                  </td>
                  <td>
                    <p className="text-xs text-slate-300 max-w-sm">{item.issueReason}</p>
                  </td>
                  <td>
                    <span className="font-bold text-white text-sm font-mono">
                      ${item.amount.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${priorityBadges[item.priority]?.class}`}>
                      {priorityBadges[item.priority]?.label}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${statusBadges[item.status]?.class}`}>
                      {statusBadges[item.status]?.label}
                    </span>
                  </td>
                  <td className="text-right">
                    {(item.status === 'OPEN' || item.status === 'UNDER_REVIEW') ? (
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          onClick={() => handleResolve(item.id, 'REFUNDED')}
                          className="btn bg-rose-600 hover:bg-rose-500 text-white text-xs py-1 px-2 rounded"
                        >
                          Issue Refund
                        </button>
                        <button
                          onClick={() => handleResolve(item.id, 'RESOLVED')}
                          className="btn btn-primary text-xs py-1 px-2"
                        >
                          Order Re-service
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-emerald-400 font-semibold inline-flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> Adjudicated
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No dispute cases match the filters.
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
