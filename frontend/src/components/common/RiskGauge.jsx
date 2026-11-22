import React from 'react';

/**
 * Calibrated Semi-Circular Risk Gauge Component (0 to 100).
 * Displays risk zones: LOW (0-30), MEDIUM (31-70), HIGH (71-89), CRITICAL (90-100).
 */
export const RiskGauge = ({ score = 0, category = 'LOW', size = 260 }) => {
  const normalizedScore = Math.min(Math.max(Number(score) || 0, 0), 100);

  const getColor = (s) => {
    if (s <= 30) return { stroke: '#A0FF99', label: 'LOW RISK', textClass: 'text-[#A0FF99]' };
    if (s <= 70) return { stroke: '#F59E0B', label: 'MEDIUM RISK', textClass: 'text-amber-400' };
    if (s <= 89) return { stroke: '#EF4444', label: 'HIGH RISK', textClass: 'text-rose-400' };
    return { stroke: '#991B1B', label: 'CRITICAL RISK', textClass: 'text-rose-500' };
  };

  const currentTheme = getColor(normalizedScore);

  const radius = 90;
  const strokeWidth = 14;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;
  const needleAngle = -90 + (normalizedScore / 100) * 180;

  return (
    <div className="flex flex-col items-center justify-center select-none">
      <div className="relative" style={{ width: size, height: size * 0.62 }}>
        <svg
          viewBox="0 0 220 130"
          className="w-full h-full overflow-visible"
        >
          {/* Background Track Arc */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none"
            stroke="#1D3A1E"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Calibrated Active Score Arc */}
          <path
            d="M 20 110 A 90 90 0 0 1 200 110"
            fill="none"
            stroke={currentTheme.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />

          {/* Threshold Tick Marks */}
          <line
            x1="55" y1="52" x2="60" y2="59"
            stroke="#8A998A"
            strokeWidth="1.5"
            strokeDasharray="2"
          />
          <line
            x1="160" y1="52" x2="155" y2="59"
            stroke="#8A998A"
            strokeWidth="1.5"
            strokeDasharray="2"
          />

          {/* Center Hub Indicator */}
          <circle cx="110" cy="110" r="7" fill="#1D3A1E" stroke="#020202" strokeWidth="2" />
          <circle cx="110" cy="110" r="3.5" fill={currentTheme.stroke} />

          {/* Needle Indicator */}
          <g transform={`rotate(${needleAngle} 110 110)`} className="transition-transform duration-1000 ease-out">
            <line
              x1="110"
              y1="110"
              x2="110"
              y2="28"
              stroke={currentTheme.stroke}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="110" cy="28" r="2.5" fill={currentTheme.stroke} />
          </g>

          {/* Scale range numbers */}
          <text x="18" y="125" className="text-[10px] fill-[#8A998A] font-mono font-medium">0</text>
          <text x="56" y="44" className="text-[9px] fill-[#A0FF99] font-mono font-medium">30</text>
          <text x="156" y="44" className="text-[9px] fill-amber-400 font-mono font-medium">70</text>
          <text x="195" y="125" className="text-[10px] fill-rose-400 font-mono font-medium">100</text>
        </svg>

        {/* Numeric Score Overlay in Center Bottom */}
        <div className="absolute inset-x-0 bottom-0 flex flex-col items-center justify-center">
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-bold tracking-tight font-mono text-white">
              {normalizedScore.toFixed(1)}
            </span>
            <span className="text-xs font-semibold text-[#8A998A] font-mono">/ 100</span>
          </div>
          <span className={`text-xs font-bold tracking-wider uppercase mt-0.5 ${currentTheme.textClass}`}>
            {category || currentTheme.label}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RiskGauge;
