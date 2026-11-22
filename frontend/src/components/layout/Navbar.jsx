import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, UserCheck, Activity, Cpu } from 'lucide-react';
import { usePersona } from '../../context/PersonaContext';
import transactionService from '../../services/transactionService';

export const Navbar = ({ activeTab, setActiveTab }) => {
  const { persona, togglePersona, isAnalyst } = usePersona();
  const [backendStatus, setBackendStatus] = useState('checking'); // 'healthy' | 'offline' | 'checking'

  useEffect(() => {
    let isMounted = true;
    const checkStatus = async () => {
      try {
        const res = await transactionService.getHealth();
        if (isMounted) {
          if (res && res.status === 'healthy') {
            setBackendStatus('healthy');
          } else {
            setBackendStatus('offline');
          }
        }
      } catch (err) {
        if (isMounted) {
          setBackendStatus('offline');
        }
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-navy-800 bg-navy-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-navy-900 border border-brand-400/30 shadow-lg shadow-brand-500/20">
              <Shield className="w-5 h-5 text-white" />
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-navy-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-white">
                  Transaction<span className="text-brand-400">Guard</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
                  AI v2.0
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Multi-Layer Financial Risk & Anomaly Intelligence
              </p>
            </div>
          </div>

          {/* Navigation Tabs (Quick links if needed) */}
          {activeTab && setActiveTab && (
            <nav className="hidden md:flex items-center space-x-1">
              {[
                { id: 'analyze', label: 'Risk Analysis' },
                { id: 'simulator', label: 'What-If Simulator' },
                { id: 'audit', label: 'Audit History' },
                { id: 'alerts', label: 'Security Alerts' },
                { id: 'bulk', label: 'Batch Processing' },
                { id: 'intelligence', label: 'Model Metrics' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-navy-900'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          )}

          {/* Right Action Controls: Backend Status & Persona Switcher */}
          <div className="flex items-center gap-3">
            {/* Backend Connectivity Indicator */}
            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono bg-navy-900/80 border border-navy-800"
              title={
                backendStatus === 'healthy'
                  ? 'FastAPI & ML Engine Online'
                  : backendStatus === 'checking'
                  ? 'Connecting to backend...'
                  : 'Backend server offline (run uvicorn backend.app.main:app)'
              }
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'healthy'
                    ? 'bg-emerald-400 animate-pulse'
                    : backendStatus === 'checking'
                    ? 'bg-amber-400 animate-bounce'
                    : 'bg-rose-500'
                }`}
              />
              <span className="text-[11px] text-slate-300">
                {backendStatus === 'healthy'
                  ? 'FastAPI Live'
                  : backendStatus === 'checking'
                  ? 'Connecting'
                  : 'Offline'}
              </span>
            </div>

            {/* Persona Switcher Toggle */}
            <div className="flex items-center bg-navy-900 p-1 rounded-xl border border-navy-800">
              <button
                type="button"
                onClick={togglePersona}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  !isAnalyst
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Everyday User Persona: Plain-English explanations & intuitive guidance"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Everyday User</span>
              </button>

              <button
                type="button"
                onClick={togglePersona}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
                  isAnalyst
                    ? 'bg-purple-600 text-white shadow-md shadow-purple-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Risk Analyst Persona: TreeSHAP vectors, Isolation Forest metrics, rules triggered & raw feature vectors"
              >
                <Cpu className="w-3.5 h-3.5" />
                <span>Risk Analyst</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
