import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  BarChart3,
  BookOpen,
  CheckSquare,
  Bot,
  User,
  Settings,
  Sparkles,
  Zap,
  Presentation,
} from 'lucide-react';
import { Logo } from './Logo';

interface SidebarProps {
  isOpen: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/roadmap', label: 'My Roadmap', icon: Map },
    { to: '/skill-gaps', label: 'Skill Gaps', icon: BarChart3 },
    { to: '/resources', label: 'Resource Catalog', icon: BookOpen },
    { to: '/assessments', label: 'Assessments', icon: CheckSquare },
    { to: '/assistant', label: 'AI Assistant', icon: Bot, badge: 'RAG' },
    { to: '/adaptive-update', label: 'Adaptive Engine', icon: Zap },
    { to: '/profile', label: 'Profile & Skills', icon: User },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-950/80 z-40 lg:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-950/95 backdrop-blur-xl border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 shadow-2xl ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center px-5 border-b border-slate-800/80">
          <Logo size="sm" showText={true} />
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3.5 py-5 space-y-1.5 custom-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-500/15 to-emerald-500/15 text-cyan-300 border border-cyan-500/30 font-semibold shadow-sm shadow-cyan-950/50'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/80 border border-transparent'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-cyan-950/90 text-cyan-400 border border-cyan-800/60 font-mono">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Ambient Banner */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="glass-card rounded-xl p-3.5 border border-cyan-900/40 relative overflow-hidden bg-gradient-to-br from-slate-900/90 via-slate-950/90 to-cyan-950/30">
            <div className="flex items-center gap-2 mb-1.5">
              <div className="w-5 h-5 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              </div>
              <span className="text-xs font-bold text-white tracking-tight">Adaptive Core</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Dynamically recalibrates prerequisites upon assessment completion.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
