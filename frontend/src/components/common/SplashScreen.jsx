import React, { useState, useEffect } from 'react';

export const SplashScreen = ({ onComplete }) => {
  const [isFadingOut, setIsFadingOut] = useState(false);

  useEffect(() => {
    // Start smooth fade-out at 2.0 seconds, complete at 2.5 seconds
    const timer = setTimeout(() => {
      setIsFadingOut(true);
    }, 2000);

    const completeTimer = setTimeout(() => {
      onComplete();
    }, 2500);

    return () => {
      clearTimeout(timer);
      clearTimeout(completeTimer);
    };
  }, [onComplete]);

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#020202] text-white transition-opacity duration-500 ease-in-out select-none ${
        isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      <div className="flex flex-col items-center text-center space-y-6 max-w-md px-6">
        {/* Minimalist Professional Logo */}
        <div className="relative w-16 h-16 flex items-center justify-center">
          <svg viewBox="0 0 48 48" className="w-full h-full" fill="none">
            {/* Geometric diamond / polygon mark */}
            <rect x="8" y="8" width="32" height="32" rx="4" transform="rotate(45 24 24)" stroke="#1D3A1E" strokeWidth="2.5" />
            <rect x="13" y="13" width="22" height="22" rx="2" transform="rotate(45 24 24)" fill="#1D3A1E" stroke="#A0FF99" strokeWidth="1.5" />
            <circle cx="24" cy="24" r="3.5" fill="#A0FF99" />
          </svg>
        </div>

        {/* Brand Name & Editorial Tagline */}
        <div className="space-y-1.5">
          <h1 className="text-2xl font-bold tracking-tight text-white font-sans">
            Transaction<span className="text-[#A0FF99]">Guard</span> AI
          </h1>
          <p className="text-xs tracking-wider text-[#8A998A] uppercase font-mono">
            Intelligent Transaction Risk Analysis
          </p>
        </div>

        {/* Subtle Minimalist Line Progress */}
        <div className="w-36 h-[2px] bg-[#1D3A1E] rounded-full overflow-hidden mt-4">
          <div className="h-full bg-[#A0FF99] rounded-full animate-[pulse_1.8s_ease-in-out_infinite]" style={{ width: '70%' }} />
        </div>
      </div>
    </div>
  );
};

export default SplashScreen;
