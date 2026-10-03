import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  Bell,
  Activity,
  ShieldCheck,
  CheckCheck,
  Zap,
  X,
  FileText,
  Wrench,
  DollarSign,
  ShieldAlert,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

interface NotificationItem {
  id: number;
  event_type: string;
  title: string;
  message: string;
  is_read: boolean;
  time: string;
  category: 'repair' | 'quote' | 'warranty' | 'resale';
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 1,
    event_type: 'QUOTE_APPROVED',
    title: 'Quote Approved by Customer',
    message: 'Alice Customer approved quote v1 ($220.00) for Samsung Galaxy S23.',
    is_read: false,
    time: '5 mins ago',
    category: 'quote'
  },
  {
    id: 2,
    event_type: 'REPAIR_STARTED',
    title: 'Repair Started',
    message: "Bob's Micro Repairs began logic board rework on Dell Inspiron 15.",
    is_read: false,
    time: '25 mins ago',
    category: 'repair'
  },
  {
    id: 3,
    event_type: 'RESALE_QUOTE_AVAILABLE',
    title: 'Resale Valuation Ready',
    message: 'AI trade-in offer of $420.00 computed for Samsung Galaxy S22 Ultra.',
    is_read: true,
    time: '2 hours ago',
    category: 'resale'
  },
  {
    id: 4,
    event_type: 'WARRANTY_STARTED',
    title: 'Warranty Protection Activated',
    message: '180 days parts & labor guarantee anchored to DPP-00001.',
    is_read: true,
    time: '1 day ago',
    category: 'warranty'
  }
];

const DOMAIN_EVENTS = [
  { key: 'REPAIR_REQUEST_CREATED', label: '1. Request Created', cat: 'repair' },
  { key: 'TECHNICIAN_ACCEPTED', label: '2. Tech Accepted', cat: 'repair' },
  { key: 'QUOTE_RECEIVED', label: '3. Quote Ready', cat: 'quote' },
  { key: 'QUOTE_APPROVED', label: '4. Quote Approved', cat: 'quote' },
  { key: 'REPAIR_STARTED', label: '5. Repair Started', cat: 'repair' },
  { key: 'PARTS_REQUIRED', label: '6. Parts Required', cat: 'repair' },
  { key: 'REPAIR_COMPLETED', label: '7. Repair Finished', cat: 'repair' },
  { key: 'WARRANTY_STARTED', label: '8. Warranty Active', cat: 'warranty' },
  { key: 'RESALE_QUOTE_AVAILABLE', label: '9. Resale Valuation', cat: 'resale' },
  { key: 'RESALE_STATUS_CHANGED', label: '10. Resale Status', cat: 'resale' }
];

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  const { user } = useAuth();
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const [isFlyoutOpen, setIsFlyoutOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'UNREAD' | 'repair' | 'quote' | 'warranty' | 'resale'>('ALL');
  const flyoutRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/v1/health', {
          method: 'GET',
        });
        setIsBackendOnline(res.ok);
      } catch {
        setIsBackendOnline(false);
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  // Close flyout on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (flyoutRef.current && !flyoutRef.current.contains(e.target as Node)) {
        setIsFlyoutOpen(false);
      }
    };
    if (isFlyoutOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [isFlyoutOpen]);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
  };

  const markSingleRead = (id: number) => {
    setNotifications(prev => prev.map(n => (n.id === id ? { ...n, is_read: true } : n)));
  };

  const triggerSimulatorEvent = (eventKey: string, cat: string) => {
    const newNotif: NotificationItem = {
      id: Date.now(),
      event_type: eventKey,
      title: eventKey.replace(/_/g, ' '),
      message: `Simulated live domain event [${eventKey}] broadcasted to all subscribed administrative listeners.`,
      is_read: false,
      time: 'Just now',
      category: cat as any
    };
    setNotifications(prev => [newNotif, ...prev]);
  };

  const filteredNotifs = notifications.filter(n => {
    if (activeFilter === 'UNREAD') return !n.is_read;
    if (activeFilter === 'ALL') return true;
    return n.category === activeFilter;
  });

  return (
    <header className="h-[72px] bg-[#0F172A] border-b border-slate-800 px-7 flex items-center justify-between sticky top-0 z-50">
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-tight">{title || 'Dashboard'}</h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Search input */}
        <div className="hidden md:flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 rounded-xl px-3.5 py-1.5 w-64">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search resources (Ctrl+K)..."
            className="bg-transparent border-none outline-none text-xs text-white placeholder-slate-500 w-full"
          />
        </div>

        {/* Server status pill */}
        <div className="flex items-center gap-2 bg-slate-800/40 border border-slate-700/50 px-3 py-1.5 rounded-full">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendOnline ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50 animate-pulse' : 'bg-amber-400'
            }`}
          />
          <span className="text-xs font-semibold text-slate-300">
            {isBackendOnline ? 'API Active' : 'Offline / Mock'}
          </span>
        </div>

        {/* Notification Bell with interactive Flyout */}
        <div className="relative" ref={flyoutRef}>
          <button
            onClick={() => setIsFlyoutOpen(!isFlyoutOpen)}
            className={`relative p-2.5 rounded-xl border transition-all ${
              isFlyoutOpen
                ? 'bg-indigo-600/20 border-indigo-500 text-indigo-400'
                : 'bg-slate-800/80 border-slate-700/60 text-slate-300 hover:text-white hover:bg-slate-700/80'
            }`}
            title="In-App Notifications"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-indigo-500 text-white font-bold text-[10px] w-5 h-5 rounded-full flex items-center justify-center border-2 border-[#0F172A] shadow-md animate-scale-in">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Floating Notification Center Flyout */}
          {isFlyoutOpen && (
            <div className="absolute right-0 mt-3 w-96 max-w-[90vw] glass-panel bg-[#0B0F17]/95 backdrop-blur-xl border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden z-50 animate-fade-in">
              {/* Flyout Header */}
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-indigo-400" />
                  <span className="font-bold text-white text-sm">Notifications & Events</span>
                  {unreadCount > 0 && (
                    <span className="badge badge-blue text-[10px] py-0 px-1.5">{unreadCount} New</span>
                  )}
                </div>
                <button
                  onClick={markAllRead}
                  disabled={unreadCount === 0}
                  className="text-xs text-indigo-400 hover:text-indigo-300 disabled:text-slate-600 font-semibold inline-flex items-center gap-1"
                >
                  <CheckCheck className="w-3.5 h-3.5" /> Mark read
                </button>
              </div>

              {/* Event Simulator Strip */}
              <div className="bg-indigo-950/40 p-3 border-b border-indigo-900/30">
                <div className="text-[11px] font-bold text-indigo-300 mb-1.5 flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-amber-400" /> Quick Broadcast Simulator:
                </div>
                <div className="flex gap-1 overflow-x-auto pb-1">
                  {DOMAIN_EVENTS.map(evt => (
                    <button
                      key={evt.key}
                      onClick={() => triggerSimulatorEvent(evt.key, evt.cat)}
                      className="px-2 py-1 rounded bg-slate-800/90 text-[10px] font-semibold text-slate-300 hover:text-white hover:bg-indigo-600 border border-slate-700 whitespace-nowrap transition-all"
                    >
                      {evt.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Category Filter Pills */}
              <div className="flex items-center gap-1 p-2 bg-slate-900/60 border-b border-slate-800/80 overflow-x-auto">
                {[
                  { key: 'ALL', label: 'All' },
                  { key: 'UNREAD', label: `Unread (${unreadCount})` },
                  { key: 'repair', label: 'Repairs' },
                  { key: 'quote', label: 'Quotes' },
                  { key: 'resale', label: 'Resale' }
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveFilter(tab.key as any)}
                    className={`px-2.5 py-1 rounded-md text-[11px] font-semibold whitespace-nowrap transition-all ${
                      activeFilter === tab.key
                        ? 'bg-indigo-600 text-white'
                        : 'text-slate-400 hover:text-white hover:bg-slate-800'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Notification Items List */}
              <div className="max-h-80 overflow-y-auto divide-y divide-slate-800/60">
                {filteredNotifs.map(item => (
                  <div
                    key={item.id}
                    onClick={() => markSingleRead(item.id)}
                    className={`p-3.5 transition-colors cursor-pointer flex gap-3 ${
                      item.is_read ? 'hover:bg-slate-800/40 opacity-70' : 'bg-slate-800/50 hover:bg-slate-800/80'
                    }`}
                  >
                    <div
                      className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                        item.is_read ? 'bg-transparent' : 'bg-indigo-400 shadow-sm shadow-indigo-400'
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-1">
                        <span className="font-semibold text-xs text-white truncate">{item.title}</span>
                        <span className="text-[10px] text-slate-500 shrink-0">{item.time}</span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 line-clamp-2 leading-relaxed">{item.message}</p>
                    </div>
                  </div>
                ))}

                {filteredNotifs.length === 0 && (
                  <div className="text-center py-8 text-slate-500 text-xs">
                    No notifications in this category.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Admin Badge */}
        <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4" />
          <span className="hidden sm:inline">Admin Access Verified</span>
        </div>
      </div>
    </header>
  );
};
