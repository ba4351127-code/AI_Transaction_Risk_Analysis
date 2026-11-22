import React from 'react';
import { Shield, CheckCircle2, Layers, Cpu, Activity, Lock, Server } from 'lucide-react';

export const AboutPage = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-10 py-4 select-none">
      {/* Header */}
      <div className="space-y-2 pb-4 border-b border-[#1D3A1E]">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-[#1D3A1E] text-[#A0FF99]">
          <span>How It Works</span>
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white font-sans">
          About TransactionGuard
        </h1>
        <p className="text-sm text-[#8A998A] leading-relaxed">
          Intelligent, multi-layered payment protection built to keep every transaction safe without slowing down customers.
        </p>
      </div>

      {/* Narrative Section */}
      <div className="p-7 rounded-xl fintech-card space-y-4 text-xs text-[#8A998A] leading-relaxed">
        <h2 className="text-base font-bold text-white font-sans">
          Our Approach to Keeping Your Payments Safe
        </h2>
        <p>
          In digital banking and modern online payments, real fraud is rare—occurring in less than 4% of all transactions. Traditional anti-fraud systems often fail by blocking legitimate customers, causing unnecessary frustration and lost trust.
        </p>
        <p>
          To solve this problem, <strong>TransactionGuard AI</strong> uses four synchronized safety checks working together in real time. Rather than relying on a single score or guessing, it verifies instant safety rules, detects complex fraud patterns, flags unusual anomalies, and checks personal spending habits.
        </p>
      </div>

      {/* 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-5 rounded-xl fintech-card space-y-2">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Lock className="w-4 h-4 text-[#A0FF99]" />
            <span>1. Instant Safety Rules (20%)</span>
          </div>
          <p className="text-xs text-[#8A998A]">
            Catches obvious red flags immediately—such as physically impossible travel speeds between transactions or extreme unexpected spending spikes.
          </p>
        </div>

        <div className="p-5 rounded-xl fintech-card space-y-2">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Cpu className="w-4 h-4 text-[#A0FF99]" />
            <span>2. AI Pattern Matcher (45%)</span>
          </div>
          <p className="text-xs text-[#8A998A]">
            Trained on thousands of real payment scenarios to detect subtle, complex signs of fraud that traditional rule lists miss.
          </p>
        </div>

        <div className="p-5 rounded-xl fintech-card space-y-2">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Activity className="w-4 h-4 text-[#A0FF99]" />
            <span>3. Unusual Activity Finder (20%)</span>
          </div>
          <p className="text-xs text-[#8A998A]">
            Identifies brand new or unusual transaction patterns and outliers that deviate from standard baseline activity.
          </p>
        </div>

        <div className="p-5 rounded-xl fintech-card space-y-2">
          <div className="flex items-center gap-2 text-white font-bold text-sm">
            <Layers className="w-4 h-4 text-[#A0FF99]" />
            <span>4. Your Normal Habits (15%)</span>
          </div>
          <p className="text-xs text-[#8A998A]">
            Compares each transaction to the customer's typical spending amounts and normal shopping hours, providing trusted approvals for familiar habits.
          </p>
        </div>
      </div>

      {/* System Technology Overview */}
      <div className="p-6 rounded-xl fintech-card space-y-4">
        <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
          System Technology Overview
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Fast Backend API</span>
            <span className="text-white font-semibold">FastAPI (Python)</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Data Verification</span>
            <span className="text-white font-semibold">Pydantic v2</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Secure Ledger</span>
            <span className="text-white font-semibold">SQLite Engine</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Pattern AI Engine</span>
            <span className="text-white font-semibold">XGBoost & Isolation Forest</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Clear Explanations</span>
            <span className="text-white font-semibold">TreeSHAP Explainability</span>
          </div>
          <div className="space-y-1">
            <span className="text-[#8A998A] block">Modern Dashboard</span>
            <span className="text-white font-semibold">React + Tailwind CSS</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;