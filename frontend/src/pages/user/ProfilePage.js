import React, { useState, useEffect } from 'react';
import { userAPI } from '../../lib/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { User, Trophy, Target, Award } from 'lucide-react';
import { toast } from 'sonner';
import { getInitials } from '../../lib/utils';
import { BadgeCard } from '../../components/BadgeCard';

export function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [badges, setBadges] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
    loadBadges();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await userAPI.getProfile();
      setProfile(res.data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadBadges = async () => {
    try {
      const res = await userAPI.getBadges();
      setBadges(res.data);
    } catch (error) {
      console.error('Failed to load badges:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (!profile) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-white rounded-xl p-8 border border-slate-200 text-center">
        <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center">
          <span className="text-3xl font-bold text-white">{getInitials(profile.user.nickname)}</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 mb-1 font-['Space_Grotesk']">{profile.user.nickname}</h1>
        <p className="text-sm text-slate-600">{profile.user.email}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200 text-center">
          <Trophy className="w-8 h-8 text-amber-500 mx-auto mb-2" />
          <p className="text-2xl font-bold text-slate-900 font-['Azeret_Mono']">{profile.stats.quizzes_played}</p>
          <p className="text-xs text-slate-600 mt-1">Quizzes Played</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200 text-center">
          <Target className="w-8 h-8 text-teal-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-slate-900 font-['Azeret_Mono']">{profile.stats.avg_correct}%</p>
          <p className="text-xs text-slate-600 mt-1">Avg Correct</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200 text-center">
          <Trophy className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
          <p className="text-2xl font-bold text-slate-900 font-['Azeret_Mono']">{profile.stats.personal_best}%</p>
          <p className="text-xs text-slate-600 mt-1">Personal Best</p>
        </div>
      </div>

      {/* Badges */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">Badges</h2>
          {badges && (
            <div className="text-sm text-slate-600">
              <span className="font-bold text-teal-600">{badges.total_earned}</span>
              <span className="mx-1">/</span>
              <span>{badges.total_available}</span>
            </div>
          )}
        </div>
        
        {!badges ? (
          <LoadingSpinner />
        ) : badges.earned.length === 0 ? (
          <div className="text-center py-12">
            <Award className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600 mb-2">No badges earned yet</p>
            <p className="text-sm text-slate-500">Complete quizzes to earn your first badge!</p>
          </div>
        ) : (
          <>
            {/* Earned Badges */}
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-slate-700 mb-4">Earned ({badges.earned.length})</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {badges.earned.map((badge) => (
                  <BadgeCard key={badge.id} badge={badge} size="sm" />
                ))}
              </div>
            </div>
            
            {/* Locked Badges */}
            {badges.available.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-4">Locked ({badges.available.length})</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {badges.available.slice(0, 6).map((badge) => (
                    <BadgeCard key={badge.id} badge={badge} locked size="sm" />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
