import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Search, 
  HelpCircle, 
  Clock, 
  AlertCircle, 
  FileText, 
  Info, 
  Sun, 
  Moon, 
  ChevronLeft, 
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  BarChart2,
  User,
  LogIn,
  LogOut
} from 'lucide-react';
import { usePersona } from '../../context/PersonaContext';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import transactionService from '../../services/transactionService';

export const Sidebar = ({ currentView, setCurrentView, hasResults }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { persona, togglePersona, isAnalyst } = usePersona();
  const { theme, toggleTheme, isDark } = useTheme();
  const { user, isAuthenticated, logout, openAuthModal } = useAuth();
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
    const interval = setInterval(check, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Simplified navigation items per user specifications:
  const navItems = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'input', label: 'Check a Transaction', icon: Search },
    ...(hasResults ? [{ id: 'results', label: 'Risk Reasons', icon: HelpCircle }] : []),
    { id: 'intelligence', label: 'Risk Insights', icon: BarChart2 },
    { id: 'history', label: 'Past Transactions', icon: Clock },
    { id: 'alerts', label: 'Important Alerts', icon: AlertCircle },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'about', label: 'About TransactionGuard', icon: Info },
  ];

  return (
    <aside
      className={`h-screen sticky top-0 flex flex-col justify-between transition-all duration-300 select-none z-30 shrink-0 border-r ${
        isCollapsed ? 'w-20' : 'w-64'
      } bg-[#060B06] border-[#1D3A1E] text-white`}
    >
      {/* Top Branding & Navigation */}
      <div>
        {/* Brand Header */}
        <div className="h-20 flex items-center justify-between px-5 border-b border-[#1D3A1E]">
          <div className="flex items-center gap-3 overflow-hidden">
            {/* Clean Professional Logo */}
            <div className="w-9 h-9 rounded-lg bg-[#1D3A1E] border border-[#A0FF99]/40 flex items-center justify-center shrink-0">
              <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
                <rect x="4" y="4" width="16" height="16" rx="2" stroke="#A0FF99" strokeWidth="1.75" />
                <path d="M9 12L11 14L15 10" stroke="#FFFFFF" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>

            {!isCollapsed && (
              <div className="leading-tight">
                <span className="font-bold text-sm tracking-tight text-white block font-sans">
                  Transaction<span className="text-[#A0FF99]">Guard</span>
                </span>
                <span className="text-[10px] tracking-wider text-[#8A998A] font-mono uppercase block">
                  Payment Protection
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded-md text-[#8A998A] hover:text-white hover:bg-[#1D3A1E] transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setCurrentView(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center px-0' : 'justify-start px-3.5'
                } py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#1D3A1E] text-white font-semibold border-l-2 border-[#A0FF99]'
                    : 'text-[#8A998A] hover:text-white hover:bg-[#122314]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 shrink-0 transition-colors ${
                      isActive ? 'text-[#A0FF99]' : 'text-[#8A998A]'
                    }`}
                  />
                  {!isCollapsed && <span>{item.label}</span>}
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Controls: Account, User Mode & System Status */}
      <div className="p-3 border-t border-[#1D3A1E] space-y-3 bg-[#0A120B]">
        {/* User Account Card / Login Action */}
        {!isCollapsed ? (
          isAuthenticated ? (
            <div className="p-2.5 rounded-lg bg-[#060B06] border border-[#1D3A1E] flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-7 h-7 rounded-full bg-[#1D3A1E] border border-[#A0FF99]/40 flex items-center justify-center shrink-0 text-[#A0FF99]">
                  <User className="w-3.5 h-3.5" />
                </div>
                <div className="min-w-0 leading-tight">
                  <span className="text-xs font-semibold text-white block truncate">
                    {user?.full_name || user?.email}
                  </span>
                  <span className="text-[10px] font-mono text-[#8A998A] block truncate">
                    {user?.user_identifier}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={logout}
                className="p-1.5 rounded-md text-[#8A998A] hover:text-[#EF4444] hover:bg-[#122314] transition-colors"
                title="Sign out of account"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => openAuthModal('login')}
              className="w-full py-2 px-3 rounded-lg bg-[#1D3A1E] hover:bg-[#254B26] border border-[#1D3A1E] text-[#A0FF99] text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In / Register</span>
            </button>
          )
        ) : (
          <button
            type="button"
            onClick={() => (isAuthenticated ? logout() : openAuthModal('login'))}
            className="w-full flex items-center justify-center p-2 rounded-lg bg-[#060B06] border border-[#1D3A1E] text-[#8A998A] hover:text-[#A0FF99]"
            title={isAuthenticated ? `Logged in as ${user?.email}. Click to sign out.` : 'Sign In'}
          >
            {isAuthenticated ? <LogOut className="w-4 h-4 text-[#A0FF99]" /> : <LogIn className="w-4 h-4" />}
          </button>
        )}

        {/* Simple User Mode Toggle */}
        {!isCollapsed ? (
          <div className="p-2 rounded-lg bg-[#060B06] border border-[#1D3A1E] space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-mono text-[#8A998A] px-1">
              <span>View Mode</span>
              <span className="text-[#A0FF99] font-semibold">
                {isAnalyst ? 'Analyst' : 'Standard'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-1 bg-[#020202] p-1 rounded-md border border-[#1D3A1E]">
              <button
                type="button"
                onClick={() => isAnalyst && togglePersona()}
                className={`py-1 px-2 rounded text-[11px] font-medium transition-all ${
                  !isAnalyst
                    ? 'bg-[#1D3A1E] text-[#A0FF99] font-semibold'
                    : 'text-[#8A998A] hover:text-white'
                }`}
                title="Simple language and clear suggestions"
              >
                Standard
              </button>

              <button
                type="button"
                onClick={() => !isAnalyst && togglePersona()}
                className={`py-1 px-2 rounded text-[11px] font-medium transition-all ${
                  isAnalyst
                    ? 'bg-[#1D3A1E] text-[#A0FF99] font-semibold'
                    : 'text-[#8A998A] hover:text-white'
                }`}
                title="Detailed risk factors and sub-scores"
              >
                Analyst
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={togglePersona}
            className="w-full flex items-center justify-center p-2 rounded-lg bg-[#060B06] border border-[#1D3A1E] text-[#A0FF99]"
            title={`Active Mode: ${isAnalyst ? 'Analyst' : 'Standard'}. Click to switch.`}
          >
            <span className="font-mono text-xs font-bold">{isAnalyst ? 'A' : 'S'}</span>
          </button>
        )}

        {/* Footer Bar: System Status & Theme Toggle */}
        <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} px-1`}>
          {!isCollapsed && (
            <div
              className="flex items-center gap-2 text-xs font-mono text-[#8A998A]"
              title="System connection status"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'online' ? 'bg-[#A0FF99]' : 'bg-[#EF4444]'
                }`}
              />
              <span className="text-[11px]">
                {backendStatus === 'online' ? 'Protection Active' : 'Offline'}
              </span>
            </div>
          )}

          <button
            type="button"
            onClick={toggleTheme}
            className="p-1.5 rounded-md border border-[#1D3A1E] text-[#8A998A] hover:text-white hover:bg-[#122314] transition-colors"
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDark ? <Sun className="w-3.5 h-3.5 text-[#A0FF99]" /> : <Moon className="w-3.5 h-3.5 text-white" />}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
