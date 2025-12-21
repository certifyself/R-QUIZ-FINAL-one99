import React, { useState, useEffect } from 'react';
import { userAPI } from '../../lib/api';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Trophy, Crown, Calendar, Target } from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

export function RankingsPage() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [viewMode, setViewMode] = useState('daily'); // 'daily' or 'quiz'
  const [quizIndex, setQuizIndex] = useState(0);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, [viewMode, quizIndex]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      if (viewMode === 'daily') {
        const res = await userAPI.getDailyLeaderboard();
        setLeaderboard(res.data.leaderboard || []);
      } else {
        const res = await userAPI.getLeaderboard(quizIndex);
        setLeaderboard(res.data.leaderboard || []);
      }
    } catch (error) {
      toast.error('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-slate-900 font-['Space_Grotesk']">{t('rankings.title')}</h1>

      {/* View Mode Toggle */}
      <div className="bg-white rounded-xl p-4 border border-slate-200">
        <div className="flex space-x-2 mb-4">
          <button
            onClick={() => setViewMode('daily')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
              viewMode === 'daily'
                ? 'bg-gradient-to-r from-teal-500 to-teal-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
            data-testid="daily-ranking-btn"
          >
            <Calendar className="w-5 h-5" />
            <span>{t('rankings.daily_challenge') || 'Daily Challenge'}</span>
          </button>
          <button
            onClick={() => setViewMode('quiz')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg font-medium transition-colors ${
              viewMode === 'quiz'
                ? 'bg-gradient-to-r from-teal-500 to-teal-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
            data-testid="quiz-ranking-btn"
          >
            <Target className="w-5 h-5" />
            <span>{t('rankings.per_quiz') || 'Per Quiz'}</span>
          </button>
        </div>

        {/* Quiz Selector - only show when in quiz mode */}
        {viewMode === 'quiz' && (
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">{t('rankings.select_quiz')}</label>
            <select
              value={quizIndex}
              onChange={(e) => setQuizIndex(parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
              data-testid="quiz-selector"
            >
              {[...Array(10)].map((_, i) => (
                <option key={i} value={i}>{t('home.quiz') || 'Quiz'} {i + 1}</option>
              ))}
              <option value={10}>{t('home.bonus_challenge') || 'Bonus Challenge'}</option>
            </select>
          </div>
        )}
      </div>

      {/* Leaderboard */}
      {loading ? (
        <LoadingSpinner className="py-20" />
      ) : leaderboard.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center">
          <Trophy className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-600">{t('rankings.no_rankings')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="divide-y divide-slate-200">
            {leaderboard.map((entry) => {
              const isCurrentUser = entry.user_id === user._id;
              const isTop3 = entry.rank <= 3;
              
              return (
                <div
                  key={entry.user_id}
                  className={`p-4 flex items-center space-x-4 ${
                    isCurrentUser ? 'bg-teal-50 border-l-4 border-teal-600' : ''
                  }`}
                  data-testid={`leaderboard-entry-${entry.rank}`}
                >
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold ${
                    entry.rank === 1 ? 'bg-amber-100 text-amber-700' :
                    entry.rank === 2 ? 'bg-slate-200 text-slate-700' :
                    entry.rank === 3 ? 'bg-amber-50 text-amber-600' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {isTop3 ? <Crown className="w-6 h-6" /> : entry.rank}
                  </div>
                  
                  <div className="flex-1">
                    <p className={`font-semibold ${
                      isCurrentUser ? 'text-teal-900' : 'text-slate-900'
                    }`}>
                      {entry.nickname} {isCurrentUser && `(${t('rankings.you')})`}
                    </p>
                    <p className="text-sm text-slate-600">
                      {viewMode === 'daily' ? (
                        <>
                          {entry.quizzes_completed} {t('rankings.quizzes') || 'quizzes'} • {(entry.avg_percentage || 0).toFixed(1)}% {t('rankings.avg') || 'avg'}
                        </>
                      ) : (
                        <>
                          {(entry.percentage || 0).toFixed(1)}% • {((entry.time_ms || 0) / 1000).toFixed(0)}s
                        </>
                      )}
                    </p>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-2xl font-bold text-slate-900 font-['Azeret_Mono']">#{entry.rank}</p>
                    {viewMode === 'daily' && (
                      <p className="text-xs text-slate-500">
                        {Math.floor(entry.total_time_ms / 60000)}m {Math.floor((entry.total_time_ms % 60000) / 1000)}s
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
