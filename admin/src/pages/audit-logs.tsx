import React, { useState } from 'react';
import Head from 'next/head';
import {
  FileText,
  Search,
  Filter,
  Shield,
  Clock,
  Terminal,
  AlertTriangle,
  Info,
  AlertOctagon,
  Download,
  Activity,
  Globe
} from 'lucide-react';
import { INITIAL_AUDIT_LOGS, AuditLogItem } from '../lib/mockData';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>(INITIAL_AUDIT_LOGS);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const filtered = logs.filter(log => {
    const matchesSearch =
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.adminUser.toLowerCase().includes(search.toLowerCase()) ||
      log.targetEntity.toLowerCase().includes(search.toLowerCase()) ||
      log.details.toLowerCase().includes(search.toLowerCase()) ||
      log.ipAddress.toLowerCase().includes(search.toLowerCase());
    const matchesSev = severityFilter === 'ALL' || log.severity === severityFilter;
    return matchesSearch && matchesSev;
  });

  const severityBadges: Record<string, { label: string; icon: any; class: string }> = {
    INFO: { label: 'INFO', icon: Info, class: 'badge-blue' },
    WARNING: { label: 'WARN', icon: AlertTriangle, class: 'badge-amber' },
    CRITICAL: { label: 'CRIT', icon: AlertOctagon, class: 'badge-rose' }
  };

  return (
    <>
      <Head>
        <title>Audit Trail & System Logs | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Terminal className="w-7 h-7 text-indigo-400" />
              Administrative Audit Trail & Security Logs
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Immutable chronological record of administrative interventions, price modifications, and verification events.
            </p>
          </div>

          <button
            onClick={() => alert('Exporting signed audit archive...')}
            className="btn btn-secondary inline-flex items-center gap-2 self-start sm:self-auto"
          >
            <Download className="w-4 h-4" />
            Export Audit Archive
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Logged Events</div>
            <div className="text-xl font-bold text-white mt-1">{logs.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Critical Security Events</div>
            <div className="text-xl font-bold text-rose-400 mt-1">
              {logs.filter(l => l.severity === 'CRITICAL').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Admin Auth Actions</div>
            <div className="text-xl font-bold text-indigo-400 mt-1">
              {logs.filter(l => l.action.includes('VERIFIED') || l.action.includes('APPROVED')).length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Log Integrity Status</div>
            <div className="text-xl font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
              <Shield className="w-4 h-4" /> SHA-256 Valid
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
              placeholder="Search by action, administrator, target, IP..."
              className="input pl-10"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            {['ALL', 'INFO', 'WARNING', 'CRITICAL'].map(sev => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  severityFilter === sev
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {sev === 'ALL' ? 'All Severities' : sev}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table font-mono text-xs">
            <thead>
              <tr className="font-sans">
                <th>Timestamp (UTC)</th>
                <th>Severity</th>
                <th>Actor / Admin User</th>
                <th>Action Identifier</th>
                <th>Target Resource</th>
                <th>Event Metadata & Parameters</th>
                <th>Origin IP</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(log => {
                const SevIcon = severityBadges[log.severity]?.icon || Info;
                return (
                  <tr key={log.id}>
                    <td>
                      <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {log.timestamp}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${severityBadges[log.severity]?.class} inline-flex items-center gap-1`}>
                        <SevIcon className="w-3 h-3" />
                        {severityBadges[log.severity]?.label}
                      </span>
                    </td>
                    <td>
                      <span className="text-indigo-400 font-semibold">{log.adminUser}</span>
                    </td>
                    <td>
                      <span className="text-cyan-300 font-bold bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                        {log.action}
                      </span>
                    </td>
                    <td>
                      <span className="text-slate-200">{log.targetEntity}</span>
                    </td>
                    <td>
                      <span className="text-slate-300 font-sans text-xs max-w-md block">
                        {log.details}
                      </span>
                    </td>
                    <td>
                      <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                        <Globe className="w-3 h-3 text-slate-500" />
                        {log.ipAddress}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center py-12 text-slate-500 font-sans">
                    No audit records match the current filter query.
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
