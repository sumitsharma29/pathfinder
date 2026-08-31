import React, { useState, useEffect } from 'react';
import {
  User,
  Target,
  Clock,
  Sliders,
  Plus,
  Trash2,
  CheckCircle2,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { api } from '../api/client';
import { LearnerProfile, LearnerSkill, Role, Skill } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';
import { LoadingSpinner, ErrorMessage } from '../components/common/FeedbackStates';

export const ProfilePage: React.FC = () => {
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [learnerSkills, setLearnerSkills] = useState<LearnerSkill[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [availableSkills, setAvailableSkills] = useState<Skill[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form states
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [dailyHours, setDailyHours] = useState<number>(2.0);
  const [durationWeeks, setDurationWeeks] = useState<number>(24);

  // Add Skill Modal
  const [isAddSkillOpen, setIsAddSkillOpen] = useState<boolean>(false);
  const [newSkillId, setNewSkillId] = useState<string>('');
  const [newSkillProf, setNewSkillProf] = useState<number>(50);

  const fetchProfileData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [profData, skillsData, rolesList, catalogSkills] = await Promise.all([
        api.getProfile(),
        api.getLearnerSkills(),
        api.getRoles(),
        api.getSkills(),
      ]);
      setProfile(profData);
      setLearnerSkills(skillsData);
      setRoles(rolesList);
      setAvailableSkills(catalogSkills);

      if (profData.target_role) {
        setSelectedRoleId(profData.target_role.id);
      }
      if (profData.daily_study_hours) {
        setDailyHours(profData.daily_study_hours);
      }
      if (profData.target_duration_weeks) {
        setDurationWeeks(profData.target_duration_weeks);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileData();
  }, []);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    try {
      await api.updateProfile({
        target_role_id: selectedRoleId || undefined,
        daily_study_hours: dailyHours,
        target_duration_weeks: durationWeeks,
      });
      setSuccessMsg('Profile settings updated successfully!');
      setTimeout(() => setSuccessMsg(null), 3000);
      await fetchProfileData();
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillId) return;

    try {
      await api.addLearnerSkill(newSkillId, newSkillProf);
      setIsAddSkillOpen(false);
      setNewSkillId('');
      setNewSkillProf(50);
      await fetchProfileData();
    } catch (err: any) {
      alert(err.message || 'Failed to add skill');
    }
  };

  const handleUpdateProficiency = async (skillId: string, prof: number) => {
    try {
      await api.updateLearnerSkill(skillId, prof);
      setLearnerSkills((prev) =>
        prev.map((s) => (s.skill_id === skillId ? { ...s, proficiency: prof } : s))
      );
    } catch (err: any) {
      alert(err.message || 'Failed to update skill proficiency');
    }
  };

  const handleDeleteSkill = async (skillId: string) => {
    if (!confirm('Remove this skill from your profile?')) return;
    try {
      await api.deleteLearnerSkill(skillId);
      await fetchProfileData();
    } catch (err: any) {
      alert(err.message || 'Failed to remove skill');
    }
  };

  if (isLoading && !profile) {
    return <LoadingSpinner message="Loading learner profile..." size="lg" />;
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Learner Profile & Skill Inventory
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Manage your career targets, study availability, and self-reported proficiencies
        </p>
      </div>

      {error && <ErrorMessage title="Profile Error" message={error} />}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/50 text-emerald-300 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {successMsg}
        </div>
      )}

      {/* Target Role & Study Schedule Form */}
      <Card className="p-6">
        <form onSubmit={handleUpdateProfile} className="space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-400" />
            Career Target & Schedule
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Target Role
              </label>
              <select
                value={selectedRoleId}
                onChange={(e) => setSelectedRoleId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Daily Study Hours
              </label>
              <input
                type="number"
                min="0.5"
                max="12"
                step="0.5"
                value={dailyHours}
                onChange={(e) => setDailyHours(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Target Duration (Weeks)
              </label>
              <input
                type="number"
                min="2"
                max="52"
                value={durationWeeks}
                onChange={(e) => setDurationWeeks(parseInt(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button type="submit" size="sm">
              Save Preferences
            </Button>
          </div>
        </form>
      </Card>

      {/* Skill Inventory Manager */}
      <Card className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-purple-400" />
              Acquired Skills Inventory ({learnerSkills.length})
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Proficiencies are used to calculate gaps and unlock roadmap prerequisites.
            </p>
          </div>

          <Button size="sm" onClick={() => setIsAddSkillOpen(true)}>
            <Plus className="w-4 h-4 mr-1" /> Add Skill
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {learnerSkills.map((s) => (
            <div
              key={s.id}
              className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-3 hover:border-slate-700 transition"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">{s.skill_name}</h4>
                  <span className="text-[10px] text-slate-400 capitalize">{s.category} • Source: {s.source}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-emerald-400">{s.proficiency}%</span>
                  <button
                    onClick={() => handleDeleteSkill(s.skill_id)}
                    className="p-1 rounded text-slate-500 hover:text-rose-400 transition"
                    title="Remove skill"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <input
                type="range"
                min="0"
                max="100"
                value={s.proficiency}
                onChange={(e) => handleUpdateProficiency(s.skill_id, parseInt(e.target.value))}
                className="w-full accent-emerald-500 bg-slate-800 rounded-lg h-1.5 cursor-pointer"
              />
            </div>
          ))}
        </div>
      </Card>

      {/* Add Skill Modal */}
      <Modal
        isOpen={isAddSkillOpen}
        onClose={() => setIsAddSkillOpen(false)}
        title="Add Skill to Profile"
      >
        <form onSubmit={handleAddSkill} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Select Skill
            </label>
            <select
              required
              value={newSkillId}
              onChange={(e) => setNewSkillId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="">-- Choose a skill --</option>
              {availableSkills.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({s.category})
                </option>
              ))}
            </select>
          </div>

          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Proficiency Level</span>
              <span className="font-mono font-bold text-emerald-400">{newSkillProf}%</span>
            </div>
            <input
              type="range"
              min="1"
              max="100"
              value={newSkillProf}
              onChange={(e) => setNewSkillProf(parseInt(e.target.value))}
              className="w-full accent-emerald-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button variant="ghost" type="button" onClick={() => setIsAddSkillOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Add Skill</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
