import React, { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, FileSpreadsheet, CheckCircle2 } from 'lucide-react';
import transactionService from '../../services/transactionService';

export const ReportsPage = () => {
  const [records, setRecords] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloadingCsv, setIsDownloadingCsv] = useState(false);
  const [downloadingPdfRef, setDownloadingPdfRef] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const fetchRecords = async () => {
      try {
        const data = await transactionService.getTransactionHistory({ page: 1, limit: 15 });
        if (isMounted && data && Array.isArray(data.records)) {
          setRecords(data.records);
        }
      } catch (e) {
        if (isMounted) setErrorMessage(e.message || 'Could not load reports list.');
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    fetchRecords();
    return () => { isMounted = false; };
  }, []);

  const handleDownloadCsv = async () => {
    setIsDownloadingCsv(true);
    setErrorMessage(null);
    try {
      await transactionService.downloadCsv();
    } catch (e) {
      setErrorMessage(e.message || 'Failed to download CSV report.');
    } finally {
      setIsDownloadingCsv(false);
    }
  };

  const handleDownloadPdf = async (ref) => {
    setDownloadingPdfRef(ref);
    setErrorMessage(null);
    try {
      await transactionService.downloadPdf(ref);
    } catch (e) {
      setErrorMessage(e.message || 'Failed to download PDF report.');
    } finally {
      setDownloadingPdfRef(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-2 select-none">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
            Reports & Downloads
          </h1>
          <p className="text-xs sm:text-sm text-[#8A998A] mt-1">
            Download your payment data as a CSV spreadsheet or get clear, printable PDF safety summaries.
          </p>
        </div>

        <button
          type="button"
          onClick={handleDownloadCsv}
          disabled={isDownloadingCsv}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors disabled:opacity-50"
        >
          <FileSpreadsheet className={`w-4 h-4 ${isDownloadingCsv ? 'animate-spin' : ''}`} />
          <span>{isDownloadingCsv ? 'Exporting CSV...' : 'Download All Past Transactions (CSV)'}</span>
        </button>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-xs text-[#FCA5A5]">
          {errorMessage}
        </div>
      )}

      {/* Report Info Banner */}
      <div className="p-6 rounded-xl fintech-card space-y-3">
        <h3 className="text-sm font-bold text-white">
          Downloadable Safety Summaries (PDF)
        </h3>
        <p className="text-xs text-[#8A998A] leading-relaxed">
          Every payment analyzed by TransactionGuard AI comes with a complete safety summary. Click 'Download PDF' next to any transaction below to save or print an official report.
        </p>
      </div>

      {/* Transaction List with PDF download links */}
      <div className="space-y-3">
        <h3 className="text-xs font-mono font-semibold uppercase tracking-wider text-[#8A998A]">
          Recent Transactions Ready for Download
        </h3>

        {isLoading ? (
          <div className="p-8 text-center text-xs text-[#8A998A]">
            <RefreshCw className="w-5 h-5 animate-spin mx-auto text-[#A0FF99] mb-2" />
            Loading past transactions...
          </div>
        ) : records.length > 0 ? (
          <div className="rounded-xl border border-[#1D3A1E] overflow-hidden fintech-card">
            <div className="divide-y divide-[#1D3A1E]">
              {records.map((tx) => (
                <div
                  key={tx.id || tx.transaction_ref}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#122314] transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-white">{tx.transaction_ref}</span>
                      <span className="text-xs text-[#8A998A] font-mono">• ${Number(tx.amount).toFixed(2)} {tx.currency}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        tx.recommended_action === 'APPROVE' ? 'bg-[#1D3A1E] text-[#A0FF99]' :
                        tx.recommended_action === 'REVIEW' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-rose-500/20 text-rose-400'
                      }`}>
                        {tx.risk_category === 'LOW' ? 'Low Risk' :
                         tx.risk_category === 'MEDIUM' ? 'Medium Risk' :
                         tx.risk_category === 'HIGH' ? 'High Risk' :
                         'Very High Risk'}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#8A998A] font-mono">
                      City: {tx.location_city} | Payment Method: {tx.payment_method?.replace('_', ' ')} | Risk Level: {Number(tx.risk_score).toFixed(1)}/100
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDownloadPdf(tx.transaction_ref)}
                    disabled={downloadingPdfRef === tx.transaction_ref}
                    className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-[#1D3A1E] bg-[#0A120B] text-xs font-mono text-[#A0FF99] hover:bg-[#1D3A1E] transition-colors shrink-0 disabled:opacity-50"
                  >
                    <Download className={`w-3.5 h-3.5 ${downloadingPdfRef === tx.transaction_ref ? 'animate-bounce' : ''}`} />
                    <span>{downloadingPdfRef === tx.transaction_ref ? 'Exporting...' : 'Download PDF'}</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-[#8A998A] fintech-card rounded-xl">
            No transactions found yet. Check a transaction first to generate a safety report.
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;