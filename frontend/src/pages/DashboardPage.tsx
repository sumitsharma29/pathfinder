import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Clock,
  BookOpen,
  Target,
  Zap,
  TrendingUp,
  Award,
  ChevronRight,
  RotateCcw
} from 'lucide-react';
import { api } from '../api/client';
import {
  OverallProgressResponse,
  SkillGapAnalysisData,
  NextBestActionResponse,
  RecommendationItem,
  LearnerProfile
} from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner, ErrorMessage, EmptyState } from '../components/common/FeedbackStates';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [progress, setProgress] = useState<OverallProgressResponse | null>(null);
  const [gaps, setGaps] = useState<SkillGapAnalysisData | null>(null);
  const [nextAction, setNextAction] = useState<NextBestActionResponse | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [profData, progData, gapData, nbaData, recData] = await Promise.all([
        api.getProfile().catch(() => null),
        api.getOverallProgress().catch(() => null),
        api.getSkillGaps().catch(() => null),
        api.getNextBestAction().catch(() => null),
        api.getRecommendations({ page_size: 3 }).catch(() => []),
      ]);

      setProfile(profData);
      setProgress(progData);
      setGaps(gapData);
      setNextAction(nbaData);
      setRecommendations(recData || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load learner dashboard telemetry');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Assembling real-time learning metrics..." size="lg" />;
  }

  if (error) {
    return <ErrorMessage title="Dashboard Sync Error" message={error} onRetry={fetchDashboardData} />;
  }

  // If no target role or no roadmap
  if (!profile?.target_role || !progress?.active_roadmap_id) {
    return (
      <EmptyState
        icon={<Target className="w-8 h-8" />}
        title="No Active Learning Roadmap"
        description="You haven't configured a target career role or generated your personalized roadmap yet."
        action={
          <Button onClick={() => navigate('/onboarding')}>
            Launch AI Goal Setup <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        }
      />
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. Top Section: Header & Next Best Action Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Learner Command Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Targeting <span className="text-emerald-400 font-semibold">{profile.target_role?.name || 'Selected Career Track'}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={fetchDashboardData}>
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Sync Telemetry
          </Button>
          <Button size="sm" onClick={() => navigate('/assistant')}>
            <Sparkles className="w-3.5 h-3.5 mr-1.5" /> Ask AI Assistant
          </Button>
        </div>
      </div>

      {/* 5. What should I do next? (Next Best Action Banner) */}
      {nextAction && (
        <Card className="p-6 border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-slate-900/80 relative overflow-hidden glow-brand">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                <Badge variant="success" size="sm">
                  NEXT BEST ACTION
                </Badge>
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold font-mono">
                  {nextAction.action_type.replace('_', ' ')}
                </span>
              </div>
              <h3 className="text-lg sm:text-xl font-bold text-white">{nextAction.title}</h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">{nextAction.reason}</p>
            </div>

            <Button
              onClick={() => {
                if (nextAction.action_type === 'attempt_assessment' && nextAction.assessment_id) {
                  navigate(`/assessments/${nextAction.assessment_id}`);
                } else {
                  navigate('/roadmap');
                }
              }}
              size="lg"
              className="w-full md:w-auto shrink-0 shadow-lg shadow-emerald-500/20"
            >
              Take Action Now <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </Card>
      )}

      {/* 2. Core Telemetry Metrics Grid (Where am I & What have I completed) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <Card hoverEffect className="space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Overall Roadmap</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{progress.overall_percentage}%</span>
            <span className="text-xs text-slate-400">
              ({progress.completed_items}/{progress.total_items} items)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${progress.overall_percentage}%` }}
            />
          </div>
        </Card>

        <Card hoverEffect className="space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Role Readiness</span>
            <Award className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {gaps?.summary.overall_readiness_percentage ?? 0}%
            </span>
            <span className="text-xs text-slate-400">
              ({gaps?.summary.skills_mastered ?? 0}/{gaps?.summary.total_skills_required ?? 0} Mastered)
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${gaps?.summary.overall_readiness_percentage ?? 0}%` }}
            />
          </div>
        </Card>

        <Card hoverEffect className="space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Actual Study Time</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {Math.floor(progress.time_spent_minutes / 60)}h {progress.time_spent_minutes % 60}m
            </span>
            <span className="text-xs text-slate-400">logged</span>
          </div>
          <p className="text-[11px] text-slate-400">Target: {profile.daily_study_hours ?? 2} hrs/day</p>
        </Card>

        <Card hoverEffect className="space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <span>Skill Gaps</span>
            <Target className="w-4 h-4 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              {(gaps?.summary.skills_in_progress ?? 0) + (gaps?.summary.skills_missing ?? 0)}
            </span>
            <span className="text-xs text-slate-400">skills pending</span>
          </div>
          <Link to="/skill-gaps" className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 font-medium">
            View Skill Breakdown <ChevronRight className="w-3 h-3" />
          </Link>
        </Card>
      </div>

      {/* 3 & 4: What am I learning & What am I weak at */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Learning Milestone */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">Current Learning Milestone</h3>
              </div>
              <Link to="/roadmap" className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1">
                Full Roadmap <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {progress.current_milestone ? (
              <div className="glass-card rounded-xl p-5 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Badge variant={progress.current_milestone.status === 'IN_PROGRESS' ? 'info' : 'warning'}>
                      {progress.current_milestone.status}
                    </Badge>
                    <span className="text-xs text-slate-400 font-mono">Step #{progress.current_milestone.sequence_order}</span>
                  </div>
                  <h4 className="text-base font-bold text-white">{progress.current_milestone.title}</h4>
                  <p className="text-xs text-slate-400">
                    Skill: <strong className="text-slate-200">{progress.current_milestone.skill_name}</strong> • Est: {progress.current_milestone.estimated_minutes} mins
                  </p>
                </div>

                <Button onClick={() => navigate('/roadmap')} size="sm">
                  Continue Milestone
                </Button>
              </div>
            ) : (
              <p className="text-xs text-slate-400">All milestones in the active roadmap are completed!</p>
            )}
          </Card>

          {/* Personalized Recommendations */}
          <Card className="p-6">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <h3 className="text-base font-bold text-white">Recommended For You</h3>
              </div>
              <Link to="/resources" className="text-xs text-slate-400 hover:text-slate-200">
                Browse All Resources
              </Link>
            </div>

            {recommendations.length > 0 ? (
              <div className="space-y-3">
                {recommendations.map((rec) => (
                  <div
                    key={rec.recommendation_id}
                    className="p-4 rounded-xl glass-card border border-slate-800 flex items-center justify-between gap-4 hover:border-slate-700 transition"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="default" size="sm">
                          {rec.resource_type.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-slate-400 font-medium">{rec.difficulty}</span>
                      </div>
                      <a
                        href={rec.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-semibold text-white hover:text-emerald-400 transition"
                      >
                        {rec.title}
                      </a>
                      <p className="text-xs text-slate-400">{rec.reason.primary_reason}</p>
                    </div>

                    <a
                      href={rec.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No active recommendations at this time.</p>
            )}
          </Card>
        </div>

        {/* Weak Skills & Interventions Sidebar */}
        <div className="space-y-6">
          <Card className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-rose-400" />
                <h3 className="text-base font-bold text-white">Priority Focus Skills</h3>
              </div>
            </div>

            <p className="text-xs text-slate-400">
              Skills with largest delta against requirements for {profile.target_role.name}:
            </p>

            <div className="space-y-3">
              {gaps?.skills
                .filter((s) => s.status !== 'MASTERED')
                .slice(0, 5)
                .map((s) => (
                  <div key={s.skill_id} className="p-3 bg-slate-900/80 rounded-xl border border-slate-800">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-white">{s.skill}</span>
                      <span className="text-rose-400 font-bold font-mono">Gap: {s.gap}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-rose-500 h-1.5 rounded-full"
                        style={{ width: `${s.current}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                      <span>Current: {s.current}%</span>
                      <span>Target: {s.required}%</span>
                    </div>
                  </div>
                ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              className="w-full mt-2"
              onClick={() => navigate('/assessments')}
            >
              Take Skill Assessments
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
};
