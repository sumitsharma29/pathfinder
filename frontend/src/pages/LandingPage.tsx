import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Layers,
  BrainCircuit,
  CheckCircle2,
  Presentation,
  Compass,
  GitBranch,
  Search,
  BookOpen,
  Award
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { Logo } from '../components/common/Logo';

export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  return (
    <div className="relative overflow-hidden selection:bg-cyan-500 selection:text-slate-950">
      {/* Background Glows & Ambience */}
      <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[700px] h-[500px] bg-gradient-to-tr from-cyan-600/20 via-emerald-600/15 to-blue-600/20 rounded-full blur-[120px] pointer-events-none -z-10" />
      <div className="absolute top-1/3 left-1/4 w-[450px] h-[450px] bg-teal-500/10 rounded-full blur-[100px] pointer-events-none -z-10" />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-300 text-xs font-semibold mb-8 shadow-sm shadow-cyan-950">
          <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
          Next-Gen Autonomous Learning Navigation Platform
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white max-w-5xl mx-auto leading-[1.12] mb-6">
          Turn your career ambitions into an{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
            intelligent topological roadmap.
          </span>
        </h1>

        <p className="text-base sm:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed font-normal">
          <strong className="text-white font-semibold">PathFinder Nexus</strong> analyzes your natural-language goals, mathematically computes skill gaps, builds strict Kahn's DAG prerequisite roadmaps, and adapts dynamically with server-graded assessments.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-16">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="w-full sm:w-auto">
                <Button size="lg" className="w-full sm:w-auto shadow-xl shadow-cyan-500/25 bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold">
                  Go to Dashboard <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <Link to="/roadmap" className="w-full sm:w-auto">
                <Button variant="outline" size="lg" className="w-full sm:w-auto border-slate-700 hover:border-cyan-500/50">
                  View My Roadmap
                </Button>
              </Link>
            </>
          ) : (
            <>
              <Link to="/register" className="w-full sm:w-auto">
                <Button size="lg" className="w-full sm:w-auto shadow-xl shadow-cyan-500/25 bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold">
                  Build Your Learning Plan <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <Link to="/login" className="w-full sm:w-auto">
                <Button variant="outline" size="lg" className="w-full sm:w-auto border-slate-700 hover:border-cyan-500/50">
                  Sign In to Account
                </Button>
              </Link>
            </>
          )}
        </div>

        {/* Architectural Creed Card */}
        <div className="max-w-4xl mx-auto mb-20 p-6 rounded-2xl bg-slate-900/60 border border-slate-800/90 backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-500 via-teal-400 to-emerald-500" />
          <p className="text-xs uppercase tracking-widest text-cyan-400 font-mono font-semibold mb-2">Core System Philosophy</p>
          <blockquote className="text-lg sm:text-xl font-medium text-slate-200 italic">
            "RAG retrieves. LLMs explain. The Database grounds. Deterministic engines decide."
          </blockquote>
        </div>

        {/* 7 Core Engines Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto text-left">
          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-cyan-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400 mb-4 group-hover:scale-105 transition-transform">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">1. AI Goal Understanding</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Extracts target roles, timeline, and current skills from free-form goals using Gemini with Pydantic validation.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-teal-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-teal-950/80 border border-teal-800/60 flex items-center justify-center text-teal-400 mb-4 group-hover:scale-105 transition-transform">
              <GitBranch className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">2. Topological Kahn's DAG</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Prerequisite graph engine guarantees foundational milestones strictly precede advanced topics with zero cycles.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-emerald-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 mb-4 group-hover:scale-105 transition-transform">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">3. Dynamic Skill Gap Engine</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Formulaic real-time gap computation without static persistence: Gap = max(Required - Current, 0).
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-blue-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400 mb-4 group-hover:scale-105 transition-transform">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">4. 6-Factor Recommendation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Transparent multi-objective resource ranking (Gap 30%, Prereq 20%, Goal 15%, Difficulty 15%, Time 10%, Pref 10%).
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-purple-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400 mb-4 group-hover:scale-105 transition-transform">
              <Award className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">5. Server-Graded Assessment</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Sanitized delivery with authoritative backend grading and Bayesian-inspired evidence fusion mastery updates.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800/80 relative group hover:border-rose-500/40 transition duration-300">
            <div className="w-12 h-12 rounded-xl bg-rose-950/80 border border-rose-800/60 flex items-center justify-center text-rose-400 mb-4 group-hover:scale-105 transition-transform">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-2">6. Grounded RAG Assistant</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              pgvector similarity search with strict XML security delimiters and anti-hallucination source citation verification.
            </p>
          </div>
        </div>
      </section>

      {/* Trust & Deployment Summary */}
      <section className="border-t border-slate-800/80 bg-slate-900/50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <h4 className="text-2xl font-bold text-white mb-2">Production-Ready & Fully Deterministic</h4>
              <p className="text-sm text-slate-400 max-w-xl">
                Engineered with 162 backend unit/integration tests and complete fallback safety. Deploys seamlessly on Netlify + Render.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                Zero Hallucinations
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                Topological Kahn DAG
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                <Zap className="w-5 h-5 text-amber-400" />
                Adaptive Interventions
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
