import React, { useState, useEffect } from 'react';
import { History, Download, RefreshCw, Filter, ArrowUpRight, Clock, ShieldCheck, User } from 'lucide-react';
import transactionService from '../../services/transactionService';
import { useAuth } from '../../context/AuthContext';

export const TransactionHistoryPage = () => {
  const { user, isAuthenticated, openAuthModal } = useAuth();
  const [records, setRecords] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [page, setPage] = useState(1);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await transactionService.getTransactionHistory({ page, limit: 25 });
      if (data && Array.isArray(data.records)) {
        setRecords(data.records);
      }
    } catch (err) {
      setError(err.message || 'Failed to retrieve past transactions.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, user]); // Refetch when page or user changes

  const handleDownloadCsv = async () => {
    try {
      setIsDownloading(true);
      await transactionService.downloadCsv();
    } catch (err) {
      setError(err.message || 'Failed to download CSV export.');
    } finally {
      setIsDownloading(false);
    }
  };

  const filteredRecords = filterCategory === 'ALL'
    ? records
    : records.filter((r) => r.risk_category?.toUpperCase() === filterCategory);

  const categoryFilterOptions = [
    { id: 'ALL', label: 'All' },
    { id: 'LOW', label: 'Safe (Low)' },
    { id: 'MEDIUM', label: 'Medium' },
    { id: 'HIGH', label: 'High' },
    { id: 'CRITICAL', label: 'Very High' }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 py-2 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
            Past Transactions
          </h1>
          <p className="text-xs sm:text-sm text-[#8A998A] mt-1">
            Search and review all evaluated payments recorded in your secure ledger.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fetchHistory}
            className="p-2.5 rounded-lg border border-[#1D3A1E] bg-[#0A120B] text-[#8A998A] hover:text-white transition-colors"
            title="Refresh List"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <button
            type="button"
            onClick={handleDownloadCsv}
            disabled={isDownloading}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors disabled:opacity-50"
          >
            <Download className={`w-4 h-4 ${isDownloading ? 'animate-bounce' : ''}`} />
            <span>{isDownloading ? 'Preparing CSV...' : 'Download Past Transactions (CSV)'}</span>
          </button>
        </div>
      </div>

      {/* User Ledger Scope Banner */}
      {isAuthenticated ? (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-xl bg-[#0A120B] border border-[#1D3A1E] text-xs">
          <div className="flex items-center gap-2.5 text-white">
            <span className="w-2 h-2 rounded-full bg-[#A0FF99]" />
            <span>
              Personal Ledger for <strong className="text-[#A0FF99]">{user?.full_name || user?.email}</strong>
              <span className="text-[#8A998A] ml-1.5 font-mono">({user?.user_identifier})</span>
            </span>
          </div>
          <span className="text-[11px] font-mono text-[#8A998A]">
            Showing only transactions evaluated under your account
          </span>
        </div>
      ) : (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-xl bg-[#1D3A1E]/30 border border-[#1D3A1E] text-xs">
          <div className="flex items-center gap-2 text-[#8A998A]">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span>Public Demo Mode: Showing general evaluation records. Sign in to view your personal ledger.</span>
          </div>
          <button
            type="button"
            onClick={() => openAuthModal('login')}
            className="px-3 py-1 rounded bg-[#A0FF99] text-[#020202] text-xs font-semibold hover:bg-[#B8FFB3] transition-colors w-fit"
          >
            Sign In
          </button>
        </div>
      )}

      {/* Filter Chips */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-mono text-[#8A998A] mr-2 flex items-center gap-1">
          <Filter className="w-3.5 h-3.5" /> Risk Level:
        </span>
        {categoryFilterOptions.map((opt) => (
          <button
            key={opt.id}
            type="button"
            onClick={() => setFilterCategory(opt.id)}
            className={`px-3 py-1 rounded-md text-xs font-mono font-semibold transition-all ${
              filterCategory === opt.id
                ? 'bg-[#1D3A1E] text-[#A0FF99] border border-[#A0FF99]/40'
                : 'bg-[#0A120B] text-[#8A998A] border border-[#1D3A1E] hover:text-white'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Ledger Table */}
      <div className="rounded-xl border border-[#1D3A1E] overflow-hidden fintech-card">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-[#8A998A] space-y-2">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto text-[#A0FF99]" />
            <p>Loading past transactions from database...</p>
          </div>
        ) : filteredRecords.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#1D3A1E]/50 text-[#8A998A] border-b border-[#1D3A1E]">
                <tr>
                  <th className="py-3.5 px-4 font-semibold">Payment ID</th>
                  <th className="py-3.5 px-4 font-semibold">Date & Time</th>
                  <th className="py-3.5 px-4 font-semibold">Amount</th>
                  <th className="py-3.5 px-4 font-semibold">City</th>
                  <th className="py-3.5 px-4 font-semibold">Payment Method</th>
                  <th className="py-3.5 px-4 font-semibold">Known Device?</th>
                  <th className="py-3.5 px-4 font-semibold">Risk Level</th>
                  <th className="py-3.5 px-4 font-semibold text-right">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1D3A1E] text-white">
                {filteredRecords.map((tx) => (
                  <tr key={tx.id || tx.transaction_ref} className="hover:bg-[#122314] transition-colors">
                    <td className="py-3 px-4 font-semibold text-[#A0FF99]">{tx.transaction_ref}</td>
                    <td className="py-3 px-4 text-[#8A998A]">
                      {new Date(tx.timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 font-bold">${Number(tx.amount).toFixed(2)}</td>
                    <td className="py-3 px-4 text-[#8A998A]">{tx.location_city}</td>
                    <td className="py-3 px-4 capitalize">{tx.payment_method?.replace('_', ' ')}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        tx.is_device_familiar ? 'bg-[#1D3A1E] text-[#A0FF99]' : 'bg-rose-500/20 text-rose-300'
                      }`}>
                        {tx.is_device_familiar ? 'Yes (Known)' : 'New Device'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-bold">{Number(tx.risk_score).toFixed(1)}</span>
                      <span className="text-[#8A998A]"> / 100</span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        tx.recommended_action === 'APPROVE' ? 'bg-[#1D3A1E] text-[#A0FF99]' :
                        tx.recommended_action === 'REVIEW' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-rose-500/20 text-rose-400'
                      }`}>
                        {tx.recommended_action === 'APPROVE' ? 'Approved (Safe)' :
                         tx.recommended_action === 'REVIEW' ? 'Needs Review' :
                         'Blocked'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-xs text-[#8A998A] space-y-2">
            <Clock className="w-6 h-6 text-[#8A998A] mx-auto" />
            <p>No transactions match the selected filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionHistoryPage;