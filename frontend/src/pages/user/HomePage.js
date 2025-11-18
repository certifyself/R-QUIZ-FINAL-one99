import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Lock, CheckCircle2, Play, Trophy } from 'lucide-react';
import { toast } from 'sonner';

export function HomePage() {
  const [pack, setPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadTodayPack();
  }, []);

  const loadTodayPack = async () => {
    try {
      const res = await userAPI.getTodayPack();
      setPack(res.data);
    } catch (error) {
      toast.error('Failed to load today\'s quizzes');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (!pack) {
    return (
      <div className="text-center py-20">
        <p className="text-slate-600">No quizzes available today</p>
      </div>
    );
  }

  const getStatusIcon = (quiz) => {
    if (quiz.is_locked) return <Lock className="w-5 h-5 text-slate-500" />;
    if (quiz.status === 'completed') return <CheckCircle2 className="w-5 h-5 text-teal-600" />;
    if (quiz.status === 'in_progress') return <Play className="w-5 h-5 text-amber-500" />;
    return <Play className="w-5 h-5 text-slate-400" />;
  };

  const getStatusColor = (quiz) => {
    if (quiz.is_locked) return 'border-slate-300 bg-slate-50';
    if (quiz.status === 'completed') return 'border-teal-300 bg-teal-50';
    if (quiz.status === 'in_progress') return 'border-amber-300 bg-amber-50';
    return 'border-slate-300 bg-white hover:border-teal-400 hover:shadow-md cursor-pointer';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-500 rounded-2xl p-8 text-white">
        <h1 className="text-3xl md:text-4xl font-bold mb-2 font-['Space_Grotesk']">Today's Quest</h1>
        <p className="text-teal-100">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>

      {/* Progress Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm text-slate-600 mb-1">Completed</p>
          <p className="text-3xl font-bold text-teal-600 font-['Azeret_Mono']">
            {pack.quizzes.filter(q => q.attempt_count > 0).length}/10
          </p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm text-slate-600 mb-1">Best Score</p>
          <p className="text-3xl font-bold text-slate-900 font-['Azeret_Mono']">
            {Math.max(...pack.quizzes.map(q => q.best_score?.percentage || 0).concat(0)).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Regular Quizzes */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4 font-['Space_Grotesk']">Regular Quizzes</h2>
        <div className="grid gap-4">
          {pack.quizzes.map((quiz) => (
            <div
              key={quiz.index}
              onClick={() => !quiz.is_locked && quiz.attempt_count < 3 && navigate(`/quiz/${quiz.index}`)}
              className={`border-2 rounded-xl p-4 transition-all ${getStatusColor(quiz)}`}
              data-testid={`quiz-card-${quiz.index}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(quiz)}
                    <h3 className="font-semibold text-slate-900 font-['Space_Grotesk']">Quiz {quiz.index + 1}</h3>
                  </div>
                  <p className="text-sm text-slate-600 mb-2">{quiz.topic?.name}</p>
                  
                  {quiz.best_score && (
                    <div className="flex items-center space-x-4 text-xs text-slate-600">
                      <span>Best: {quiz.best_score.percentage.toFixed(0)}%</span>
                      <span>Time: {(quiz.best_score.time_ms / 1000).toFixed(0)}s</span>
                    </div>
                  )}
                </div>
                
                <div className="text-right">
                  {quiz.is_locked ? (
                    <span className="text-xs text-slate-500">Locked</span>
                  ) : quiz.attempt_count >= 3 ? (
                    <span className="text-xs text-slate-600">3/3 attempts</span>
                  ) : (
                    <span className="text-xs text-slate-600">{quiz.attempt_count}/3 attempts</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bonus Quiz */}
      {pack.bonus_quiz && (
        <div>
          <h2 className="text-xl font-bold text-slate-900 mb-4 font-['Space_Grotesk'] flex items-center space-x-2">
            <Trophy className="w-6 h-6 text-amber-500" />
            <span>Bonus Quiz</span>
          </h2>
          
          <div
            onClick={() => pack.bonus_quiz.unlocked && !pack.bonus_quiz.is_locked && pack.bonus_quiz.attempt_count < 3 && navigate('/quiz/10')}
            className={`border-2 rounded-xl p-6 transition-all ${
              pack.bonus_quiz.unlocked
                ? pack.bonus_quiz.is_locked
                  ? 'border-slate-300 bg-slate-50'
                  : pack.bonus_quiz.status === 'completed'
                  ? 'border-amber-300 bg-amber-50'
                  : 'border-amber-400 bg-gradient-to-br from-amber-50 to-amber-100 hover:shadow-lg cursor-pointer'
                : 'border-slate-300 bg-slate-100'
            }`}
            data-testid="bonus-quiz-card"
          >
            {pack.bonus_quiz.unlocked ? (
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Trophy className="w-6 h-6 text-amber-500" />
                  <h3 className="font-semibold text-slate-900 font-['Space_Grotesk'] text-lg">Bonus Challenge</h3>
                </div>
                <p className="text-sm text-slate-600 mb-2">{pack.bonus_quiz.topic?.name}</p>
                
                {pack.bonus_quiz.best_score && (
                  <div className="flex items-center space-x-4 text-xs text-slate-600">
                    <span>Best: {pack.bonus_quiz.best_score.percentage.toFixed(0)}%</span>
                    <span>Time: {(pack.bonus_quiz.best_score.time_ms / 1000).toFixed(0)}s</span>
                  </div>
                )}
                
                {pack.bonus_quiz.is_locked ? (
                  <span className="text-xs text-slate-500 mt-2 block">Locked after viewing answers</span>
                ) : pack.bonus_quiz.attempt_count >= 3 ? (
                  <span className="text-xs text-slate-600 mt-2 block">3/3 attempts used</span>
                ) : (
                  <span className="text-xs text-slate-600 mt-2 block">{pack.bonus_quiz.attempt_count}/3 attempts</span>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <Lock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-sm text-slate-600 font-medium">Complete all 10 regular quizzes to unlock</p>
                <p className="text-xs text-slate-500 mt-1">{pack.quizzes.filter(q => q.attempt_count > 0).length}/10 completed</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
