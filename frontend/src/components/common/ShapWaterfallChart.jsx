import React from 'react';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';

/**
 * Plain-English Reasons Behind the Risk (TreeSHAP Explainer).
 * Translates machine learning feature contributions into natural language explanations.
 */
export const ShapWaterfallChart = ({ contributions = [] }) => {
  if (!contributions || contributions.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-[#8A998A] bg-[#0A120B] rounded-xl border border-[#1D3A1E]">
        No specific risk factors were flagged for this transaction.
      </div>
    );
  }

  // Calculate max absolute value for visual bar scaling
  const maxAbsValue = Math.max(
    ...contributions.map((c) => Math.abs(Number(c.shap_value) || 0.01)),
    0.1
  );

  const getFriendlyFeatureInfo = (featureName, rawDisplayName, value, isRisk) => {
    const lower = `${featureName || ''} ${rawDisplayName || ''}`.toLowerCase();
    
    if (lower.includes('amount') && (lower.includes('avg') || lower.includes('user') || lower.includes('ratio'))) {
      return {
        title: 'Amount Compared to Usual',
        explanation: isRisk 
          ? 'This amount is noticeably higher than your normal spending habits.'
          : 'This transaction amount is consistent with your everyday spending.'
      };
    }
    if (lower.includes('device') || lower.includes('familiar')) {
      const isKnown = String(value) === 'true' || String(value) === '1' || String(value).toLowerCase() === 'familiar';
      return {
        title: 'Is This a Known Device?',
        explanation: isKnown
          ? 'Payment was made from a trusted phone or computer used safely before.'
          : 'Payment was initiated from a new device that has not been seen on this account before.'
      };
    }
    if (lower.includes('amount')) {
      return {
        title: 'Transaction Amount',
        explanation: isRisk 
          ? 'The payment size is large compared to normal activity.'
          : 'The payment size is within normal, safe limits.'
      };
    }
    if (lower.includes('payment') || lower.includes('method') || lower.includes('card')) {
      return {
        title: 'Payment Method',
        explanation: isRisk 
          ? 'The payment rail or card type has higher scrutiny for this type of purchase.'
          : 'Standard trusted payment rail used.'
      };
    }
    if (lower.includes('velocity') || lower.includes('speed') || lower.includes('distance')) {
      return {
        title: 'Travel Speed Between Payments',
        explanation: isRisk 
          ? 'The time and distance between this payment and the last one look physically impossible.'
          : 'Location aligns naturally with your recent payment history.'
      };
    }
    if (lower.includes('hour') || lower.includes('time')) {
      return {
        title: 'Time of Day',
        explanation: isRisk 
          ? 'Payment was made at an unusual hour, such as the middle of the night.'
          : 'Payment occurred during normal daytime shopping hours.'
      };
    }
    return {
      title: rawDisplayName || featureName || 'Payment Detail',
      explanation: isRisk 
        ? 'This payment factor contributed to raising the risk level.'
        : 'This payment factor helped verify the transaction as safe.'
    };
  };

  const getImpactBadge = (magnitude, direction) => {
    const isIncrease = direction === 'increases_risk';
    
    // Simplify magnitude labels per user prompt
    let cleanMagnitude = 'Medium Risk';
    const magLower = (magnitude || '').toLowerCase();
    if (magLower.includes('crit')) cleanMagnitude = 'Very High Risk';
    else if (magLower.includes('high')) cleanMagnitude = 'High Risk';
    else if (magLower.includes('mod')) cleanMagnitude = 'Medium Risk';
    else if (magLower.includes('low')) cleanMagnitude = 'Low Risk';

    const baseClass = isIncrease
      ? 'bg-rose-500/15 text-rose-400 border-rose-500/30'
      : 'bg-[#1D3A1E] text-[#A0FF99] border-[#A0FF99]/30';

    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border ${baseClass}`}>
        {isIncrease ? cleanMagnitude : 'Makes Safer'}
      </span>
    );
  };

  return (
    <div className="space-y-4 select-none">
      {/* Legend & Clear Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-[#8A998A] pb-2 border-b border-[#1D3A1E]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-rose-500" />
            <span className="text-white font-medium">Increases Risk</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-[#A0FF99]" />
            <span className="text-white font-medium">Makes the Transaction Safer</span>
          </div>
        </div>
        <div className="font-mono text-[11px] text-[#8A998A]">
          Reasons Behind the Risk
        </div>
      </div>

      {/* Feature Contributions List */}
      <div className="space-y-3">
        {contributions.map((item, idx) => {
          const val = Number(item.shap_value) || 0;
          const isIncrease = item.direction === 'increases_risk' || val > 0;
          const absVal = Math.abs(val);
          const barPercent = Math.min(Math.round((absVal / maxAbsValue) * 100), 100);

          const { title, explanation } = getFriendlyFeatureInfo(
            item.feature,
            item.display_name,
            item.value,
            isIncrease
          );

          // Format value nicely
          let displayVal = String(item.value);
          if (typeof item.value === 'boolean' || displayVal === 'true' || displayVal === 'false') {
            displayVal = displayVal === 'true' ? 'Yes (Known)' : 'No (New)';
          } else if (typeof item.value === 'number' && item.feature?.toLowerCase().includes('amount')) {
            displayVal = `$${item.value.toFixed(2)}`;
          }

          return (
            <div
              key={item.feature || idx}
              className="p-4 rounded-xl fintech-card space-y-2.5"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  {isIncrease ? (
                    <TrendingUp className="w-4 h-4 text-rose-400 shrink-0" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-[#A0FF99] shrink-0" />
                  )}
                  <div>
                    <span className="text-sm font-semibold text-white">
                      {title}
                    </span>
                    <span className="text-xs text-[#8A998A] font-mono ml-2">
                      (Your Transaction Value: <strong className="text-white">{displayVal}</strong>)
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 shrink-0">
                  {getImpactBadge(item.impact_magnitude, item.direction)}
                  <span
                    className={`font-mono text-xs font-bold ${
                      isIncrease ? 'text-rose-400' : 'text-[#A0FF99]'
                    }`}
                  >
                    {val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Simple explanation sentence below each factor */}
              <p className="text-xs text-[#8A998A] leading-relaxed">
                {explanation}
              </p>

              {/* Relative Impact Bar */}
              <div className="w-full bg-[#020202] h-1.5 rounded-full overflow-hidden flex border border-[#1D3A1E]">
                {isIncrease ? (
                  <div
                    className="h-full bg-rose-500 rounded-full transition-all duration-500"
                    style={{ width: `${barPercent}%` }}
                  />
                ) : (
                  <div
                    className="h-full bg-[#A0FF99] rounded-full transition-all duration-500"
                    style={{ width: `${barPercent}%` }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ShapWaterfallChart;
