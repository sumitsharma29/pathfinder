import React from 'react';
import { Link } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Target,
  Layers,
  Bot,
  BrainCircuit,
  CheckCircle2
} from 'lucide-react';
import { Button } from '../components/common/Button';

export const LandingPage: React.FC = () => {
  return (
    <div className="relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-blue-500/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/80 text-emerald-400 text-xs font-semibold mb-8 animate-in fade-in slide-in-from-bottom-3 duration-500">
          <Sparkles className="w-3.5 h-3.5" />
          Autonomous Career Navigation Engine
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-[1.1] mb-6">
          Turn your career ambitions into an{' '}
          <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
            adaptive roadmap.
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          PathFinder AI analyzes your current skills, pinpoints critical gaps, and constructs topologically-ordered learning paths that continuously adapt with every assessment you take.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-16">
          <Link to="/register" className="w-full sm:w-auto">
            <Button size="lg" className="w-full sm:w-auto shadow-xl shadow-emerald-500/25">
              Start Free Assessment <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
          <Link to="/login" className="w-full sm:w-auto">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Sign In to Account
            </Button>
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto text-left">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 relative group hover:border-emerald-500/40 transition">
            <div className="w-12 h-12 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 mb-4">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">AI Goal Grounding</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Describe your target career in natural language. Our AI grounds your intent against validated industry role catalogs.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 relative group hover:border-emerald-500/40 transition">
            <div className="w-12 h-12 rounded-xl bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400 mb-4">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Dependency-Aware Roadmaps</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Strict prerequisite graphs ensure foundational concepts are mastered before advancing to complex milestones.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 relative group hover:border-emerald-500/40 transition">
            <div className="w-12 h-12 rounded-xl bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400 mb-4">
              <Zap className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white mb-2">Adaptive Feedback Loop</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Real-time server-side scored assessments adjust recommendations, unlock downstream milestones, and schedule interventions.
            </p>
          </div>
        </div>
      </section>

      {/* Trust & Guarantee Banner */}
      <section className="border-t border-slate-800/80 bg-slate-900/40 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div>
              <h4 className="text-2xl font-bold text-white mb-2">Grounded AI. No Hallucinations.</h4>
              <p className="text-sm text-slate-400 max-w-xl">
                Every learning recommendation is sourced from authentic curated resources. Assistant answers are validated against direct database citations.
              </p>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Deterministic Scoring</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Server-Side Grading</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
