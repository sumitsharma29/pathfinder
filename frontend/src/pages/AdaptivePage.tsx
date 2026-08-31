import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Zap,
  Sparkles,
  AlertTriangle,
  Layers,
  ArrowRight,
  RotateCcw,
  CheckCircle2,
  TrendingDown,
  ShieldAlert
} from 'lucide-react';
import { api } from '../api/client';
import { AdaptiveEvaluationResponse } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner, ErrorMessage } from '../components/common/FeedbackStates';

export const AdaptivePage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<AdaptiveEvaluationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const runEvaluation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.evaluateAdaptation('MANUAL_EVALUATION');
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger adaptive evaluation loop');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runEvaluation();
  }, []);

  if (isLoading && !data) {
    return <LoadingSpinner message="Evaluating learner state and adaptive interventions..." size="lg" />;
  }

  if (error || !data) {
    return <ErrorMessage title="Adaptive Engine" message={error || 'Unable to load adaptive evaluation.'} onRetry={runEvaluation} />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Adaptive Learning Engine
            </h1>
            <Badge variant="purple" size="sm">
              Continuous Recalibration
            </Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Dynamic telemetry feedback loop adapting roadmaps to your actual evidence and speed
          </p>
        </div>

        <Button onClick={runEvaluation} isLoading={isLoading}>
          <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Re-evaluate State
        </Button>
      </div>

      {/* Next Best Action Card */}
      {data.next_best_action && (
        <Card className="p-6 border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-slate-900/80 glow-brand">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Badge variant="success" size="sm">
                  ADAPTED NEXT ACTION
                </Badge>
                <span className="text-xs text-slate-400 font-mono capitalize">
                  {data.next_best_action.action_type.replace('_', ' ')}
                </span>
              </div>
              <h3 className="text-lg font-bold text-white">{data.next_best_action.title}</h3>
              <p className="text-xs text-slate-300">{data.next_best_action.reason}</p>
            </div>

            <Button onClick={() => navigate('/roadmap')} size="sm">
              View on Roadmap <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </div>
        </Card>
      )}

      {/* Selected Interventions Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          Active Interventions & Adjustments
        </h3>

        {data.interventions_selected.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {data.interventions_selected.map((inv) => (
              <Card key={inv.skill_id} className="p-5 space-y-3 border-amber-800/40 bg-slate-900/60">
                <div className="flex items-center justify-between">
                  <Badge variant="warning" size="sm">
                    {inv.intervention_type.replace('_', ' ')}
                  </Badge>
                  <span className="text-xs text-slate-400 font-mono">Priority #{inv.priority}</span>
                </div>

                <div>
                  <h4 className="text-base font-bold text-white">{inv.skill_name}</h4>
                  <p className="text-xs text-slate-300 mt-1 leading-relaxed">{inv.explanation}</p>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center text-slate-400 text-sm">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            No urgent interventions required. You are on track with your learning milestones!
          </Card>
        )}
      </div>

      {/* Weak Skills Detected */}
      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-rose-400" />
          Detected Weak Areas ({data.weak_skills_detected.length})
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.weak_skills_detected.map((w) => (
            <div key={w.skill_id} className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <h5 className="font-semibold text-sm text-white">{w.skill_name}</h5>
                <span className="text-xs text-rose-400 font-mono font-bold">Gap: {w.gap}%</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{w.reason}</p>
              <div className="flex justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800">
                <span>Current: {w.current_proficiency}%</span>
                <span>Target: {w.required_proficiency}%</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
