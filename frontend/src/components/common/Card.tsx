import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hoverEffect?: boolean;
  glow?: 'none' | 'brand' | 'blue';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hoverEffect = false,
  glow = 'none',
  ...props
}) => {
  const glowClasses = {
    none: '',
    brand: 'border-emerald-500/30 glow-brand',
    blue: 'border-blue-500/30 glow-blue',
  };

  return (
    <div
      className={`glass-card rounded-xl p-5 border border-slate-800/80 transition-all ${
        hoverEffect ? 'hover:border-slate-700 hover:shadow-xl hover:translate-y-[-2px]' : ''
      } ${glowClasses[glow]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
