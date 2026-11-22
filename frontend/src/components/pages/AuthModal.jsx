import React, { useState } from 'react';
import { X, Lock, Mail, User, ShieldCheck, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const AuthModal = () => {
  const {
    isAuthModalOpen,
    closeAuthModal,
    authModalTab,
    setAuthModalTab,
    login,
    signup
  } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isAuthModalOpen) return null;

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setFullName('');
    setConfirmPassword('');
    setError(null);
  };

  const handleTabSwitch = (tab) => {
    resetForm();
    setAuthModalTab(tab);
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

    if (authModalTab === 'signup') {
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
      if (authModalTab === 'login') {
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#020202]/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-md bg-[#060B06] border border-[#1D3A1E] rounded-2xl shadow-2xl overflow-hidden text-white font-sans relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header Bar */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#1D3A1E] bg-[#0A120B]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#1D3A1E] border border-[#A0FF99]/40 flex items-center justify-center text-[#A0FF99]">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold tracking-tight text-white">
                Transaction<span className="text-[#A0FF99]">Guard</span> Account
              </h2>
              <p className="text-[11px] font-mono text-[#8A998A]">Secure Payment Intelligence</p>
            </div>
          </div>

          <button
            type="button"
            onClick={closeAuthModal}
            className="p-1 rounded-md text-[#8A998A] hover:text-white hover:bg-[#1D3A1E] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="grid grid-cols-2 p-1.5 mx-6 mt-6 rounded-lg bg-[#020202] border border-[#1D3A1E]">
          <button
            type="button"
            onClick={() => handleTabSwitch('login')}
            className={`py-2 text-xs font-semibold rounded-md transition-all ${
              authModalTab === 'login'
                ? 'bg-[#1D3A1E] text-[#A0FF99] shadow-sm'
                : 'text-[#8A998A] hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => handleTabSwitch('signup')}
            className={`py-2 text-xs font-semibold rounded-md transition-all ${
              authModalTab === 'signup'
                ? 'bg-[#1D3A1E] text-[#A0FF99] shadow-sm'
                : 'text-[#8A998A] hover:text-white'
            }`}
          >
            Create Account
          </button>
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
          {authModalTab === 'signup' && (
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
                  placeholder="e.g. John Doe"
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
                placeholder="analyst@institution.com"
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
            {authModalTab === 'signup' && (
              <p className="text-[10px] text-[#8A998A] mt-1 font-mono">
                Must be at least 8 characters long.
              </p>
            )}
          </div>

          {authModalTab === 'signup' && (
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
            className="w-full mt-2 py-3 px-4 rounded-lg bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] text-xs font-bold font-sans flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? (
              <span>Authenticating...</span>
            ) : (
              <>
                <span>{authModalTab === 'login' ? 'Sign In to Account' : 'Create Protected Account'}</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Security Assurance Notice */}
        <div className="px-6 py-4 bg-[#0A120B] border-t border-[#1D3A1E] text-[11px] text-[#8A998A] flex items-start gap-2.5 leading-relaxed">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-[#A0FF99] mt-0.5" />
          <div>
            <strong className="text-white block font-medium">Zero-Credential Security Policy</strong>
            TransactionGuard AI uses institutional bcrypt & JWT encryption. We never collect or store bank account numbers, UPI PINs, OTPs, or credit card CVVs.
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
