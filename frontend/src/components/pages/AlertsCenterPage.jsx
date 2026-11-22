import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, RefreshCw, Clock, ShieldCheck, User } from 'lucide-react';
import transactionService from '../../services/transactionService';
import { useAuth } from '../../context/AuthContext';

export const AlertsCenterPage = () => {
  const { user, isAuthenticated, openAuthModal } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('ALL');

  const fetchAlerts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await transactionService.getAlertsFeed({
        status_filter: filter === 'ALL' ? undefined : filter,
        limit: 50
      });
      if (Array.isArray(data)) {
        setAlerts(data);
      }
    } catch (err) {
      setError(err.message || 'Unable to retrieve alerts.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filter, user]);

  const handleUpdateStatus = async (alertId, newStatus) => {
    try {
      await transactionService.updateAlertStatus(alertId, { status: newStatus });
      fetchAlerts();
    } catch (e) {
      alert(`Could not update alert status: ${e.message}`);
    }
  };

  const filterTabs = [
    { id: 'ALL', label: 'All' },
    { id: 'OPEN', label: 'Needs Attention' },
    { id: 'ACKNOWLEDGED', label: 'Under Review' },
    { id: 'RESOLVED', label: 'Resolved' },
    { id: 'FALSE_POSITIVE', label: 'Safe Payment (False Alarm)' }
  ];

  const getSeverityLabel = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'Very High Risk';
      case 'HIGH': return 'High Risk';
      case 'MEDIUM': return 'Medium Risk';
      case 'LOW': return 'Low Risk';
      default: return severity || 'Flagged';
    }
  };

  const getStatusLabel = (status) => {
    switch (status?.toUpperCase()) {
      case 'OPEN': return 'Needs Attention';
      case 'ACKNOWLEDGED': return 'Under Review';
      case 'RESOLVED': return 'Resolved';
      case 'FALSE_POSITIVE': return 'Safe (False Alarm)';
      default: return status || 'Unknown';
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-2 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
            Important Alerts
          </h1>
          <p className="text-xs sm:text-sm text-[#8A998A] mt-1">
            Transactions that require your attention or manual confirmation.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchAlerts}
          className="p-2.5 rounded-lg border border-[#1D3A1E] bg-[#0A120B] text-[#8A998A] hover:text-white transition-colors"
          title="Refresh Alerts"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2">
        {filterTabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setFilter(tab.id)}
            className={`px-3 py-1 rounded-md text-xs font-mono font-semibold transition-all ${
              filter === tab.id
                ? 'bg-[#1D3A1E] text-[#A0FF99] border border-[#A0FF99]/40'
                : 'bg-[#0A120B] text-[#8A998A] border border-[#1D3A1E] hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* User Alerts Scope Banner */}
      {isAuthenticated ? (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-xl bg-[#0A120B] border border-[#1D3A1E] text-xs">
          <div className="flex items-center gap-2.5 text-white">
            <span className="w-2 h-2 rounded-full bg-[#A0FF99]" />
            <span>
              Personal Security Alerts for <strong className="text-[#A0FF99]">{user?.full_name || user?.email}</strong>
              <span className="text-[#8A998A] ml-1.5 font-mono">({user?.user_identifier})</span>
            </span>
          </div>
          <span className="text-[11px] font-mono text-[#8A998A]">
            Showing only alerts flagged on your account
          </span>
        </div>
      ) : (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-xl bg-[#1D3A1E]/30 border border-[#1D3A1E] text-xs">
          <div className="flex items-center gap-2 text-[#8A998A]">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span>Public Demo Mode: Showing general evaluation alerts. Sign in to view your account alerts.</span>
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

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Alerts Feed */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-[#8A998A] space-y-2">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto text-[#A0FF99]" />
            <p>Loading alerts...</p>
          </div>
        ) : alerts.length > 0 ? (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="p-5 rounded-xl fintech-card space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-[#1D3A1E]">
                <div className="flex items-center gap-2.5">
                  <ShieldAlert className={`w-4 h-4 ${
                    alert.severity === 'CRITICAL' ? 'text-rose-500' : 'text-amber-400'
                  }`} />
                  <span className="text-xs font-bold font-mono text-white">
                    {alert.transaction_ref}
                  </span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    alert.severity === 'CRITICAL'
                      ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}>
                    {getSeverityLabel(alert.severity)}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs font-mono text-[#8A998A]">
                  <span>{new Date(alert.created_at).toLocaleString()}</span>
                  <span className="px-2 py-0.5 rounded bg-[#1D3A1E] text-white">
                    Status: <strong className="text-[#A0FF99]">{getStatusLabel(alert.status)}</strong>
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 font-mono">
                {alert.message}
              </p>

              {/* Triage Actions */}
              <div className="flex flex-wrap items-center justify-between pt-2 text-xs font-mono gap-2">
                <span className="text-[#8A998A]">Flagged Amount: ${Number(alert.amount).toFixed(2)}</span>
                
                <div className="flex items-center gap-2">
                  {alert.status === 'OPEN' && (
                    <button
                      type="button"
                      onClick={() => handleUpdateStatus(alert.id, 'ACKNOWLEDGED')}
                      className="px-2.5 py-1 rounded bg-[#1D3A1E] text-white hover:bg-[#2A522C] transition-colors"
                    >
                      Mark as Reviewed
                    </button>
                  )}
                  {alert.status !== 'RESOLVED' && (
                    <button
                      type="button"
                      onClick={() => handleUpdateStatus(alert.id, 'RESOLVED')}
                      className="px-2.5 py-1 rounded bg-[#1D3A1E] text-[#A0FF99] hover:bg-[#2A522C] transition-colors"
                    >
                      Resolve Alert
                    </button>
                  )}
                  {alert.status !== 'FALSE_POSITIVE' && (
                    <button
                      type="button"
                      onClick={() => handleUpdateStatus(alert.id, 'FALSE_POSITIVE')}
                      className="px-2.5 py-1 rounded border border-[#1D3A1E] text-[#8A998A] hover:text-white transition-colors"
                    >
                      Safe Payment (False Alarm)
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-12 text-center text-xs text-[#8A998A] space-y-3 bg-[#060B06] border border-[#1D3A1E] rounded-2xl">
            <CheckCircle2 className="w-8 h-8 text-[#A0FF99] mx-auto" />
            <p className="font-semibold text-white text-sm">No Security Alerts Flagged</p>
            <p className="max-w-md mx-auto text-[#8A998A]">
              {isAuthenticated
                ? "All transactions evaluated under your account are operating within normal risk parameters. No suspicious activity has been detected."
                : "No alerts match the selected status filter."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertsCenterPage;