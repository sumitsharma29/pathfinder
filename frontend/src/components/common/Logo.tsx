import React from 'react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

export const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showText = true,
  className = '',
}) => {
  const sizeMap = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const textMap = {
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl',
  };

  return (
    <div className={`flex items-center gap-2.5 select-none ${className}`}>
      <div className={`relative ${sizeMap[size]} flex-shrink-0 group`}>
        {/* Ambient Glow */}
        <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full blur-md opacity-40 group-hover:opacity-75 transition duration-500"></div>
        
        {/* SVG Mark */}
        <svg
          viewBox="0 0 512 512"
          className="relative w-full h-full drop-shadow-[0_0_12px_rgba(6,182,212,0.5)] transition-transform duration-300 group-hover:scale-105"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="logo-grad-1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06B6D4" />
              <stop offset="50%" stopColor="#10B981" />
              <stop offset="100%" stopColor="#3B82F6" />
            </linearGradient>
            <linearGradient id="logo-grad-2" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#34D399" />
            </linearGradient>
          </defs>

          {/* Orbit Rings */}
          <circle cx="256" cy="256" r="210" stroke="url(#logo-grad-1)" strokeWidth="8" strokeDasharray="16 16" opacity="0.5" />
          <circle cx="256" cy="256" r="160" stroke="#0ea5e9" strokeWidth="6" opacity="0.4" />
          <circle cx="256" cy="256" r="110" stroke="#10b981" strokeWidth="8" strokeDasharray="24 12" opacity="0.7" />

          {/* Outer Topological Diamond */}
          <polygon points="256,60 452,256 256,452 60,256" stroke="url(#logo-grad-1)" strokeWidth="12" fill="none" opacity="0.85" />

          {/* Nodes */}
          <circle cx="256" cy="60" r="22" fill="#0284c7" stroke="#38bdf8" strokeWidth="6" />
          <circle cx="452" cy="256" r="22" fill="#059669" stroke="#34d399" strokeWidth="6" />
          <circle cx="256" cy="452" r="22" fill="#2563eb" stroke="#60a5fa" strokeWidth="6" />
          <circle cx="60" cy="256" r="22" fill="#0d9488" stroke="#2dd4bf" strokeWidth="6" />

          {/* Navigation Arrow Core */}
          <path d="M256 120 L340 330 L256 285 L172 330 Z" fill="url(#logo-grad-1)" />
          <circle cx="256" cy="256" r="24" fill="#38bdf8" />
          <circle cx="256" cy="256" r="12" fill="#ffffff" />
        </svg>
      </div>

      {showText && (
        <div className="flex flex-col leading-none">
          <div className="flex items-center gap-1.5">
            <span className={`font-black tracking-tight text-white ${textMap[size]}`}>
              PathFinder
            </span>
            <span className={`font-extrabold bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent ${textMap[size]}`}>
              NEXUS
            </span>
          </div>
          <span className="text-[9px] uppercase tracking-widest text-cyan-400/80 font-mono font-medium mt-0.5">
            Autonomous Learning Navigator
          </span>
        </div>
      )}
    </div>
  );
};
