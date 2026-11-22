import React from 'react';
import { X, Shield, Cpu, Activity, Layers, Lock, CheckCircle2 } from 'lucide-react';

export const AboutModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in select-none">
      <div className="relative w-full max-w-2xl cyber-card rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl border border-cyber-border">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-cyber-card border border-cyber-border text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-cyber-border">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-electric to-cyber-navy border border-electric-glow/40 shadow-electric-sm">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white font-sans">
              Transaction<span className="text-electric-glow">Guard</span> AI
            </h2>
            <p className="text-xs text-slate-400 font-mono">
              Industry-Grade Financial Risk & Anomaly Intelligence
            </p>
          </div>
        </div>

        {/* Overview Body */}
        <div className="space-y-4 text-xs text-slate-300 leading-relaxed">
          <p>
            <strong>TransactionGuard AI</strong> is a production-engineered financial intelligence platform developed for real-time transaction scoring, behavioral anomaly detection, and explainable AI audit trails.
          </p>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="p-3 rounded-xl bg-cyber-black/70 border border-cyber-border space-y-1">
              <span className="text-[10px] font-mono text-electric-light uppercase font-bold block">Engine Architecture</span>
              <span className="text-sm font-bold text-white block">4-Tier Risk Fusion</span>
              <p className="text-[11px] text-slate-400">Heuristics + XGBoost + Isolation Forest + Behavioral Z-Score.</p>
            </div>

            <div className="p-3 rounded-xl bg-cyber-black/70 border border-cyber-border space-y-1">
              <span className="text-[10px] font-mono text-electric-light uppercase font-bold block">Explainability</span>
              <span className="text-sm font-bold text-white block">TreeSHAP XAI</span>
              <p className="text-[11px] text-slate-400">Exact Shapley feature vectors translated for consumers & analysts.</p>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block font-semibold">
              Core Technical Capabilities:
            </span>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Sub-15ms in-memory ML inference</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Haversine velocity travel checks</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Rolling 30-day personal baseline profiling</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span>Immutable relational audit trail</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-cyber-border text-[11px] font-mono text-slate-500">
          <span>FastAPI • React 18 • TreeSHAP • SQLite</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-electric hover:bg-electric-glow text-white font-bold transition-all"
          >
            Close Overview
          </button>
        </div>
      </div>
    </div>
  );
};

export default AboutModal;
