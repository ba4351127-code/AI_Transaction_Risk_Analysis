import React from 'react';
import { 
  Shield, 
  Zap, 
  Cpu, 
  ArrowRight, 
  Layers, 
  Activity, 
  Lock, 
  CheckCircle2, 
  ShieldCheck, 
  Radar, 
  TrendingUp, 
  Sparkles,
  Sliders,
  ChevronRight
} from 'lucide-react';

export const LandingPage = ({ onStartAnalysis }) => {
  return (
    <div className="max-w-6xl mx-auto space-y-16 py-4 animate-fade-in select-none">
      
      {/* 1. Hero Section */}
      <section className="relative overflow-hidden rounded-3xl p-8 sm:p-12 lg:p-16 border border-cyber-border bg-gradient-to-br from-cyber-navy via-cyber-black to-cyber-card shadow-2xl">
        {/* Subtle Ambient Electric Glows */}
        <div className="ambient-glow-blue w-96 h-96 -top-20 -left-20" />
        <div className="ambient-glow-blue w-96 h-96 -bottom-20 -right-20 opacity-50" />
        <div className="absolute inset-0 cyber-grid pointer-events-none opacity-20" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Hero Left Column */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-electric/10 text-electric-light border border-electric/30 font-mono shadow-electric-sm">
              <span className="w-2 h-2 rounded-full bg-electric-glow animate-pulse" />
              <span>Enterprise Financial Security Platform</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1] font-sans">
              Intelligent Protection <br />
              <span className="bg-gradient-to-r from-electric via-electric-glow to-cyan-400 bg-clip-text text-transparent">
                for Every Transaction
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-sans max-w-xl">
              TransactionGuard AI safeguards modern digital banking and payment networks through real-time multi-layered intelligence, pairing supervised machine learning and unsupervised anomaly detection with transparent TreeSHAP explainability.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                type="button"
                onClick={onStartAnalysis}
                className="inline-flex items-center gap-2.5 px-7 py-4 rounded-xl font-bold text-sm bg-electric hover:bg-electric-glow text-white shadow-electric-md transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
              >
                <Zap className="w-4 h-4 fill-white" />
                <span>Start Risk Analysis</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-2 px-4 py-3.5 rounded-xl border border-cyber-border bg-cyber-card/60 backdrop-blur text-xs font-mono text-slate-300">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>FastAPI & SQLite Engine Active</span>
              </div>
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-cyber-border/70 text-slate-300">
              <div>
                <span className="text-xl sm:text-2xl font-bold font-mono text-white block">&lt; 15 ms</span>
                <span className="text-[11px] text-slate-400 font-mono uppercase">Inference Latency</span>
              </div>
              <div>
                <span className="text-xl sm:text-2xl font-bold font-mono text-white block">1.0 ROC-AUC</span>
                <span className="text-[11px] text-slate-400 font-mono uppercase">Validation Accuracy</span>
              </div>
              <div>
                <span className="text-xl sm:text-2xl font-bold font-mono text-white block">4 Layers</span>
                <span className="text-[11px] text-slate-400 font-mono uppercase">Risk Fusion Engine</span>
              </div>
            </div>
          </div>

          {/* Hero Right Column: Sophisticated Security / Shield Composition */}
          <div className="lg:col-span-5 flex items-center justify-center relative">
            <div className="relative w-72 h-72 sm:w-80 sm:h-80 flex items-center justify-center">
              {/* Outer Orbit Rings */}
              <div className="absolute inset-0 rounded-full border border-electric/20 border-dashed animate-spin-slow" />
              <div className="absolute inset-6 rounded-full border border-electric-glow/30 animate-spin-slow" style={{ animationDirection: 'reverse', animationDuration: '24s' }} />
              <div className="absolute inset-12 rounded-full border border-cyan-400/20" />

              {/* Luminous Core Glow */}
              <div className="absolute w-44 h-44 rounded-full bg-electric/25 blur-2xl animate-pulse-slow" />

              {/* 3D Shield Emblem */}
              <div className="relative z-10 flex flex-col items-center justify-center w-32 h-36 rounded-3xl bg-gradient-to-b from-electric via-electric-dark to-cyber-navy border-2 border-electric-glow shadow-electric-lg">
                <Shield className="w-14 h-14 text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.7)]" />
                <span className="text-[10px] font-mono font-bold text-cyan-300 mt-2 tracking-wider">SECURED</span>
              </div>

              {/* Floating Intelligence Telemetry Badges */}
              <div className="absolute -top-2 -left-4 px-3 py-1.5 rounded-lg bg-cyber-card/90 border border-cyber-border text-[11px] font-mono text-slate-300 shadow-lg backdrop-blur animate-pulse-slow flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Heuristic Rules: Active</span>
              </div>

              <div className="absolute -bottom-2 -right-4 px-3 py-1.5 rounded-lg bg-cyber-card/90 border border-cyber-border text-[11px] font-mono text-slate-300 shadow-lg backdrop-blur flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-electric-glow" />
                <span>TreeSHAP: 15ms Latency</span>
              </div>

              <div className="absolute top-1/2 -right-6 px-3 py-1.5 rounded-lg bg-cyber-card/90 border border-cyber-border text-[11px] font-mono text-slate-300 shadow-lg backdrop-blur flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                <span>Isolation Forest: Calibrated</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Four Analytical Layers: Sophisticated Layered Architecture Flow */}
      <section className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <span className="text-xs font-mono font-semibold text-electric-glow uppercase tracking-wider block">
              Multi-Layer Analytical Defense
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
              Synchronized 4-Layer Risk Fusion
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 max-w-md font-sans">
            Every transaction is scrutinized concurrently through deterministic rules, supervised machine learning, unsupervised anomaly detection, and personal behavioral baselines.
          </p>
        </div>

        {/* Connected Architecture Flow */}
        <div className="relative grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-3xl bg-cyber-navy/40 border border-cyber-border">
          {/* Layer 1 */}
          <div className="cyber-card rounded-2xl p-6 relative flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                  LAYER 01
                </span>
                <Lock className="w-4 h-4 text-amber-400" />
              </div>
              <h3 className="text-base font-bold text-white">Heuristic Rule Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Deterministic circuit breakers evaluating impossible travel speeds (&gt;900 km/h), radical amount spikes (&gt;15x user average), and unrecognized hardware hashes.
              </p>
            </div>
            <div className="pt-3 border-t border-cyber-border/60 text-[11px] font-mono text-amber-400/90 flex items-center justify-between">
              <span>Weight: 20%</span>
              <span className="text-[10px] text-slate-500">Instant Bypass</span>
            </div>
          </div>

          {/* Layer 2 */}
          <div className="cyber-card rounded-2xl p-6 relative flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-electric/15 text-electric-light border border-electric/30">
                  LAYER 02
                </span>
                <Cpu className="w-4 h-4 text-electric-glow" />
              </div>
              <h3 className="text-base font-bold text-white">XGBoost Fraud Model</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Supervised gradient-boosted decision trees trained with depth-4 regularization and class-weighted balancing to estimate card and digital payment fraud probability.
              </p>
            </div>
            <div className="pt-3 border-t border-cyber-border/60 text-[11px] font-mono text-electric-light flex items-center justify-between">
              <span>Weight: 45%</span>
              <span className="text-[10px] text-slate-500">Supervised Trees</span>
            </div>
          </div>

          {/* Layer 3 */}
          <div className="cyber-card rounded-2xl p-6 relative flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">
                  LAYER 03
                </span>
                <Activity className="w-4 h-4 text-purple-400" />
              </div>
              <h3 className="text-base font-bold text-white">Isolation Forest</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Unsupervised ensemble isolating multivariate anomalies and novel zero-day attack vectors across multi-dimensional feature space without requiring prior fraud labels.
              </p>
            </div>
            <div className="pt-3 border-t border-cyber-border/60 text-[11px] font-mono text-purple-300 flex items-center justify-between">
              <span>Weight: 20%</span>
              <span className="text-[10px] text-slate-500">Unsupervised</span>
            </div>
          </div>

          {/* Layer 4 */}
          <div className="cyber-card rounded-2xl p-6 relative flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  LAYER 04
                </span>
                <Layers className="w-4 h-4 text-emerald-400" />
              </div>
              <h3 className="text-base font-bold text-white">Behavioral Profiler</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Calculates statistical Z-scores against the user's rolling 30-day spending history, favorite merchant categories, habitual transaction hours, and geo-centers.
              </p>
            </div>
            <div className="pt-3 border-t border-cyber-border/60 text-[11px] font-mono text-emerald-400 flex items-center justify-between">
              <span>Weight: 15%</span>
              <span className="text-[10px] text-slate-500">Rolling Baseline</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. How TransactionGuard AI Works: 3-Step Pipeline */}
      <section className="space-y-8">
        <div>
          <span className="text-xs font-mono font-semibold text-electric-glow uppercase tracking-wider block">
            End-to-End Workflow
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
            How TransactionGuard AI Evaluates Risk
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="cyber-card rounded-2xl p-6 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-electric/20 border border-electric/30 flex items-center justify-center text-sm font-mono font-bold text-electric-light">
              01
            </div>
            <h4 className="text-base font-bold text-white">Telemetry Ingestion</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Captures financial volume, currency, payment rail, merchant category, resolved geographic coordinates, and client device fingerprint.
            </p>
          </div>

          <div className="cyber-card rounded-2xl p-6 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-electric/20 border border-electric/30 flex items-center justify-center text-sm font-mono font-bold text-electric-light">
              02
            </div>
            <h4 className="text-base font-bold text-white">Concurrent Scoring</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Simultaneously executes the 4 layers in memory under 15ms. Applies mathematical calibration and circuit breaker overrides to compute a unified 0-100 risk score.
            </p>
          </div>

          <div className="cyber-card rounded-2xl p-6 space-y-3">
            <div className="w-8 h-8 rounded-xl bg-electric/20 border border-electric/30 flex items-center justify-center text-sm font-mono font-bold text-electric-light">
              03
            </div>
            <h4 className="text-base font-bold text-white">TreeSHAP Explainability</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              TreeSHAP decomposes the exact Shapley contribution of every parameter. Formats outputs for everyday consumers or senior risk analysts with instant audit persistence.
            </p>
          </div>
        </div>
      </section>

      {/* 4. Bottom Launch CTA */}
      <section className="p-8 sm:p-10 rounded-3xl border border-cyber-border bg-gradient-to-r from-cyber-card via-cyber-navy to-cyber-black flex flex-col sm:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="space-y-1 max-w-xl text-center sm:text-left">
          <h3 className="text-xl font-bold text-white">
            Ready to Evaluate a Transaction?
          </h3>
          <p className="text-xs sm:text-sm text-slate-400">
            Submit payment parameters to test live risk classification, heuristic validation, and TreeSHAP waterfall decomposition.
          </p>
        </div>

        <button
          type="button"
          onClick={onStartAnalysis}
          className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl text-xs sm:text-sm font-bold bg-electric hover:bg-electric-glow text-white shadow-electric-md transition-all hover:scale-[1.02] shrink-0"
        >
          <Zap className="w-4 h-4 fill-white" />
          <span>Launch Analysis Form</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </section>
    </div>
  );
};

export default LandingPage;
