import React from 'react';

export const LoadingSpinner: React.FC<{ message?: string; size?: 'sm' | 'md' | 'lg' }> = ({
  message = 'Loading...',
  size = 'md',
}) => {
  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center space-y-3">
      <div
        className={`${sizes[size]} rounded-full border-emerald-500/20 border-t-emerald-500 animate-spin`}
      />
      {message && <p className="text-sm text-slate-400 font-medium">{message}</p>}
    </div>
  );
};

export const EmptyState: React.FC<{
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}> = ({ icon, title, description, action }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center glass-card rounded-2xl border border-slate-800">
      {icon && <div className="p-3 bg-slate-800/80 rounded-2xl mb-4 text-emerald-400">{icon}</div>}
      <h4 className="text-lg font-semibold text-white mb-1">{title}</h4>
      <p className="text-sm text-slate-400 max-w-sm mb-6">{description}</p>
      {action}
    </div>
  );
};

export const ErrorMessage: React.FC<{
  title?: string;
  message: string;
  onRetry?: () => void;
}> = ({ title = 'Something went wrong', message, onRetry }) => {
  return (
    <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 flex items-start justify-between">
      <div>
        <h5 className="font-semibold text-rose-200 text-sm">{title}</h5>
        <p className="text-xs text-rose-300/90 mt-0.5">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs bg-rose-900/60 hover:bg-rose-900 px-2.5 py-1 rounded-md text-white font-medium ml-4 transition"
        >
          Retry
        </button>
      )}
    </div>
  );
};
