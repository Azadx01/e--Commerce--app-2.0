import React, { useState } from 'react';
import Head from 'next/head';
import {
  Star,
  Search,
  Filter,
  CheckCircle,
  Flag,
  MessageSquare,
  Sparkles,
  Smile,
  Meh,
  Frown,
  User,
  Wrench,
  EyeOff
} from 'lucide-react';
import { INITIAL_REVIEWS, ReviewItem } from '../lib/mockData';

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<ReviewItem[]>(INITIAL_REVIEWS);
  const [search, setSearch] = useState('');
  const [ratingFilter, setRatingFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filtered = reviews.filter(r => {
    const matchesSearch =
      r.customerName.toLowerCase().includes(search.toLowerCase()) ||
      r.technicianName.toLowerCase().includes(search.toLowerCase()) ||
      r.repairCode.toLowerCase().includes(search.toLowerCase()) ||
      r.comment.toLowerCase().includes(search.toLowerCase());
    const matchesRating = ratingFilter === 'ALL' || r.rating.toString() === ratingFilter;
    const matchesStatus = statusFilter === 'ALL' || r.status === statusFilter;
    return matchesSearch && matchesRating && matchesStatus;
  });

  const handleToggleFlag = (id: number) => {
    setReviews(prev =>
      prev.map(r => {
        if (r.id === id) {
          return {
            ...r,
            status: r.status === 'PUBLISHED' ? 'FLAGGED' : 'PUBLISHED'
          };
        }
        return r;
      })
    );
  };

  const avgRating = (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1);

  const sentimentBadges: Record<string, { label: string; icon: any; class: string }> = {
    POSITIVE: { label: 'Positive', icon: Smile, class: 'badge-emerald' },
    NEUTRAL: { label: 'Neutral', icon: Meh, class: 'badge-blue' },
    NEGATIVE: { label: 'Negative', icon: Frown, class: 'badge-rose' }
  };

  const statusBadges: Record<string, { label: string; class: string }> = {
    PUBLISHED: { label: 'Published Live', class: 'badge-emerald' },
    FLAGGED: { label: 'Flagged for Moderation', class: 'badge-rose' },
    RESOLVED: { label: 'Resolved / Suppressed', class: 'badge-slate' }
  };

  return (
    <>
      <Head>
        <title>Customer Reviews & Feedback | ReVivo Admin</title>
      </Head>

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
              <Star className="w-7 h-7 text-amber-400 fill-amber-400" />
              Customer Reviews & Reputation Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Monitor technician service quality ratings, sentiment analyses, and moderate flagged feedback.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Average Platform Rating</div>
            <div className="flex items-center gap-2 mt-1">
              <div className="text-2xl font-bold text-amber-400">{avgRating}</div>
              <div className="flex text-amber-400">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400" />
                ))}
              </div>
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Total Reviews</div>
            <div className="text-xl font-bold text-white mt-1">{reviews.length}</div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Positive Sentiment</div>
            <div className="text-xl font-bold text-emerald-400 mt-1">
              {Math.round((reviews.filter(r => r.sentiment === 'POSITIVE').length / reviews.length) * 100)}%
            </div>
          </div>
          <div className="glass-panel p-4 rounded-xl">
            <div className="text-xs text-slate-400 font-medium">Flagged Reviews</div>
            <div className="text-xl font-bold text-rose-400 mt-1">
              {reviews.filter(r => r.status === 'FLAGGED').length}
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
              placeholder="Search feedback text, customer, technician..."
              className="input pl-10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-slate-400 font-medium">Rating:</span>
              {['ALL', '5', '4', '3'].map(stars => (
                <button
                  key={stars}
                  onClick={() => setRatingFilter(stars)}
                  className={`px-2.5 py-1 rounded text-xs font-semibold ${
                    ratingFilter === stars
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {stars === 'ALL' ? 'All' : `${stars} ★`}
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
                <option value="PUBLISHED">Published</option>
                <option value="FLAGGED">Flagged</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Customer & Repair #</th>
                <th>Assigned Technician</th>
                <th>Score</th>
                <th>Customer Feedback</th>
                <th>Sentiment</th>
                <th>Status</th>
                <th>Date</th>
                <th className="text-right">Moderation</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(review => {
                const SentimentIcon = sentimentBadges[review.sentiment]?.icon || Smile;
                return (
                  <tr key={review.id}>
                    <td>
                      <div>
                        <div className="font-semibold text-white text-sm">
                          {review.customerName}
                        </div>
                        <span className="font-mono text-xs text-indigo-400">
                          {review.repairCode}
                        </span>
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5 text-xs text-slate-200">
                        <Wrench className="w-3.5 h-3.5 text-slate-400" />
                        {review.technicianName}
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <div className="flex text-amber-400">
                          {[...Array(review.rating)].map((_, i) => (
                            <Star key={i} className="w-3.5 h-3.5 fill-amber-400" />
                          ))}
                        </div>
                        <span className="text-xs font-bold text-slate-300 ml-1">
                          {review.rating}.0
                        </span>
                      </div>
                    </td>
                    <td>
                      <p className="text-xs text-slate-200 line-clamp-2 max-w-sm italic">
                        &ldquo;{review.comment}&rdquo;
                      </p>
                    </td>
                    <td>
                      <span className={`badge ${sentimentBadges[review.sentiment]?.class} flex items-center gap-1 w-fit`}>
                        <SentimentIcon className="w-3 h-3" />
                        {sentimentBadges[review.sentiment]?.label}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${statusBadges[review.status]?.class}`}>
                        {statusBadges[review.status]?.label}
                      </span>
                    </td>
                    <td>
                      <span className="text-xs text-slate-400">{review.date}</span>
                    </td>
                    <td className="text-right">
                      <button
                        onClick={() => handleToggleFlag(review.id)}
                        className={`btn text-xs py-1 px-2.5 inline-flex items-center gap-1.5 ${
                          review.status === 'FLAGGED'
                            ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                            : 'btn-secondary text-rose-400 hover:border-rose-500/50'
                        }`}
                      >
                        <Flag className="w-3.5 h-3.5" />
                        {review.status === 'FLAGGED' ? 'Approve' : 'Flag'}
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} className="text-center py-12 text-slate-500">
                    No customer reviews match the selected filter.
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
