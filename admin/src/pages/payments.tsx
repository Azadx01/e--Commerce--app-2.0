import React, { useState } from 'react';
import Head from 'next/head';
import {
  CreditCard,
  Search,
  DollarSign,
  TrendingUp,
  Percent,
  Download,
  Filter,
  CheckCircle2,
  RotateCcw,
  ShieldCheck,
  ArrowUpRight,
  ArrowDownLeft
} from 'lucide-react';
import { INITIAL_PAYMENTS, PaymentItem } from '../lib/mockData';

export default function PaymentsPage() {
  const [payments, setPayments] = useState<PaymentItem[]>(INITIAL_PAYMENTS);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = payments.filter(p => {
    const matchesSearch =
      p.transactionId.toLowerCase().includes(search.toLowerCase()) ||
      p.paymentMethod.toLowerCase().includes(search.toLowerCase()) ||
      p.type.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'ALL' || p.type === typeFilter;
    const matchesStatus = statusFilter === 'ALL' || p.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const totalGross = payments.reduce((sum, p) => (p.status === 'COMPLETED' ? sum + p.amount : sum), 0);
  const totalPlatformFees = payments.reduce((sum, p) => (p.status === 'COMPLETED' ? sum + p.platformFee : sum), 0);
  const totalPayouts = payments.reduce((sum, p) => (p.status === 'COMPLETED' ? sum + p.payoutAmount : sum), 0);

  const handleRefund = (id: number) => {
    if (confirm('Issue full refund for this transaction?')) {
      setPayments(prev =>
        prev.map(p => (p.id === id ? { ...p, status: 'REFUNDED' } : p))
      );
    }
  };

  const typeLabels: Record<string, { label: string; class: string }> = {
    CUSTOMER_REPAIR: { label: 'Repair Payment (Customer)', class: 'badge-blue' },
    TECHNICIAN_PAYOUT: { label: 'Tech Payout (85%)', class: 'badge-emerald' },
    RESALE_BUYBACK: { label: 'Resale Buyback Payout', class: 'badge-purple' },
    PARTS_PURCHASE: { label: 'Spare Parts Order', class: 'badge-amber' }
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    COMPLETED: { label: 'Settled', class: 'badge-emerald' },
    PENDING: { label: 'Processing', class: 'badge-amber' },
    REFUNDED: { label: 'Refunded', class: 'badge-rose' },
    FAILED: { label: 'Failed', class: 'badge-rose' }
  };

  return (
    <>
      <Head>
        <title>Payments & Financial Ledger | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <CreditCard className="w-7 h-7 text-indigo-400" />
              Financial Ledger & Payment Gateway
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Live settlement streams, 15% marketplace revenue commission cuts, and automated technician payouts.
            </p>
          </div>

          <button
            onClick={() => alert('Exporting sanitized ledger to CSV...')}
            className="btn btn-secondary inline-flex items-center gap-2 self-start sm:self-auto"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Gross Transaction Volume
              </div>
              <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
                <DollarSign className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white mt-3 font-mono">
              ${totalGross.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-emerald-400 flex items-center gap-1 mt-2">
              <TrendingUp className="w-3.5 h-3.5" /> +18.4% this month
            </div>
          </div>

          <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                ReVivo Platform Commission (15%)
              </div>
              <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                <Percent className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-3 font-mono">
              ${totalPlatformFees.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-slate-400 mt-2">Net platform revenue collected</div>
          </div>

          <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
                Technician & Vendor Disbursals
              </div>
              <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl font-bold text-cyan-400 mt-3 font-mono">
              ${totalPayouts.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-slate-400 mt-2">100% automated direct deposits</div>
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
              placeholder="Search by Txn ID, payment method..."
              className="input pl-10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Type:</span>
              <select
                value={typeFilter}
                onChange={e => setTypeFilter(e.target.value)}
                className="input py-1 px-2.5 text-xs h-8"
              >
                <option value="ALL">All Types</option>
                <option value="CUSTOMER_REPAIR">Customer Repair</option>
                <option value="TECHNICIAN_PAYOUT">Tech Payout</option>
                <option value="RESALE_BUYBACK">Resale Buyback</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Status:</span>
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="input py-1 px-2.5 text-xs h-8"
              >
                <option value="ALL">All Statuses</option>
                <option value="COMPLETED">Settled</option>
                <option value="REFUNDED">Refunded</option>
                <option value="PENDING">Pending</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Txn Reference</th>
                <th>Transaction Type</th>
                <th>Payment Method</th>
                <th>Gross Total</th>
                <th>Platform Commission</th>
                <th>Net Payout</th>
                <th>Status</th>
                <th>Date</th>
                <th className="text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(txn => (
                <tr key={txn.id}>
                  <td>
                    <span className="font-mono text-xs font-bold text-slate-200">
                      {txn.transactionId}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${typeLabels[txn.type]?.class || 'badge-slate'}`}>
                      {typeLabels[txn.type]?.label || txn.type}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs text-slate-300 font-medium">{txn.paymentMethod}</span>
                  </td>
                  <td>
                    <span className="font-bold text-white text-sm font-mono">
                      ${txn.amount.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className="font-mono text-xs text-emerald-400 font-semibold">
                      +${txn.platformFee.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className="font-mono text-xs text-cyan-400">
                      ${txn.payoutAmount.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${statusBadges[txn.status]?.class}`}>
                      {statusBadges[txn.status]?.label}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs text-slate-400">{txn.date}</span>
                  </td>
                  <td className="text-right">
                    {txn.status === 'COMPLETED' && txn.type === 'CUSTOMER_REPAIR' && (
                      <button
                        onClick={() => handleRefund(txn.id)}
                        className="text-xs text-rose-400 hover:text-rose-300 font-medium inline-flex items-center gap-1 hover:underline"
                      >
                        <RotateCcw className="w-3.5 h-3.5" /> Refund
                      </button>
                    )}
                    {txn.status === 'REFUNDED' && (
                      <span className="text-xs text-rose-400 font-semibold">Reversed</span>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500">
                    No transactions match the selected filters.
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
