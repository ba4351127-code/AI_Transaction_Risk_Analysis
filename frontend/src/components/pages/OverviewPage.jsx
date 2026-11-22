import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, 
  ArrowUpRight, 
  Search, 
  FileText, 
  Clock, 
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  HelpCircle
} from 'lucide-react';
import transactionService from '../../services/transactionService';

export const OverviewPage = ({ onStartAnalysis, onNavigate }) => {
  const [recentTransactions, setRecentTransactions] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchRecent = async () => {
      try {
        const data = await transactionService.getTransactionHistory({ page: 1, limit: 5 });
        if (isMounted && data && Array.isArray(data.records)) {
          setRecentTransactions(data.records);
        }
      } catch (e) {
      } finally {
        if (isMounted) setIsLoadingHistory(false);
      }
    };
    fetchRecent();
    return () => { isMounted = false; };
  }, []);

  const safetyLayers = [
    {
      num: '01',
      title: 'Instant Safety Rules',
      category: 'Speed & Limit Checks',
      desc: 'Catches impossible travel speeds (like a payment in Tokyo an hour after one in London) and sudden spending spikes that are far higher than normal.'
    },
    {
      num: '02',
      title: 'Pattern Matcher',
      category: 'AI Detection System',
      desc: 'Compares the payment against thousands of verified patterns to spot telltale signs of stolen cards or unauthorized account access.'
    },
    {
      num: '03',
      title: 'Unusual Activity Finder',
      category: 'New Threat Detection',
      desc: 'Identifies completely new and unexpected fraud techniques that have never been seen before, even if no rule specifically blocks them.'
    },
    {
      num: '04',
      title: 'Your Normal Habits',
      category: 'Personal Profile',
      desc: 'Learns your typical transaction amounts, favorite merchant categories, and typical shopping hours so unusual deviations stand out immediately.'
    }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-16 py-4 select-none">
      
      {/* 1. Header Section */}
      <section className="space-y-6 pt-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[#1D3A1E] text-[#A0FF99]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99]" />
          <span>Real-Time Payment Security</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white leading-[1.1] font-sans">
          Every Payment, <br />
          <span className="text-[#A0FF99]">Checked in Seconds.</span>
        </h1>

        <p className="text-base sm:text-lg text-[#8A998A] max-w-2xl leading-relaxed">
          TransactionGuard checks payments in real time to catch suspicious activity before money leaves an account. It provides clear, plain-English reasons for every decision so you always know why a payment was approved, reviewed, or stopped.
        </p>

        <div className="flex flex-wrap items-center gap-4 pt-2">
          <button
            type="button"
            onClick={onStartAnalysis}
            className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-lg font-semibold text-sm bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors"
          >
            <Search className="w-4 h-4" />
            <span>Check a Transaction</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={() => onNavigate('history')}
            className="inline-flex items-center gap-2 px-5 py-3.5 rounded-lg font-medium text-sm border border-[#1D3A1E] text-white hover:bg-[#1D3A1E] transition-colors"
          >
            <Clock className="w-4 h-4 text-[#A0FF99]" />
            <span>View Past Transactions</span>
          </button>
        </div>
      </section>

      {/* 2. Four Protection Layers */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
          <div>
            <span className="text-xs font-mono font-semibold text-[#A0FF99] uppercase tracking-wider block">
              How You Are Protected
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">
              Four Levels of Payment Security
            </h2>
          </div>
          <p className="text-xs text-[#8A998A] max-w-sm">
            Every transaction goes through four simultaneous checks in less than a second to ensure it is authentic and safe.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {safetyLayers.map((layer) => (
            <div
              key={layer.num}
              className="p-6 rounded-xl fintech-card space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#A0FF99]">
                  CHECK {layer.num}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#1D3A1E] text-white">
                  {layer.category}
                </span>
              </div>
              <h3 className="text-base font-bold text-white">
                {layer.title}
              </h3>
              <p className="text-xs text-[#8A998A] leading-relaxed">
                {layer.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. Recent Real Transactions */}
      <section className="space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1D3A1E]">
          <div>
            <span className="text-xs font-mono font-semibold text-[#A0FF99] uppercase tracking-wider block">
              Recent Activity
            </span>
            <h2 className="text-xl font-bold text-white">
              Recently Checked Payments
            </h2>
          </div>

          <button
            type="button"
            onClick={() => onNavigate('history')}
            className="inline-flex items-center gap-1.5 text-xs text-[#A0FF99] hover:underline font-mono"
          >
            <span>See all past payments</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recentTransactions.length > 0 ? (
          <div className="rounded-xl border border-[#1D3A1E] overflow-hidden">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#1D3A1E]/50 text-[#8A998A] border-b border-[#1D3A1E]">
                <tr>
                  <th className="py-3 px-4 font-semibold">Payment ID</th>
                  <th className="py-3 px-4 font-semibold">Amount</th>
                  <th className="py-3 px-4 font-semibold">City</th>
                  <th className="py-3 px-4 font-semibold">Payment Method</th>
                  <th className="py-3 px-4 font-semibold">Risk Level</th>
                  <th className="py-3 px-4 font-semibold text-right">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1D3A1E] text-white">
                {recentTransactions.map((tx) => {
                  const getActionText = (action) => {
                    if (action === 'APPROVE') return 'Approved (Safe)';
                    if (action === 'REVIEW') return 'Needs Review';
                    if (action === 'BLOCK') return 'Blocked (Unsafe)';
                    if (action === 'FREEZE') return 'Stopped Immediately';
                    return action || 'Checked';
                  };

                  return (
                    <tr key={tx.id || tx.transaction_ref} className="hover:bg-[#122314] transition-colors">
                      <td className="py-3 px-4 font-semibold text-[#A0FF99]">{tx.transaction_ref}</td>
                      <td className="py-3 px-4 font-bold">${Number(tx.amount).toFixed(2)}</td>
                      <td className="py-3 px-4 text-[#8A998A]">{tx.location_city}</td>
                      <td className="py-3 px-4 capitalize">{tx.payment_method?.replace('_', ' ')}</td>
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
                          {getActionText(tx.recommended_action)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 rounded-xl border border-[#1D3A1E] bg-[#0A120B] text-center space-y-2">
            <Clock className="w-6 h-6 text-[#8A998A] mx-auto" />
            <p className="text-xs text-[#8A998A]">
              {isLoadingHistory ? 'Loading payments...' : 'No payments checked yet. Run your first check below.'}
            </p>
            <button
              type="button"
              onClick={onStartAnalysis}
              className="text-xs text-[#A0FF99] hover:underline font-semibold"
            >
              Check your first transaction ➔
            </button>
          </div>
        )}
      </section>

    </div>
  );
};

export default OverviewPage;
