import React, { useState, useEffect } from 'react';
import {
  Map,
  CheckCircle2,
  Lock,
  Play,
  RotateCcw,
  Sparkles,
  ExternalLink,
  Clock,
  Layers,
  ChevronRight,
  Info,
  BookOpen
} from 'lucide-react';
import { api } from '../api/client';
import { RoadmapSummaryResponse, RoadmapItem } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner, ErrorMessage, EmptyState } from '../components/common/FeedbackStates';

export const RoadmapPage: React.FC = () => {
  const [roadmap, setRoadmap] = useState<RoadmapSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedLockedItem, setSelectedLockedItem] = useState<RoadmapItem | null>(null);

  const fetchRoadmap = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getCurrentRoadmap();
      setRoadmap(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve active learning roadmap');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleStartItem = async (itemId: string) => {
    setActionLoading(itemId);
    try {
      await api.startRoadmapItem(itemId);
      await fetchRoadmap();
    } catch (err: any) {
      alert(err.message || 'Failed to start milestone');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCompleteItem = async (itemId: string) => {
    setActionLoading(itemId);
    try {
      await api.completeRoadmapItem(itemId);
      await fetchRoadmap();
    } catch (err: any) {
      alert(err.message || 'Failed to complete milestone');
    } finally {
      setActionLoading(null);
    }
  };

  const handleRecalculate = async () => {
    if (!roadmap) return;
    setIsLoading(true);
    try {
      await api.recalculateRoadmap(roadmap.roadmap_id);
      await fetchRoadmap();
    } catch (err: any) {
      setError(err.message || 'Failed to recalculate roadmap');
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading topological learning path..." size="lg" />;
  }

  if (error || !roadmap) {
    return (
      <ErrorMessage
        title="Roadmap Unavailable"
        message={error || 'No active roadmap found.'}
        onRetry={fetchRoadmap}
      />
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header & Meta */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Personalized Learning Roadmap
            </h1>
            <Badge variant="purple" size="sm">
              Version {roadmap.version}
            </Badge>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Topologically ordered learning path • {roadmap.completed_items} of {roadmap.total_items} milestones completed ({roadmap.overall_progress}%)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={handleRecalculate}>
            <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> Recalculate Path
          </Button>
        </div>
      </div>

      {/* Progress Bar Header */}
      <div className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 glass-card">
        <div className="flex items-center justify-between text-xs text-slate-400 mb-2 font-semibold">
          <span>Overall Progression</span>
          <span className="text-emerald-400 font-mono text-sm">{roadmap.overall_progress}%</span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-emerald-500 to-teal-400 h-2.5 rounded-full transition-all duration-700"
            style={{ width: `${roadmap.overall_progress}%` }}
          />
        </div>
      </div>

      {/* Topological Milestones Timeline */}
      <div className="space-y-4 relative before:absolute before:inset-0 before:left-6 sm:before:left-8 before:w-0.5 before:bg-slate-800/80 before:z-0">
        {roadmap.items.map((item, index) => {
          const isCompleted = item.status === 'COMPLETED';
          const isInProgress = item.status === 'IN_PROGRESS';
          const isAvailable = item.status === 'AVAILABLE';
          const isLocked = item.status === 'LOCKED';

          const title = item.skill?.name || item.resource?.title || item.project?.title || `Milestone ${item.sequence}`;
          const duration = item.estimated_hours ? `${item.estimated_hours}h` : '1h';

          return (
            <div key={item.id} className="relative z-10 flex items-start gap-4 sm:gap-6 group">
              {/* Sequence Node Indicator */}
              <div
                className={`w-12 h-12 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-300 ${
                  isCompleted
                    ? 'bg-emerald-950 border-emerald-600 text-emerald-400 shadow-lg shadow-emerald-500/20'
                    : isInProgress
                    ? 'bg-blue-950 border-blue-500 text-blue-400 glow-blue animate-pulse'
                    : isAvailable
                    ? 'bg-slate-900 border-amber-500/80 text-amber-400'
                    : 'bg-slate-950 border-slate-800 text-slate-600'
                }`}
              >
                {isCompleted ? (
                  <CheckCircle2 className="w-6 h-6" />
                ) : isLocked ? (
                  <Lock className="w-5 h-5" />
                ) : (
                  <span className="font-bold font-mono text-sm sm:text-base">#{item.sequence}</span>
                )}
              </div>

              {/* Milestone Card */}
              <Card
                className={`flex-1 p-5 border transition-all ${
                  isInProgress
                    ? 'border-blue-500/40 bg-slate-900/90 shadow-lg'
                    : isAvailable
                    ? 'border-slate-700 bg-slate-900/70 hover:border-slate-600'
                    : isCompleted
                    ? 'border-emerald-900/40 bg-slate-900/40 opacity-90'
                    : 'border-slate-800/60 bg-slate-950/60 opacity-60 cursor-not-allowed'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1.5 max-w-xl">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge
                        variant={
                          isCompleted
                            ? 'success'
                            : isInProgress
                            ? 'info'
                            : isAvailable
                            ? 'warning'
                            : 'default'
                        }
                        size="sm"
                      >
                        {item.status}
                      </Badge>
                      {item.skill?.category && (
                        <span className="text-xs text-slate-400 font-medium px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                          {item.skill.category}
                        </span>
                      )}
                      <span className="text-xs text-slate-400 flex items-center gap-1 font-mono">
                        <Clock className="w-3.5 h-3.5" /> {duration}
                      </span>
                    </div>

                    <h3 className="text-base sm:text-lg font-bold text-white leading-snug">
                      {title}
                    </h3>

                    {item.resource && (
                      <p className="text-xs text-slate-300 line-clamp-1">
                        Resource: <span className="text-emerald-400 font-semibold">{item.resource.title}</span> ({item.resource.provider || 'Self-paced'})
                      </p>
                    )}

                    {isLocked && item.locked_reason && (
                      <button
                        onClick={() => setSelectedLockedItem(item)}
                        className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 mt-1 underline font-medium"
                      >
                        <Info className="w-3.5 h-3.5" /> View Prerequisite Lock Details
                      </button>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {item.resource?.url && (
                      <a
                        href={item.resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition text-xs font-medium inline-flex items-center gap-1"
                      >
                        <BookOpen className="w-4 h-4" /> Material
                      </a>
                    )}

                    {isAvailable && (
                      <Button
                        size="sm"
                        onClick={() => handleStartItem(item.id)}
                        isLoading={actionLoading === item.id}
                      >
                        <Play className="w-3.5 h-3.5 mr-1" /> Start
                      </Button>
                    )}

                    {isInProgress && (
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleCompleteItem(item.id)}
                        isLoading={actionLoading === item.id}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Complete
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            </div>
          );
        })}
      </div>

      {/* Lock Details Modal */}
      <Modal
        isOpen={!!selectedLockedItem}
        onClose={() => setSelectedLockedItem(null)}
        title="Milestone Locked by Prerequisites"
      >
        {selectedLockedItem && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <h4 className="text-sm font-bold text-white mb-1">
                {selectedLockedItem.skill?.name || 'Milestone'}
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                {selectedLockedItem.locked_reason || 'This milestone requires foundational prerequisite knowledge before it can be unlocked.'}
              </p>
            </div>
            <p className="text-xs text-slate-400">
              Complete upstream roadmap milestones or pass prerequisite assessments to unlock this milestone automatically.
            </p>
            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setSelectedLockedItem(null)}>
                Got it
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
