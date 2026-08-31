import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BrainCircuit,
  Target,
  Clock,
  CheckCircle2,
  Sliders,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { GoalAnalysisData, Role } from '../types/api';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { ErrorMessage } from '../components/common/FeedbackStates';

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();

  // Steps: 1 = Goal Prompt, 2 = AI Grounding Review, 3 = Skill Baseline Tuning, 4 = Generate Roadmap
  const [step, setStep] = useState<number>(1);
  const [goalText, setGoalText] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [analysis, setAnalysis] = useState<GoalAnalysisData | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [dailyHours, setDailyHours] = useState<number>(2.0);
  const [timelineWeeks, setTimelineWeeks] = useState<number>(24);
  const [skillProficiencies, setSkillProficiencies] = useState<Record<string, number>>({});
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getRoles().then(setRoles).catch(console.error);
  }, []);

  const handleAnalyzeGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalText.trim()) return;

    setError(null);
    setIsAnalyzing(true);
    try {
      const res = await api.analyzeGoal(goalText);
      setAnalysis(res);

      if (res.role_id) {
        setSelectedRoleId(res.role_id);
      } else if (roles.length > 0) {
        setSelectedRoleId(roles[0].id);
      }

      if (res.daily_study_hours) {
        setDailyHours(res.daily_study_hours);
      }
      if (res.timeline_weeks) {
        setTimelineWeeks(res.timeline_weeks);
      }

      // Populate baseline skills
      const initialSkills: Record<string, number> = {};
      if (res.known_skills && res.known_skills.length > 0) {
        res.known_skills.forEach((s) => {
          if (s.skill_id) {
            initialSkills[s.skill_id] = 50; // default baseline proficiency
          }
        });
      }
      setSkillProficiencies(initialSkills);

      setStep(2);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze learning goal');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCompleteOnboarding = async () => {
    if (!selectedRoleId) {
      setError('Please select a target career role.');
      return;
    }

    setError(null);
    setIsGenerating(true);
    try {
      // 1. Update learner profile with target role & study hours
      await api.updateProfile({
        target_role_id: selectedRoleId,
        daily_study_hours: dailyHours,
        target_duration_weeks: timelineWeeks,
      });

      // 2. Add tuned baseline skills
      for (const [skillId, prof] of Object.entries(skillProficiencies)) {
        if (prof > 0) {
          try {
            await api.addLearnerSkill(skillId, prof);
          } catch (e) {
            try {
              await api.updateLearnerSkill(skillId, prof);
            } catch (ignore) {}
          }
        }
      }

      // 3. Generate initial topological roadmap
      await api.generateRoadmap(selectedRoleId, timelineWeeks);

      // 4. Redirect to learner dashboard
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to construct learning roadmap');
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-8">
          {[
            { num: 1, label: 'Goal Intent' },
            { num: 2, label: 'AI Grounding' },
            { num: 3, label: 'Baseline Skills' },
          ].map((s) => (
            <div key={s.num} className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition ${
                  step === s.num
                    ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/25'
                    : step > s.num
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    : 'bg-slate-900 text-slate-500 border border-slate-800'
                }`}
              >
                {step > s.num ? <CheckCircle2 className="w-4 h-4" /> : s.num}
              </div>
              <span className={`text-xs font-semibold hidden sm:inline ${step === s.num ? 'text-white' : 'text-slate-500'}`}>
                {s.label}
              </span>
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-6">
            <ErrorMessage title="Action required" message={error} />
          </div>
        )}

        {/* Step 1: Natural Language Goal Prompt */}
        {step === 1 && (
          <Card className="p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-emerald-950/80 rounded-xl text-emerald-400 border border-emerald-800/60">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">What is your career goal?</h2>
                <p className="text-xs text-slate-400">Our AI parses your goals, timeline, and current background.</p>
              </div>
            </div>

            <form onSubmit={handleAnalyzeGoal} className="space-y-6">
              <div>
                <textarea
                  rows={4}
                  required
                  value={goalText}
                  onChange={(e) => setGoalText(e.target.value)}
                  placeholder="e.g. I want to become an AI/ML engineer in six months. I know basic Python, but I am weak in statistics and linear algebra. I can study about 2 hours every day."
                  className="w-full bg-slate-900/80 border border-slate-700/80 rounded-xl p-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition leading-relaxed resize-none"
                />
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="text-xs text-slate-400 font-medium self-center mr-1">Quick Prompts:</span>
                {[
                  'Become a full-stack Python engineer in 3 months',
                  'Transition from data analyst to ML Engineer studying 2h/day',
                  'Master Deep Learning and PyTorch from scratch',
                ].map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    onClick={() => setGoalText(sample)}
                    className="text-[11px] bg-slate-900 hover:bg-slate-800 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-800 transition"
                  >
                    "{sample}"
                  </button>
                ))}
              </div>

              <Button type="submit" size="lg" isLoading={isAnalyzing} className="w-full">
                <Sparkles className="w-4 h-4 mr-2" />
                Analyze with Grounded AI
              </Button>
            </form>
          </Card>
        )}

        {/* Step 2: AI Grounding Review */}
        {step === 2 && analysis && (
          <Card className="p-6 sm:p-8 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-950/80 rounded-xl text-blue-400 border border-blue-800/60">
                  <Target className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">AI Grounded Understanding</h2>
                  <p className="text-xs text-slate-400">Review the target role and parameters extracted from your goal.</p>
                </div>
              </div>
              <Badge variant={analysis.confidence >= 0.8 ? 'success' : 'warning'}>
                {Math.round(analysis.confidence * 100)}% Confidence
              </Badge>
            </div>

            {/* Target Role Selection */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Target Career Role
              </label>
              <select
                value={selectedRoleId}
                onChange={(e) => setSelectedRoleId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Time & Study Commitment */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="glass-card rounded-xl p-4 border border-slate-800">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  <Clock className="w-4 h-4 text-emerald-400" />
                  Daily Study Hours
                </div>
                <input
                  type="number"
                  min="0.5"
                  max="12"
                  step="0.5"
                  value={dailyHours}
                  onChange={(e) => setDailyHours(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white"
                />
              </div>

              <div className="glass-card rounded-xl p-4 border border-slate-800">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-2">
                  <Clock className="w-4 h-4 text-blue-400" />
                  Target Duration (Weeks)
                </div>
                <input
                  type="number"
                  min="2"
                  max="52"
                  value={timelineWeeks}
                  onChange={(e) => setTimelineWeeks(parseInt(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white"
                />
              </div>
            </div>

            {analysis.clarification_prompt && (
              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-400 leading-relaxed">
                <strong className="text-slate-200">AI Prompt Note:</strong> {analysis.clarification_prompt}
              </div>
            )}

            <div className="flex items-center justify-between pt-4">
              <Button variant="ghost" onClick={() => setStep(1)}>
                Back to Prompt
              </Button>
              <Button onClick={() => setStep(3)}>
                Proceed to Skills <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </div>
          </Card>
        )}

        {/* Step 3: Baseline Skill Tuning & Generation */}
        {step === 3 && (
          <Card className="p-6 sm:p-8 space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
              <div className="p-2 bg-emerald-950/80 rounded-xl text-emerald-400 border border-emerald-800/60">
                <Sliders className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Fine-tune Your Skill Proficiencies</h2>
                <p className="text-xs text-slate-400">Set your baseline knowledge level (0 = Beginner, 100 = Expert).</p>
              </div>
            </div>

            <div className="space-y-4 max-h-[360px] overflow-y-auto pr-2">
              {analysis?.known_skills.map((skill) => {
                if (!skill.skill_id) return null;
                const currentVal = skillProficiencies[skill.skill_id] ?? 50;

                return (
                  <div key={skill.skill_id} className="glass-card rounded-xl p-4 border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sm text-white">{skill.matched_name || skill.name}</span>
                      <span className="text-xs font-mono font-bold text-emerald-400">{currentVal}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={currentVal}
                      onChange={(e) =>
                        setSkillProficiencies({
                          ...skillProficiencies,
                          [skill.skill_id!]: parseInt(e.target.value),
                        })
                      }
                      className="w-full accent-emerald-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
                    />
                  </div>
                );
              })}
              {(!analysis?.known_skills || analysis.known_skills.filter((s) => s.skill_id).length === 0) && (
                <p className="text-xs text-slate-400 p-4 text-center">
                  No specific baseline skills detected. You will start fresh with beginner baseline proficiencies.
                </p>
              )}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <Button variant="ghost" onClick={() => setStep(2)}>
                Back
              </Button>
              <Button onClick={handleCompleteOnboarding} isLoading={isGenerating} size="lg">
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Roadmap & Launch Dashboard
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};
