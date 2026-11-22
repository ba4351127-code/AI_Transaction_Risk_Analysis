import React, { useState } from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { PersonaProvider, usePersona } from './context/PersonaContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import SplashScreen from './components/common/SplashScreen';
import AuthModal from './components/pages/AuthModal';
import AuthPage from './components/pages/AuthPage';
import Sidebar from './components/layout/Sidebar';
import OverviewPage from './components/pages/OverviewPage';
import TransactionInputPage from './components/pages/TransactionInputPage';
import TransactionOutputPage from './components/pages/TransactionOutputPage';
import RiskIntelligencePage from './components/pages/RiskIntelligencePage';
import TransactionHistoryPage from './components/pages/TransactionHistoryPage';
import AlertsCenterPage from './components/pages/AlertsCenterPage';
import ReportsPage from './components/pages/ReportsPage';
import AboutPage from './components/pages/AboutPage';

const MainLayout = () => {
  // Splash Screen State (auto transitions after 2.5s)
  const [showSplash, setShowSplash] = useState(true);

  // Active View State
  const [currentView, setCurrentView] = useState('overview');
  
  // Real backend risk assessment result (Zero mock policy)
  const [currentAssessment, setCurrentAssessment] = useState(null);

  const { persona, isAnalyst } = usePersona();
  const { isDark } = useTheme();
  const { user, isAuthenticated, logout, openAuthModal } = useAuth();

  const handleStartAnalysis = () => {
    setCurrentAssessment(null);
    setCurrentView('input');
  };

  const handleAnalysisComplete = (assessmentData) => {
    setCurrentAssessment(assessmentData);
    setCurrentView('results');
  };

  const handleNewAnalysis = () => {
    setCurrentAssessment(null);
    setCurrentView('input');
  };

  // Simplified navigation title mapping matching user specifications
  const getViewTitle = () => {
    switch (currentView) {
      case 'overview': return 'Dashboard';
      case 'input': return 'Check a Transaction';
      case 'results': return 'Why Was This Transaction Flagged?';
      case 'intelligence': return 'Risk Insights';
      case 'history': return 'Past Transactions';
      case 'alerts': return 'Important Alerts';
      case 'reports': return 'Reports';
      case 'about': return 'About TransactionGuard';
      default: return 'TransactionGuard';
    }
  };

  // 1. Opening Splash Screen appears first
  if (showSplash) {
    return <SplashScreen onComplete={() => setShowSplash(false)} />;
  }

  // 2. Gateway Login / Signup Page (Protected Platform Requirement)
  if (!isAuthenticated) {
    return <AuthPage />;
  }

  return (
    <>
      {/* Protected Dashboard Platform Shell */}
      <div className="min-h-screen flex bg-[#020202] text-white font-sans selection:bg-[#A0FF99] selection:text-[#020202] transition-colors duration-200">
        {/* Persistent Sidebar */}
        <Sidebar
          currentView={currentView}
          setCurrentView={setCurrentView}
          hasResults={Boolean(currentAssessment)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto h-screen relative">
          {/* Top Status Header */}
          <header className="h-20 shrink-0 border-b border-[#1D3A1E] bg-[#060B06]/90 backdrop-blur-md px-6 sm:px-8 flex items-center justify-between sticky top-0 z-20">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-[#8A998A]">
                Section
              </span>
              <span className="text-xs font-mono font-bold px-3 py-1 rounded-md bg-[#1D3A1E] text-[#A0FF99] border border-[#1D3A1E]">
                {getViewTitle()}
              </span>
            </div>

            {/* Active Persona Pill Indicator & User Auth Badge */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1 rounded-md text-xs font-mono bg-[#1D3A1E] text-white border border-[#1D3A1E]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99]" />
                <span>Mode: <strong className="text-[#A0FF99]">{isAnalyst ? 'Analyst' : 'Standard'}</strong></span>
              </div>

              {isAuthenticated ? (
                <div className="flex items-center gap-2 px-3 py-1 rounded-md text-xs font-mono bg-[#0A120B] text-white border border-[#1D3A1E]">
                  <span className="w-2 h-2 rounded-full bg-[#A0FF99]" />
                  <span className="truncate max-w-[140px] text-[#A0FF99] font-medium" title={user.email}>
                    {user.full_name || user.email}
                  </span>
                  <button
                    type="button"
                    onClick={logout}
                    className="ml-1 text-[10px] text-[#8A998A] hover:text-[#EF4444] transition-colors uppercase tracking-wider"
                    title="Sign Out"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => openAuthModal('login')}
                  className="px-3.5 py-1 rounded-md text-xs font-mono font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors shadow-sm"
                >
                  Sign In
                </button>
              )}
            </div>
          </header>

          {/* View Content Container */}
          <main className="flex-1 p-6 sm:p-8 lg:p-10 max-w-6xl w-full mx-auto relative z-10">
            {currentView === 'overview' && (
              <OverviewPage
                onStartAnalysis={handleStartAnalysis}
                onNavigate={setCurrentView}
              />
            )}

            {currentView === 'input' && (
              <TransactionInputPage onAnalysisComplete={handleAnalysisComplete} />
            )}

            {currentView === 'results' && (
              <TransactionOutputPage
                assessment={currentAssessment}
                onNewAnalysis={handleNewAnalysis}
              />
            )}

            {currentView === 'intelligence' && (
              <RiskIntelligencePage />
            )}

            {currentView === 'history' && (
              <TransactionHistoryPage />
            )}

            {currentView === 'alerts' && (
              <AlertsCenterPage />
            )}

            {currentView === 'reports' && (
              <ReportsPage />
            )}

            {currentView === 'about' && (
              <AboutPage />
            )}
          </main>

          {/* Minimalist Editorial Footer */}
          <footer className="shrink-0 border-t border-[#1D3A1E] bg-[#060B06] py-4 px-6 sm:px-8 text-xs text-[#8A998A] font-mono flex flex-col sm:flex-row items-center justify-between gap-2">
            <div>TransactionGuard AI • Simple & Intelligent Payment Safety</div>
            <div className="flex items-center gap-3 text-white">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99]" />
                FastAPI Connected
              </span>
              <span>•</span>
              <span>SQLite Ledger</span>
              <span>•</span>
              <span>Clear Explanations</span>
            </div>
          </footer>
        </div>
      </div>
    </>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <PersonaProvider>
          <MainLayout />
        </PersonaProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}