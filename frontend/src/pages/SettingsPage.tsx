import React, { useState, useEffect } from 'react';
import {
  Settings,
  User,
  Bell,
  Lock,
  CheckCircle2,
  Shield,
  Save,
  Mail
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { LearnerProfile } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner, ErrorMessage } from '../components/common/FeedbackStates';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Notification Preferences State (stored in learning_preferences)
  const [emailDigest, setEmailDigest] = useState<boolean>(true);
  const [roadmapAlerts, setRoadmapAlerts] = useState<boolean>(true);
  const [assessmentReminders, setAssessmentReminders] = useState<boolean>(true);

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        const prof = await api.getProfile();
        setProfile(prof);
        const prefs = prof.learning_preferences || {};
        if (prefs.email_digest !== undefined) setEmailDigest(!!prefs.email_digest);
        if (prefs.roadmap_alerts !== undefined) setRoadmapAlerts(!!prefs.roadmap_alerts);
        if (prefs.assessment_reminders !== undefined) setAssessmentReminders(!!prefs.assessment_reminders);
      } catch (err: any) {
        setError(err.message || 'Failed to load user settings');
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSaveNotifications = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const updatedPrefs = {
        ...(profile?.learning_preferences || {}),
        email_digest: emailDigest,
        roadmap_alerts: roadmapAlerts,
        assessment_reminders: assessmentReminders,
      };

      await api.updateProfile({
        learning_preferences: updatedPrefs,
      });

      setSuccessMsg('Notification preferences updated successfully!');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to update preferences');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading account settings..." size="lg" />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300 max-w-4xl">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Account & System Settings
          </h1>
          <Badge variant="default" size="sm">
            Configuration
          </Badge>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Manage your account credentials, notifications, and application preferences
        </p>
      </div>

      {error && <ErrorMessage title="Settings Error" message={error} />}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {successMsg}
        </div>
      )}

      {/* 1. Account Details */}
      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <User className="w-5 h-5 text-emerald-400" />
          Account Profile Details
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Full Name</span>
            <p className="text-sm font-bold text-white">{user?.name || 'Learner'}</p>
          </div>

          <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Email Address</span>
            <p className="text-sm font-bold text-white">{user?.email || 'learner@example.com'}</p>
          </div>

          <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-1 sm:col-span-2">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Learner ID</span>
            <p className="text-xs font-mono text-slate-300">{user?.id || profile?.user_id}</p>
          </div>
        </div>
      </Card>

      {/* 2. Notification Preferences */}
      <Card className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-400" />
            Notification & Telemetry Alerts
          </h3>
          <span className="text-xs text-slate-400">Stored in learner preferences</span>
        </div>

        <form onSubmit={handleSaveNotifications} className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-white">Daily Study Digest</h4>
              <p className="text-xs text-slate-400">Receive daily reminders to stay consistent with your target study hours.</p>
            </div>
            <input
              type="checkbox"
              checked={emailDigest}
              onChange={(e) => setEmailDigest(e.target.checked)}
              className="w-4 h-4 accent-emerald-500 rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-white">Roadmap Recalculation Alerts</h4>
              <p className="text-xs text-slate-400">Get notified when adaptive evaluations update downstream roadmap items.</p>
            </div>
            <input
              type="checkbox"
              checked={roadmapAlerts}
              onChange={(e) => setRoadmapAlerts(e.target.checked)}
              className="w-4 h-4 accent-emerald-500 rounded cursor-pointer"
            />
          </div>

          <div className="flex items-center justify-between p-4 bg-slate-900 rounded-xl border border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-white">Assessment Verification Reminders</h4>
              <p className="text-xs text-slate-400">Prompt for periodic skill tests to reinforce acquired proficiencies.</p>
            </div>
            <input
              type="checkbox"
              checked={assessmentReminders}
              onChange={(e) => setAssessmentReminders(e.target.checked)}
              className="w-4 h-4 accent-emerald-500 rounded cursor-pointer"
            />
          </div>

          <div className="flex justify-end pt-2">
            <Button type="submit" isLoading={isSaving} size="sm">
              <Save className="w-4 h-4 mr-1.5" /> Save Notification Preferences
            </Button>
          </div>
        </form>
      </Card>

      {/* 3. Security & Password Update */}
      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Lock className="w-5 h-5 text-purple-400" />
          Security & Password Management
        </h3>

        <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-2">
          <div className="flex items-center gap-2 font-semibold text-white">
            <Shield className="w-4 h-4 text-emerald-400" />
            Argon2id Hash Protection
          </div>
          <p className="text-slate-400 leading-relaxed">
            Your credentials are protected using memory-hard Argon2id cryptographic hashing with rate-limited authentication endpoints.
          </p>
          <p className="text-slate-400">
            Direct in-app password update endpoints are not enabled on this backend release. To request an account reset, please contact system administration.
          </p>
        </div>
      </Card>
    </div>
  );
};
