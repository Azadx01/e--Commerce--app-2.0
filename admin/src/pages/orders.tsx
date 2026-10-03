import React, { useState } from 'react';
import Head from 'next/head';
import {
  ShoppingBag,
  Search,
  Truck,
  ExternalLink,
  CheckCircle2,
  Clock,
  Filter,
  Building,
  Wrench,
  AlertCircle
} from 'lucide-react';
import { INITIAL_ORDERS, OrderItem } from '../lib/mockData';

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderItem[]>(INITIAL_ORDERS);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = orders.filter(o => {
    const matchesSearch =
      o.orderNumber.toLowerCase().includes(search.toLowerCase()) ||
      o.supplier.toLowerCase().includes(search.toLowerCase()) ||
      o.technician.toLowerCase().includes(search.toLowerCase()) ||
      o.trackingNumber.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || o.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleStatusChange = (id: number, nextStatus: OrderItem['status']) => {
    setOrders(prev =>
      prev.map(o => (o.id === id ? { ...o, status: nextStatus } : o))
    );
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    PROCESSING: { label: 'Processing at Hub', class: 'badge-amber' },
    SHIPPED: { label: 'In Transit', class: 'badge-blue' },
    DELIVERED: { label: 'Delivered', class: 'badge-emerald' },
    CANCELLED: { label: 'Cancelled', class: 'badge-rose' }
  };

  return (
    <>
      <Head>
        <title>Supply & Parts Orders | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <ShoppingBag className="w-7 h-7 text-indigo-400" />
              Supply & B2B Purchase Orders
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Track warehouse parts dispatches, supplier fulfillment timelines, and technician delivery receipts.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Orders</div>
            <div className="text-xl font-bold text-white mt-1">{orders.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">In Transit / Shipped</div>
            <div className="text-xl font-bold text-blue-400 mt-1">
              {orders.filter(o => o.status === 'SHIPPED').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Delivered Orders</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              {orders.filter(o => o.status === 'DELIVERED').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Order Volume</div>
            <div className="text-xl font-bold text-indigo-400 mt-1">
              ${orders.reduce((sum, o) => sum + o.totalAmount, 0).toFixed(2)}
            </div>
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
              placeholder="Search by order #, supplier, technician, tracking..."
              className="input pl-10"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            {['ALL', 'PROCESSING', 'SHIPPED', 'DELIVERED'].map(st => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                  statusFilter === st
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {st === 'ALL' ? 'All Orders' : st}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Order Number</th>
                <th>Supplier / Hub</th>
                <th>Recipient Technician</th>
                <th>Items Count</th>
                <th>Total Value</th>
                <th>Carrier & Tracking</th>
                <th>Status</th>
                <th>Date</th>
                <th className="text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(order => (
                <tr key={order.id}>
                  <td>
                    <span className="font-mono font-bold text-indigo-400 text-xs bg-indigo-950/40 px-2 py-1 rounded border border-indigo-800/40">
                      {order.orderNumber}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5 text-slate-200 text-xs font-medium">
                      <Building className="w-3.5 h-3.5 text-slate-400" />
                      {order.supplier}
                    </div>
                  </td>
                  <td>
                    <div className="flex items-center gap-1.5 text-slate-200 text-xs">
                      <Wrench className="w-3.5 h-3.5 text-indigo-400" />
                      {order.technician}
                    </div>
                  </td>
                  <td>
                    <span className="text-xs text-slate-300 font-semibold">
                      {order.itemsCount} line items
                    </span>
                  </td>
                  <td>
                    <span className="font-bold text-emerald-400 text-sm">
                      ${order.totalAmount.toFixed(2)}
                    </span>
                  </td>
                  <td>
                    <div className="flex items-center gap-1 font-mono text-xs text-slate-300">
                      <Truck className="w-3.5 h-3.5 text-blue-400" />
                      <span>{order.trackingNumber}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${statusBadges[order.status]?.class}`}>
                      {statusBadges[order.status]?.label}
                    </span>
                  </td>
                  <td>
                    <span className="text-xs text-slate-400">{order.orderDate}</span>
                  </td>
                  <td className="text-right">
                    {order.status === 'PROCESSING' && (
                      <button
                        onClick={() => handleStatusChange(order.id, 'SHIPPED')}
                        className="btn btn-primary text-xs py-1 px-2.5"
                      >
                        Mark Shipped
                      </button>
                    )}
                    {order.status === 'SHIPPED' && (
                      <button
                        onClick={() => handleStatusChange(order.id, 'DELIVERED')}
                        className="btn bg-emerald-600 hover:bg-emerald-500 text-white text-xs py-1 px-2.5 rounded-lg"
                      >
                        Confirm Delivery
                      </button>
                    )}
                    {order.status === 'DELIVERED' && (
                      <span className="text-xs text-emerald-400 font-semibold inline-flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Received
                      </span>
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500">
                    No purchase orders found matching filter criteria.
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
