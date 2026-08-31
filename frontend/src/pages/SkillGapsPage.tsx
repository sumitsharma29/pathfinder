import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Target,
  SlidersHorizontal,
  Layers,
  ChevronDown
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import { api } from '../api/client';
import { SkillGapAnalysisData, Role } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner, ErrorMessage } from '../components/common/FeedbackStates';

export const SkillGapsPage: React.FC = () => {
  const [data, setData] = useState<SkillGapAnalysisData | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const fetchGaps = async (overrideRoleId?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [gapData, rolesList] = await Promise.all([
        overrideRoleId ? api.analyzeSkillGaps(overrideRoleId) : api.getSkillGaps(),
        api.getRoles(),
      ]);
      setData(gapData);
      setRoles(rolesList);
      setSelectedRoleId(gapData.target_role_id);
    } catch (err: any) {
      setError(err.message || 'Failed to compute dynamic skill gaps');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGaps();
  }, []);

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newRoleId = e.target.value;
    setSelectedRoleId(newRoleId);
    fetchGaps(newRoleId);
  };

  if (isLoading && !data) {
    return <LoadingSpinner message="Calculating dynamic skill delta..." size="lg" />;
  }

  if (error || !data) {
    return (
      <ErrorMessage
        title="Skill Gap Engine"
        message={error || 'Unable to compute skill gaps.'}
        onRetry={() => fetchGaps()}
      />
    );
  }

  // Filter skills
  const categories = ['all', ...Array.from(new Set(data.skills.map((s) => s.category)))];
  const filteredSkills = categoryFilter === 'all'
    ? data.skills
    : data.skills.filter((s) => s.category === categoryFilter);

  // Prepare chart data
  const chartData = filteredSkills.map((s) => ({
    name: s.skill,
    Current: s.current,
    Required: s.required,
    Gap: s.gap,
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header & Role Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Dynamic Skill Gap Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time evaluation against industry proficiency requirements
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Target Role:</span>
          <select
            value={selectedRoleId}
            onChange={handleRoleChange}
            className="bg-slate-900 border border-slate-700 text-white rounded-xl px-3 py-1.5 text-xs font-semibold focus:outline-none focus:border-emerald-500"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary Analytics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <Card className="p-4 space-y-1 text-center">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Required Skills</p>
          <p className="text-2xl font-bold text-white">{data.summary.total_skills_required}</p>
        </Card>

        <Card className="p-4 space-y-1 text-center border-emerald-900/40">
          <p className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Mastered</p>
          <p className="text-2xl font-bold text-emerald-400">{data.summary.skills_mastered}</p>
        </Card>

        <Card className="p-4 space-y-1 text-center border-blue-900/40">
          <p className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider">In Progress</p>
          <p className="text-2xl font-bold text-blue-400">{data.summary.skills_in_progress}</p>
        </Card>

        <Card className="p-4 space-y-1 text-center border-rose-900/40">
          <p className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">Missing</p>
          <p className="text-2xl font-bold text-rose-400">{data.summary.skills_missing}</p>
        </Card>

        <Card className="p-4 space-y-1 text-center">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Avg Gap</p>
          <p className="text-2xl font-bold text-white">{data.summary.average_gap}%</p>
        </Card>

        <Card className="p-4 space-y-1 text-center bg-gradient-to-tr from-emerald-950/60 to-slate-900 border-emerald-500/30">
          <p className="text-[11px] font-semibold text-emerald-300 uppercase tracking-wider">Readiness</p>
          <p className="text-2xl font-bold text-emerald-400">{data.summary.overall_readiness_percentage}%</p>
        </Card>
      </div>

      {/* Recharts Visualizer */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white">Proficiency Comparison</h3>
            <p className="text-xs text-slate-400">Current learner proficiency vs required threshold per skill</p>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`text-xs px-2.5 py-1 rounded-lg transition capitalize font-medium ${
                  categoryFilter === cat
                    ? 'bg-emerald-500 text-slate-950 font-semibold'
                    : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="h-72 sm:h-96 w-full pt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="name"
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                interval={0}
                angle={-30}
                textAnchor="end"
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                }}
              />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px' }} />
              <Bar dataKey="Current" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Required" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Granular Skill Gap Table */}
      <Card className="p-6">
        <h3 className="text-lg font-bold text-white mb-4">Detailed Skill Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="pb-3 px-2">Skill</th>
                <th className="pb-3 px-2">Category</th>
                <th className="pb-3 px-2">Current</th>
                <th className="pb-3 px-2">Required</th>
                <th className="pb-3 px-2">Gap Delta</th>
                <th className="pb-3 px-2">Importance</th>
                <th className="pb-3 px-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredSkills.map((s) => (
                <tr key={s.skill_id} className="hover:bg-slate-900/40 transition">
                  <td className="py-3 px-2 font-semibold text-white">{s.skill}</td>
                  <td className="py-3 px-2 text-slate-400 capitalize">{s.category}</td>
                  <td className="py-3 px-2 font-mono font-medium text-emerald-400">{s.current}%</td>
                  <td className="py-3 px-2 font-mono font-medium text-blue-400">{s.required}%</td>
                  <td className="py-3 px-2 font-mono font-bold text-rose-400">{s.gap}%</td>
                  <td className="py-3 px-2 text-slate-300">{(s.importance * 100).toFixed(0)}%</td>
                  <td className="py-3 px-2 text-right">
                    <Badge
                      variant={
                        s.status === 'MASTERED'
                          ? 'success'
                          : s.status === 'PARTIAL'
                          ? 'info'
                          : 'danger'
                      }
                      size="sm"
                    >
                      {s.status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
