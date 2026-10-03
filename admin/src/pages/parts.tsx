import React, { useState } from 'react';
import Head from 'next/head';
import {
  Package,
  Search,
  Plus,
  Filter,
  CheckCircle,
  AlertTriangle,
  Layers,
  Wrench,
  ShieldCheck,
  Building2,
  Tag,
  X,
  TrendingDown
} from 'lucide-react';
import { INITIAL_PARTS, PartItem } from '../lib/mockData';

export default function PartsPage() {
  const [parts, setParts] = useState<PartItem[]>(INITIAL_PARTS);
  const [search, setSearch] = useState('');
  const [conditionFilter, setConditionFilter] = useState('ALL');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // New part form state
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    partType: 'Screen',
    manufacturer: '',
    condition: 'OEM' as 'OEM' | 'COMPATIBLE_THIRD_PARTY' | 'USED_TESTED',
    price: 99.0,
    stock: 10,
    warranty: '180 days',
    seller: 'ReVivo Central Supply',
    compatibleModels: ''
  });

  const filtered = parts.filter(p => {
    const matchesSearch =
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.sku.toLowerCase().includes(search.toLowerCase()) ||
      p.manufacturer.toLowerCase().includes(search.toLowerCase()) ||
      p.compatibleModels.some(m => m.toLowerCase().includes(search.toLowerCase()));
    const matchesCond = conditionFilter === 'ALL' || p.condition === conditionFilter;
    return matchesSearch && matchesCond;
  });

  const handleStockUpdate = (id: number, delta: number) => {
    setParts(prev =>
      prev.map(p => {
        if (p.id === id) {
          const newStock = Math.max(0, p.stock + delta);
          return { ...p, stock: newStock };
        }
        return p;
      })
    );
  };

  const handleAddPart = (e: React.FormEvent) => {
    e.preventDefault();
    const newPart: PartItem = {
      id: Date.now(),
      name: formData.name,
      sku: formData.sku || `SKU-${Date.now().toString().slice(-6)}`,
      partType: formData.partType,
      manufacturer: formData.manufacturer,
      condition: formData.condition,
      price: Number(formData.price),
      stock: Number(formData.stock),
      warranty: formData.warranty,
      seller: formData.seller,
      compatibleModels: formData.compatibleModels.split(',').map(m => m.trim()).filter(Boolean)
    };
    setParts(prev => [newPart, ...prev]);
    setIsModalOpen(false);
    setFormData({
      name: '',
      sku: '',
      partType: 'Screen',
      manufacturer: '',
      condition: 'OEM',
      price: 99.0,
      stock: 10,
      warranty: '180 days',
      seller: 'ReVivo Central Supply',
      compatibleModels: ''
    });
  };

  const conditionBadges: Record<string, { label: string; class: string }> = {
    OEM: { label: 'OEM Original', class: 'badge-emerald' },
    COMPATIBLE_THIRD_PARTY: { label: 'Compatible 3rd-Party', class: 'badge-blue' },
    USED_TESTED: { label: 'Used Tested', class: 'badge-amber' }
  };

  return (
    <>
      <Head>
        <title>Spare Parts Catalog | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Package className="w-7 h-7 text-indigo-400" />
              Spare Parts Catalog & Inventory
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Manage OEM, 3rd-party compatible, and tested reclaimed replacement hardware.
            </p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="btn btn-primary inline-flex items-center gap-2 self-start sm:self-auto"
          >
            <Plus className="w-4 h-4" />
            Add New Part SKU
          </button>
        </div>

        {/* Stats strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total SKUs</div>
            <div className="text-xl font-bold text-white mt-1">{parts.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">OEM Catalog</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              {parts.filter(p => p.condition === 'OEM').length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Low Stock Alerts</div>
            <div className="text-xl font-bold text-amber-400 mt-1">
              {parts.filter(p => p.stock < 10).length}
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Inventory Value</div>
            <div className="text-xl font-bold text-cyan-400 mt-1">
              ${parts.reduce((sum, p) => sum + p.price * p.stock, 0).toLocaleString('en-US', { minimumFractionDigits: 0 })}
            </div>
          </div>
        </div>

        {/* Filter bar */}
        <div className="glass-panel p-4 rounded-xl flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by part name, SKU, manufacturer, compatible model..."
              className="input pl-10"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            {['ALL', 'OEM', 'COMPATIBLE_THIRD_PARTY', 'USED_TESTED'].map(cond => (
              <button
                key={cond}
                onClick={() => setConditionFilter(cond)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  conditionFilter === cond
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                    : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700/80'
                }`}
              >
                {cond === 'ALL' ? 'All Conditions' : cond.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Part Details & SKU</th>
                <th>Condition</th>
                <th>Category</th>
                <th>Unit Price</th>
                <th>Stock Level</th>
                <th>Warranty</th>
                <th>Compatibility List</th>
                <th className="text-right">Quick Stock</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(part => {
                const isLowStock = part.stock < 8;
                return (
                  <tr key={part.id}>
                    <td>
                      <div>
                        <div className="font-semibold text-white">{part.name}</div>
                        <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                          <code className="text-[11px] text-cyan-400 font-mono bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                            {part.sku}
                          </code>
                          <span>• {part.manufacturer}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${conditionBadges[part.condition]?.class || 'badge-slate'}`}>
                        {conditionBadges[part.condition]?.label || part.condition}
                      </span>
                    </td>
                    <td>
                      <span className="text-xs text-slate-300 font-medium px-2 py-1 rounded bg-slate-800/70 border border-slate-700/50">
                        {part.partType}
                      </span>
                    </td>
                    <td>
                      <span className="font-bold text-emerald-400 text-sm">
                        ${part.price.toFixed(2)}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <span
                          className={`font-semibold text-sm ${
                            part.stock === 0
                              ? 'text-rose-400'
                              : isLowStock
                              ? 'text-amber-400'
                              : 'text-slate-200'
                          }`}
                        >
                          {part.stock} units
                        </span>
                        {isLowStock && (
                          <span className="badge badge-amber text-[10px] py-0 px-1.5">
                            Low
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5 text-xs text-slate-300">
                        <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                        {part.warranty}
                      </div>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {part.compatibleModels.map((model, idx) => (
                          <span
                            key={idx}
                            className="text-[11px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60"
                          >
                            {model}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="text-right">
                      <div className="inline-flex items-center gap-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/50">
                        <button
                          onClick={() => handleStockUpdate(part.id, -1)}
                          disabled={part.stock <= 0}
                          title="Reduce stock (-1)"
                          className="px-2 py-0.5 text-slate-300 hover:text-white hover:bg-slate-700 rounded disabled:opacity-30"
                        >
                          -
                        </button>
                        <button
                          onClick={() => handleStockUpdate(part.id, 1)}
                          title="Restock (+1)"
                          className="px-2 py-0.5 text-slate-300 hover:text-white hover:bg-slate-700 rounded"
                        >
                          +
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No spare parts found matching &ldquo;{search}&rdquo;
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Part Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div className="glass-panel w-full max-w-lg p-6 rounded-2xl border border-slate-700/80 shadow-2xl relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Package className="w-5 h-5 text-indigo-400" />
              Add New Spare Part to Catalog
            </h3>

            <form onSubmit={handleAddPart} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1 block">
                  Part Name / Description
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. iPhone 15 Pro OLED Super Retina Panel"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="input"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">SKU Code</label>
                  <input
                    type="text"
                    placeholder="SKU-IPH-15P-DISP"
                    value={formData.sku}
                    onChange={e => setFormData({ ...formData, sku: e.target.value })}
                    className="input font-mono text-xs"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Category</label>
                  <select
                    value={formData.partType}
                    onChange={e => setFormData({ ...formData, partType: e.target.value })}
                    className="input"
                  >
                    <option value="Screen">Screen / OLED</option>
                    <option value="Battery">Battery Unit</option>
                    <option value="Camera">Camera Sensor</option>
                    <option value="Keyboard">Keyboard / Topcase</option>
                    <option value="Charging Port">Charging Sub-Board</option>
                    <option value="Logic Board">Logic / Motherboard</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Manufacturer</label>
                  <input
                    type="text"
                    required
                    placeholder="Apple OEM, Samsung, LG..."
                    value={formData.manufacturer}
                    onChange={e => setFormData({ ...formData, manufacturer: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Condition</label>
                  <select
                    value={formData.condition}
                    onChange={e =>
                      setFormData({
                        ...formData,
                        condition: e.target.value as any
                      })
                    }
                    className="input"
                  >
                    <option value="OEM">OEM Original</option>
                    <option value="COMPATIBLE_THIRD_PARTY">Compatible Third-Party</option>
                    <option value="USED_TESTED">Used Tested / Grade A Reclaim</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Price ($)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="1"
                    required
                    value={formData.price}
                    onChange={e => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Initial Stock</label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={formData.stock}
                    onChange={e => setFormData({ ...formData, stock: parseInt(e.target.value) || 0 })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">Warranty</label>
                  <input
                    type="text"
                    required
                    value={formData.warranty}
                    onChange={e => setFormData({ ...formData, warranty: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 mb-1 block">
                  Compatible Device Models (Comma separated)
                </label>
                <input
                  type="text"
                  placeholder="iPhone 15 Pro, A2848, A3101"
                  value={formData.compatibleModels}
                  onChange={e => setFormData({ ...formData, compatibleModels: e.target.value })}
                  className="input text-xs"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-700/60">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Register Part
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
