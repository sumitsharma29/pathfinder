import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Compass,
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
} from 'lucide-react';

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
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-500/20">
            <Compass className="w-5 h-5 text-slate-950" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              PathFinder <span className="text-emerald-400 text-xs px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/60 font-mono">AI</span>
            </span>
            <p className="text-[10px] text-slate-400">Career Navigator</p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-1.5">
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
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/80 border border-transparent'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 transition-transform group-hover:scale-110" />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-400 border border-blue-800/60">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Banner */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="glass-card rounded-xl p-3.5 border border-emerald-900/40 relative overflow-hidden">
            <div className="flex items-center gap-2 mb-1.5">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-semibold text-white">Adaptive Learning</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Every assessment automatically optimizes your roadmap.
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
