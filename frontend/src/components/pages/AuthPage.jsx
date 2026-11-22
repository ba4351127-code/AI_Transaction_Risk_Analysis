import React, { useState, useEffect } from 'react';
import { ShieldCheck, Lock, Mail, User, AlertCircle, ArrowRight, CheckCircle2, Shield } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import transactionService from '../../services/transactionService';

export const AuthPage = () => {
  const { login, signup, authModalTab, setAuthModalTab } = useAuth();

  const [activeTab, setActiveTab] = useState(authModalTab || 'login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      try {
        const res = await transactionService.getHealth();
        if (isMounted) {
          setBackendStatus(res?.status === 'healthy' ? 'online' : 'offline');
        }
      } catch (e) {
        if (isMounted) setBackendStatus('offline');
      }
    };
    check();
    return () => {
      isMounted = false;
    };
  }, []);

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setFullName('');
    setConfirmPassword('');
    setError(null);
  };

  const handleTabSwitch = (tab) => {
    resetForm();
    setActiveTab(tab);
    if (setAuthModalTab) setAuthModalTab(tab);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!email || !email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    if (activeTab === 'signup') {
      if (password.length < 8) {
        setError('Password must be at least 8 characters long.');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match. Please re-enter.');
        return;
      }
    }

    setIsSubmitting(true);
    try {
      if (activeTab === 'login') {
        await login(email, password);
      } else {
        await signup(fullName, email, password);
      }
      resetForm();
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify your details.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#020202] text-white font-sans selection:bg-[#A0FF99] selection:text-[#020202] px-4 py-8">
      {/* Top Brand Bar */}
      <header className="max-w-5xl w-full mx-auto flex items-center justify-between pb-6 border-b border-[#1D3A1E]">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-[#1D3A1E] border border-[#A0FF99]/30">
            <Shield className="w-5 h-5 text-[#A0FF99]" />
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[#A0FF99]" />
          </div>
          <div>
            <div className="text-base font-bold tracking-tight text-white">
              Transaction<span className="text-[#A0FF99]">Guard</span> AI
            </div>
            <div className="text-[10px] font-mono text-[#8A998A] uppercase tracking-wider">
              Protected Intelligence Ledger
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-[#0A120B] border border-[#1D3A1E]">
          <span
            className={`w-2 h-2 rounded-full ${
              backendStatus === 'online' ? 'bg-[#A0FF99] animate-pulse' : 'bg-amber-400'
            }`}
          />
          <span className="text-[#8A998A] text-[11px]">
            {backendStatus === 'online' ? 'Engine Online' : 'Connecting to Server...'}
          </span>
        </div>
      </header>

      {/* Main Centered Gateway Card */}
      <main className="my-auto py-8 flex items-center justify-center">
        <div className="w-full max-w-md bg-[#060B06] border border-[#1D3A1E] rounded-2xl shadow-2xl overflow-hidden relative">
          {/* Card Header */}
          <div className="px-6 pt-6 pb-5 border-b border-[#1D3A1E] bg-[#0A120B]">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 rounded-xl bg-[#1D3A1E] border border-[#A0FF99]/40 flex items-center justify-center text-[#A0FF99]">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-base font-bold tracking-tight text-white">
                  {activeTab === 'login' ? 'Account Sign In' : 'Register Account'}
                </h1>
                <p className="text-xs font-mono text-[#8A998A]">
                  {activeTab === 'login'
                    ? 'Enter credentials to access transaction dashboard'
                    : 'Create your secure risk analysis workspace'}
                </p>
              </div>
            </div>

            {/* Tab Switcher */}
            <div className="grid grid-cols-2 p-1 mt-4 rounded-lg bg-[#020202] border border-[#1D3A1E]">
              <button
                type="button"
                onClick={() => handleTabSwitch('login')}
                className={`py-2 text-xs font-semibold rounded-md transition-all ${
                  activeTab === 'login'
                    ? 'bg-[#1D3A1E] text-[#A0FF99] shadow-sm font-bold'
                    : 'text-[#8A998A] hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => handleTabSwitch('signup')}
                className={`py-2 text-xs font-semibold rounded-md transition-all ${
                  activeTab === 'signup'
                    ? 'bg-[#1D3A1E] text-[#A0FF99] shadow-sm font-bold'
                    : 'text-[#8A998A] hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mx-6 mt-4 p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 flex items-start gap-2.5 text-xs text-[#FCA5A5]">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-[#EF4444]" />
              <span>{error}</span>
            </div>
          )}

          {/* Form Body */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {activeTab === 'signup' && (
              <div>
                <label className="block text-xs font-mono text-[#8A998A] mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-[#8A998A] absolute left-3 top-3" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Alex Morgan"
                    className="w-full bg-[#020202] border border-[#1D3A1E] focus:border-[#A0FF99] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-[#8A998A]/50 outline-none transition-colors"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-mono text-[#8A998A] mb-1.5">
                Email Address <span className="text-[#A0FF99]">*</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#8A998A] absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-[#020202] border border-[#1D3A1E] focus:border-[#A0FF99] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-[#8A998A]/50 outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-[#8A998A] mb-1.5">
                Password <span className="text-[#A0FF99]">*</span>
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#8A998A] absolute left-3 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-[#020202] border border-[#1D3A1E] focus:border-[#A0FF99] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-[#8A998A]/50 outline-none transition-colors"
                />
              </div>
              {activeTab === 'signup' && (
                <p className="text-[10px] text-[#8A998A] mt-1 font-mono">
                  Minimum 8 characters (maximum 72 bytes).
                </p>
              )}
            </div>

            {activeTab === 'signup' && (
              <div>
                <label className="block text-xs font-mono text-[#8A998A] mb-1.5">
                  Confirm Password <span className="text-[#A0FF99]">*</span>
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#8A998A] absolute left-3 top-3" />
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-[#020202] border border-[#1D3A1E] focus:border-[#A0FF99] rounded-lg pl-9 pr-3 py-2.5 text-xs text-white placeholder-[#8A998A]/50 outline-none transition-colors"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 py-3 px-4 rounded-lg bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] text-xs font-bold font-sans flex items-center justify-center gap-2 transition-colors disabled:opacity-50 shadow-md"
            >
              {isSubmitting ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>
                    {activeTab === 'login' ? 'Sign In to Dashboard' : 'Create Protected Account'}
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Zero-Credential Policy Notice */}
          <div className="px-6 py-4 bg-[#0A120B] border-t border-[#1D3A1E] text-[11px] text-[#8A998A] flex items-start gap-2.5 leading-relaxed">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-[#A0FF99] mt-0.5" />
            <div>
              <strong className="text-white block font-medium">Zero-Credential Security Policy</strong>
              Protected by bcrypt & JWT authentication. We never collect or store bank passwords, UPI PINs, OTPs, or credit card credentials.
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-5xl w-full mx-auto pt-6 border-t border-[#1D3A1E] flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-[#8A998A] font-mono">
        <div>TransactionGuard AI • Simple & Intelligent Payment Safety</div>
        <div>FastAPI Connected • SQLite Ledger • Strictly Isolated</div>
      </footer>
    </div>
  );
};

export default AuthPage;
