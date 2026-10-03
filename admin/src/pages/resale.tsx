import React, { useState } from 'react';
import Head from 'next/head';
import {
  RotateCcw,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  DollarSign,
  TrendingUp,
  Battery,
  Award,
  Sparkles,
  ArrowRight,
  Eye,
  ShieldCheck
} from 'lucide-react';
import { INITIAL_RESALE, ResaleItem } from '../lib/mockData';

export default function ResalePage() {
  const [resales, setResales] = useState<ResaleItem[]>(INITIAL_RESALE);
  const [search, setSearch] = useState('');
  const [gradeFilter, setGradeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedItem, setSelectedItem] = useState<ResaleItem | null>(null);

  const filtered = resales.filter(r => {
    const matchesSearch =
      r.code.toLowerCase().includes(search.toLowerCase()) ||
      r.customerName.toLowerCase().includes(search.toLowerCase()) ||
      r.device.toLowerCase().includes(search.toLowerCase());
    const matchesGrade = gradeFilter === 'ALL' || r.conditionGrade === gradeFilter;
    const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
    return matchesSearch && matchesGrade && matchesStatus;
  });

  const handleStatusChange = (id: number, newStatus: ResaleItem['status']) => {
    setResales(prev =>
      prev.map(r => (r.id === id ? { ...r, status: newStatus } : r))
    );
    if (selectedItem && selectedItem.id === id) {
      setSelectedItem({ ...selectedItem, status: newStatus });
    }
  };

  const gradeBadges: Record<string, { label: string; class: string }> = {
    A: { label: 'Grade A (Pristine)', class: 'badge-emerald' },
    B: { label: 'Grade B (Minor Wear)', class: 'badge-blue' },
    C: { label: 'Grade C (Heavy Scuffs)', class: 'badge-amber' }
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    SUBMITTED: { label: 'Submitted', class: 'badge-slate' },
    INSPECTION_PENDING: { label: 'Inspection Pending', class: 'badge-purple' },
    OFFER_ACCEPTED: { label: 'Offer Accepted', class: 'badge-blue' },
    PAID: { label: 'Payout Completed', class: 'badge-emerald' },
    REJECTED: { label: 'Rejected', class: 'badge-rose' }
  };

  const recoBadges: Record<string, { label: string; class: string }> = {
    SELL: { label: 'Direct Resale', class: 'badge-emerald' },
    REPAIR: { label: 'Refurbish First', class: 'badge-amber' },
    REPLACE: { label: 'Recycle / Salvage', class: 'badge-rose' }
  };

  return (
    <>
      <Head>
        <title>Resale & Trade-in Management | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <RotateCcw className="w-7 h-7 text-indigo-400" />
              Device Resale, Trade-in & Buyback Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Review algorithmic device valuations, verify battery health diagnostics, and approve customer payouts.
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Trade-in Requests</div>
            <div className="text-xl font-bold text-white mt-1">{resales.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Accepted Valuations</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              ${resales.filter(r => r.status === 'OFFER_ACCEPTED' || r.status === 'PAID').reduce((sum, r) => sum + r.valuationOffer, 0).toFixed(0)}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Pending Inspections</div>
            <div className="text-xl font-bold text-purple-400 mt-1">
              {resales.filter(r => r.status === 'INSPECTION_PENDING' || r.status === 'SUBMITTED').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Avg Recovery Rate</div>
            <div className="text-xl font-bold text-cyan-400 mt-1">
              {Math.round((resales.reduce((sum, r) => sum + (r.valuationOffer / r.originalPrice), 0) / resales.length) * 100)}% of MSRP
            </div>
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
              placeholder="Search by resale code, customer name, device..."
              className="input pl-10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Grade:</span>
              {['ALL', 'A', 'B', 'C'].map(grade => (
                <button
                  key={grade}
                  onClick={() => setGradeFilter(grade)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold ${
                    gradeFilter === grade
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {grade === 'ALL' ? 'All' : `Grade ${grade}`}
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
                <option value="ALL">All Statuses</option>
                <option value="SUBMITTED">Submitted</option>
                <option value="INSPECTION_PENDING">Inspection Pending</option>
                <option value="OFFER_ACCEPTED">Offer Accepted</option>
                <option value="PAID">Payout Completed</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Resale Code & Customer</th>
                <th>Device Model</th>
                <th>Condition Grade</th>
                <th>Battery Health</th>
                <th>AI Recommendation</th>
                <th>Original MSRP</th>
                <th>Valuation Offer</th>
                <th>Status</th>
                <th className="text-right">Admin Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id}>
                  <td>
                    <div>
                      <div className="font-mono text-xs font-bold text-indigo-400">
                        {item.code}
                      </div>
                      <div className="text-xs text-slate-300 mt-0.5">{item.customerName}</div>
                      <div className="text-[11px] text-slate-500">{item.requestDate}</div>
                    </div>
                  </td>
                  <td>
                    <span className="font-semibold text-white text-sm">{item.device}</span>
                  </td>
                  <td>
                    <span className={`badge ${gradeBadges[item.conditionGrade]?.class}`}>
                      {gradeBadges[item.conditionGrade]?.label}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5">
                      <Battery
                        className={`w-4 h-4 ${
                          item.batteryHealth >= 85
                            ? 'text-emerald-400'
                            : item.batteryHealth >= 75
                            ? 'text-amber-400'
                            : 'text-rose-400'
                        }`}
                      />
                      <span className="font-mono font-bold text-xs text-white">
                        {item.batteryHealth}%
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${recoBadges[item.decisionRecommendation]?.class}`}>
                      {recoBadges[item.decisionRecommendation]?.label}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs text-slate-400 line-through">
                      ${item.originalPrice.toFixed(0)}
                    </span>
                  </td>
                  <td>
                    <span className="font-bold text-emerald-400 text-sm">
                      ${item.valuationOffer.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${statusBadges[item.status]?.class}`}>
                      {statusBadges[item.status]?.label}
                    </span>
                  </td>
                  <td className="text-right">
                    <div className="inline-flex items-center gap-1.5">
                      {item.status === 'SUBMITTED' && (
                        <button
                          onClick={() => handleStatusChange(item.id, 'INSPECTION_PENDING')}
                          className="btn btn-secondary text-xs py-1 px-2.5"
                        >
                          Send to Inspect
                        </button>
                      )}
                      {item.status === 'INSPECTION_PENDING' && (
                        <button
                          onClick={() => handleStatusChange(item.id, 'OFFER_ACCEPTED')}
                          className="btn btn-primary text-xs py-1 px-2.5"
                        >
                          Approve Valuation
                        </button>
                      )}
                      {item.status === 'OFFER_ACCEPTED' && (
                        <button
                          onClick={() => handleStatusChange(item.id, 'PAID')}
                          className="btn bg-emerald-600 hover:bg-emerald-500 text-white text-xs py-1 px-2.5 rounded-lg shadow-lg shadow-emerald-600/30"
                        >
                          Authorize Payout
                        </button>
                      )}
                      {item.status === 'PAID' && (
                        <span className="text-xs text-emerald-400 font-semibold inline-flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> Disbursed
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500">
                    No resale requests match your search criteria.
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
