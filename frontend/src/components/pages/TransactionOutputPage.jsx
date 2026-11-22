import React, { useState } from 'react';
import { 
  ArrowLeft, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Download, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  Cpu, 
  UserCheck, 
  Lock, 
  BarChart2, 
  FileText 
} from 'lucide-react';
import { usePersona } from '../../context/PersonaContext';
import RiskGauge from '../common/RiskGauge';
import ShapWaterfallChart from '../common/ShapWaterfallChart';
import transactionService from '../../services/transactionService';

export const TransactionOutputPage = ({ assessment, onNewAnalysis }) => {
  const { isAnalyst } = usePersona();
  const [showJsonSnapshot, setShowJsonSnapshot] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);

  const handleDownloadPdf = async () => {
    if (!assessment?.transaction_ref) return;
    setIsDownloadingPdf(true);
    try {
      await transactionService.downloadPdf(assessment.transaction_ref);
    } catch (e) {
      alert(`Could not download safety report: ${e.message}`);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  if (!assessment) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center space-y-5 select-none">
        <div className="w-14 h-14 mx-auto rounded-xl bg-[#0A120B] border border-[#1D3A1E] flex items-center justify-center text-[#8A998A]">
          <FileText className="w-6 h-6 text-[#A0FF99]" />
        </div>
        <h2 className="text-xl font-bold text-white">
          No Transaction Checked Yet
        </h2>
        <p className="text-xs text-[#8A998A] max-w-sm mx-auto">
          Please enter transaction details to check if it is safe or flagged for review.
        </p>
        <button
          type="button"
          onClick={onNewAnalysis}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Check a Transaction</span>
        </button>
      </div>
    );
  }

  const {
    transaction_ref,
    user_identifier,
    overall_risk_score = 0,
    risk_category = 'LOW',
    recommended_action = 'APPROVE',
    everyday_user = {},
    risk_analyst = {},
    evaluated_at
  } = assessment;

  const {
    model_signals = {},
    top_shap_contributions = [],
    rules_triggered = [],
    technical_summary = '',
    feature_vector_snapshot = {}
  } = risk_analyst;

  // Simplified Status Badges and Next Step Recommendations
  const getActionBadge = (action, category) => {
    switch (action?.toUpperCase()) {
      case 'APPROVE':
        return {
          bg: 'bg-[#1D3A1E] text-[#A0FF99] border-[#A0FF99]/30',
          icon: CheckCircle2,
          label: 'Approved (Safe)',
          suggestion: 'No action needed. This transaction looks safe.'
        };
      case 'REVIEW':
        return {
          bg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
          icon: AlertTriangle,
          label: 'Needs Review',
          suggestion: 'We recommend verifying this payment with the customer.'
        };
      case 'BLOCK':
      case 'FREEZE':
        if (category === 'CRITICAL' || category === 'VERY_HIGH') {
          return {
            bg: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
            icon: ShieldAlert,
            label: 'Very High Risk – Stop Immediately',
            suggestion: 'This transaction appears very risky. Consider cancelling or freezing the card.'
          };
        }
        return {
          bg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
          icon: ShieldAlert,
          label: 'High Risk – Block Recommended',
          suggestion: 'This transaction shows strong fraud signals. We recommend blocking it.'
        };
      default:
        return {
          bg: 'bg-[#1D3A1E] text-white border-[#1D3A1E]',
          icon: CheckCircle2,
          label: 'Checked',
          suggestion: 'Review details below.'
        };
    }
  };

  const actionInfo = getActionBadge(recommended_action, risk_category);
  const ActionIcon = actionInfo.icon;

  return (
    <div className="max-w-5xl mx-auto space-y-8 py-2 select-none">
      
      {/* Top Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
              Why Was This Transaction Flagged?
            </h1>
            <span className="font-mono text-xs font-bold px-3 py-1 rounded-md bg-[#1D3A1E] text-[#A0FF99] border border-[#1D3A1E]">
              {transaction_ref}
            </span>
          </div>

          <div className="flex items-center gap-3 text-xs text-[#8A998A] font-mono">
            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[#8A998A]" />
              {evaluated_at ? new Date(evaluated_at).toLocaleString() : 'Just checked'}
            </span>
            {user_identifier && (
              <span>• Account: <strong className="text-white">{user_identifier}</strong></span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onNewAnalysis}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold border border-[#1D3A1E] bg-[#0A120B] text-[#8A998A] hover:text-white hover:bg-[#122314] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Check Another Transaction</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={isDownloadingPdf}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors disabled:opacity-50"
          >
            <Download className={`w-4 h-4 ${isDownloadingPdf ? 'animate-bounce' : ''}`} />
            <span>{isDownloadingPdf ? 'Downloading PDF...' : 'Download Safety Report (PDF)'}</span>
          </button>
        </div>
      </div>

      {/* Main Score & Decision Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Radial Calibrated Risk Gauge */}
        <div className="lg:col-span-5 fintech-card rounded-xl p-6 flex flex-col items-center justify-between space-y-4">
          <div className="w-full flex items-center justify-between pb-3 border-b border-[#1D3A1E] text-xs font-semibold text-[#8A998A] uppercase tracking-wider font-mono">
            <span>Overall Risk Level</span>
            <span className="text-[10px] text-[#A0FF99] font-mono flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99]" />
              Instant Safety Check
            </span>
          </div>

          <div className="py-2">
            <RiskGauge score={overall_risk_score} category={risk_category} size={280} />
          </div>

          {/* Action Badge */}
          <div className={`w-full py-2.5 px-4 rounded-lg border flex items-center justify-center gap-2 text-xs font-bold tracking-wider ${actionInfo.bg}`}>
            <ActionIcon className="w-4 h-4 shrink-0" />
            <span>{actionInfo.label}</span>
          </div>
        </div>

        {/* Right Column: Clear Explanations & Next Steps */}
        <div className="lg:col-span-7 fintech-card rounded-xl p-6 flex flex-col justify-between space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-[#1D3A1E]">
            <div className="flex items-center gap-2">
              {isAnalyst ? (
                <Cpu className="w-4 h-4 text-[#A0FF99]" />
              ) : (
                <UserCheck className="w-4 h-4 text-[#A0FF99]" />
              )}
              <h2 className="text-xs font-bold uppercase tracking-wider text-white font-mono">
                {isAnalyst ? 'Detailed Risk Analyst View' : 'Transaction Safety Summary'}
              </h2>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1D3A1E] text-[#8A998A]">
              System Confidence: {model_signals.confidence_score ? `${model_signals.confidence_score}%` : '95.0%'}
            </span>
          </div>

          {!isAnalyst ? (
            /* Everyday User Persona View */
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-white">
                  {everyday_user.headline || 'Transaction Check Complete'}
                </h3>
                {/* Clear Next Step Advice */}
                <p className="text-xs text-[#A0FF99] mt-2 font-medium bg-[#0A120B] p-3 rounded-lg border border-[#1D3A1E]">
                  <strong>Suggested Next Step:</strong> {everyday_user.action_advice || actionInfo.suggestion}
                </p>
              </div>

              {/* Simple reasons bullets */}
              <div className="space-y-2 pt-1">
                <span className="text-xs font-semibold text-[#8A998A] uppercase tracking-wider block font-mono">
                  Key reasons behind this result:
                </span>
                <ul className="space-y-2">
                  {everyday_user.simple_reasons?.map((reason, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2.5 text-xs text-white bg-[#060B06] p-3 rounded-lg border border-[#1D3A1E]"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99] mt-1.5 shrink-0" />
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            /* Risk Analyst Persona View: 4-Tier Diagnostics Grid */
            <div className="space-y-4">
              <div>
                <span className="text-xs font-semibold text-[#8A998A] uppercase tracking-wider block font-mono mb-2.5">
                  Detailed Safety Breakdown:
                </span>
                <div className="grid grid-cols-2 gap-3">
                  {/* Layer 1: Rules */}
                  <div className="p-3.5 rounded-lg bg-[#060B06] border border-[#1D3A1E]">
                    <span className="text-[10px] text-[#8A998A] font-mono block">1. Instant Safety Rules Score</span>
                    <span className="text-base font-bold font-mono text-white">
                      {model_signals.rule_penalty_score?.toFixed(1) || '0.0'}
                      <span className="text-xs text-[#8A998A] font-normal"> / 100</span>
                    </span>
                  </div>

                  {/* Layer 2: XGBoost */}
                  <div className="p-3.5 rounded-lg bg-[#060B06] border border-[#1D3A1E]">
                    <span className="text-[10px] text-[#8A998A] font-mono block">2. AI Pattern Matcher (Likelihood)</span>
                    <span className="text-base font-bold font-mono text-white">
                      {((model_signals.xgb_fraud_probability || 0) * 100).toFixed(2)}%
                    </span>
                  </div>

                  {/* Layer 3: Isolation Forest */}
                  <div className="p-3.5 rounded-lg bg-[#060B06] border border-[#1D3A1E]">
                    <span className="text-[10px] text-[#8A998A] font-mono block">3. Unusual Activity Finder Score</span>
                    <span className="text-base font-bold font-mono text-white">
                      {model_signals.iforest_anomaly_score?.toFixed(1) || '0.0'}
                      <span className="text-xs text-[#8A998A] font-normal"> / 100</span>
                    </span>
                  </div>

                  {/* Layer 4: Behavioral Z-Score */}
                  <div className="p-3.5 rounded-lg bg-[#060B06] border border-[#1D3A1E]">
                    <span className="text-[10px] text-[#8A998A] font-mono block">4. Difference from Normal Habits</span>
                    <span className="text-base font-bold font-mono text-white">
                      {model_signals.behavioral_z_score !== undefined
                        ? `${model_signals.behavioral_z_score > 0 ? '+' : ''}${model_signals.behavioral_z_score.toFixed(2)} σ`
                        : '0.00 σ'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Technical Summary */}
              {technical_summary && (
                <div className="p-3 rounded-lg bg-[#060B06] border border-[#1D3A1E] text-xs text-[#8A998A] leading-relaxed font-mono">
                  {technical_summary}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Instant Safety Rules Section */}
      <div className="fintech-card rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1D3A1E]">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              Instant Safety Rule Alerts ({rules_triggered.length})
            </h3>
          </div>
          <span className="text-[10px] font-mono text-[#8A998A]">Automatic Protection Rules</span>
        </div>

        {rules_triggered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {rules_triggered.map((rule, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs flex items-start gap-3 font-mono"
              >
                <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <span>{rule}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-[#A0FF99] font-mono py-1">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-[#A0FF99]" />
            <span>All instant safety rules passed. No security rules were triggered.</span>
          </div>
        )}
      </div>

      {/* TreeSHAP Feature Contribution Waterfall Section */}
      <div className="fintech-card rounded-xl p-6 sm:p-7 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-[#1D3A1E]">
          <div className="flex items-center gap-2.5">
            <BarChart2 className="w-4 h-4 text-[#A0FF99]" />
            <h3 className="text-sm font-bold text-white">
              Reasons Behind the Risk
            </h3>
          </div>
          <span className="text-[10px] font-mono text-[#8A998A]">
            Clear Explanation
          </span>
        </div>

        <p className="text-xs text-[#8A998A]">
          Here is how each detail of your payment affected the final risk level. Factors highlighted in red increase the risk, while factors in green make the payment safer.
        </p>

        <ShapWaterfallChart contributions={top_shap_contributions} />
      </div>

      {/* Technical Details Accordion */}
      {isAnalyst && feature_vector_snapshot && (
        <div className="fintech-card rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => setShowJsonSnapshot(!showJsonSnapshot)}
            className="w-full px-6 py-4 flex items-center justify-between bg-[#0A120B] hover:bg-[#122314] transition-colors text-left"
          >
            <div className="flex items-center gap-2.5">
              <Cpu className="w-4 h-4 text-[#A0FF99]" />
              <span className="text-xs font-bold uppercase tracking-wider text-white font-mono">
                Technical Data Details (For Technical Reviewers)
              </span>
            </div>
            {showJsonSnapshot ? (
              <ChevronUp className="w-4 h-4 text-[#8A998A]" />
            ) : (
              <ChevronDown className="w-4 h-4 text-[#8A998A]" />
            )}
          </button>

          {showJsonSnapshot && (
            <div className="p-4 border-t border-[#1D3A1E] bg-[#020202] text-white overflow-x-auto text-xs font-mono">
              <pre>{JSON.stringify(feature_vector_snapshot, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TransactionOutputPage;