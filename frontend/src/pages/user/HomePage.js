import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { Lock, CheckCircle2, Play, Trophy, Sparkles, Clock } from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

export function HomePage() {
  const [pack, setPack] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t } = useTranslation();

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
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden bg-gradient-to-br from-teal-600 via-teal-500 to-cyan-500 rounded-3xl p-8 text-white shadow-2xl"
      >
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjA1IiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />
        <div className="relative z-10">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
            className="flex items-center space-x-2 mb-3"
          >
            <Sparkles className="w-6 h-6 text-amber-300" />
            <span className="text-teal-100 text-sm font-semibold uppercase tracking-wider">{t('home.daily_challenge')}</span>
          </motion.div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3 font-['Space_Grotesk'] drop-shadow-lg">{t('home.todays_quest')}</h1>
          <div className="flex items-center space-x-2 text-teal-100">
            <Clock className="w-5 h-5" />
            <p>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
          </div>
        </div>
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ 
            duration: 20,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"
        />
      </motion.div>

      {/* Progress Stats */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-2 gap-4"
      >
        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow"
        >
          <p className="text-sm text-slate-600 mb-1 font-medium">{t('home.completed')}</p>
          <p className="text-4xl font-bold bg-gradient-to-r from-teal-600 to-teal-500 bg-clip-text text-transparent font-['Azeret_Mono']">
            {pack.quizzes.filter(q => q.attempt_count > 0).length}/10
          </p>
          <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${(pack.quizzes.filter(q => q.attempt_count > 0).length / 10) * 100}%` }}
              transition={{ duration: 1, delay: 0.5 }}
              className="bg-gradient-to-r from-teal-500 to-cyan-500 h-2 rounded-full"
            />
          </div>
        </motion.div>
        <motion.div 
          whileHover={{ scale: 1.05, y: -5 }}
          className="bg-white rounded-2xl p-6 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow"
        >
          <p className="text-sm text-slate-600 mb-1 font-medium">{t('home.best_score')}</p>
          <p className="text-4xl font-bold bg-gradient-to-r from-amber-600 to-amber-500 bg-clip-text text-transparent font-['Azeret_Mono']">
            {Math.max(...pack.quizzes.map(q => q.best_score?.percentage || 0).concat(0)).toFixed(0)}%
          </p>
          <div className="flex items-center space-x-1 mt-2 text-amber-600">
            {[...Array(3)].map((_, i) => (
              <Trophy key={i} className="w-4 h-4" fill="currentColor" />
            ))}
          </div>
        </motion.div>
      </motion.div>

      {/* Regular Quizzes */}
      <div>
        <motion.h2 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-slate-900 mb-6 font-['Space_Grotesk'] flex items-center space-x-2"
        >
          <div className="w-1 h-8 bg-gradient-to-b from-teal-500 to-teal-600 rounded-full" />
          <span>{t('home.regular_quizzes')}</span>
        </motion.h2>
        <div className="grid gap-4">
          <AnimatePresence>
            {pack.quizzes.map((quiz, index) => (
              <motion.div
                key={quiz.index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + (index * 0.05) }}
                whileHover={{ scale: 1.02, x: 8 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => !quiz.is_locked && quiz.attempt_count < 3 && navigate(`/quiz/${quiz.index}`)}
                className={`group relative border-2 rounded-2xl p-5 transition-all cursor-pointer overflow-hidden ${getStatusColor(quiz)}`}
                data-testid={`quiz-card-${quiz.index}`}
              >
                {/* Background Glow Effect */}
                <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity ${
                  quiz.is_locked ? '' : 'bg-gradient-to-r from-teal-500/10 to-transparent'
                }`} />
                
                <div className="relative flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.5 }}
                      >
                        {getStatusIcon(quiz)}
                      </motion.div>
                      <div>
                        <h3 className="font-bold text-slate-900 font-['Space_Grotesk'] text-lg">{t('home.quiz')} {quiz.index + 1}</h3>
                        <p className="text-sm text-slate-600 font-medium">{quiz.topic?.name}</p>
                      </div>
                    </div>
                    
                    {quiz.best_score && (
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="px-3 py-1 bg-teal-100 text-teal-700 rounded-full font-semibold">
                          Best: {quiz.best_score.percentage.toFixed(0)}%
                        </span>
                        <span className="text-slate-600 font-mono">
                          {(quiz.best_score.time_ms / 1000).toFixed(0)}s
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="text-right">
                    {quiz.is_locked ? (
                      <div className="px-3 py-2 bg-slate-100 rounded-lg">
                        <Lock className="w-5 h-5 text-slate-500 mx-auto mb-1" />
                        <span className="text-xs text-slate-500 font-medium block">Locked</span>
                      </div>
                    ) : quiz.attempt_count >= 3 ? (
                      <div className="px-3 py-2 bg-amber-50 rounded-lg border border-amber-200">
                        <span className="text-sm font-bold text-amber-700 block">3/3</span>
                        <span className="text-xs text-amber-600">attempts</span>
                      </div>
                    ) : (
                      <div className="px-3 py-2 bg-teal-50 rounded-lg border border-teal-200">
                        <span className="text-sm font-bold text-teal-700 block">{quiz.attempt_count}/3</span>
                        <span className="text-xs text-teal-600">attempts</span>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Bonus Quiz */}
      {pack.bonus_quiz && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <motion.h2 
            className="text-2xl font-bold text-slate-900 mb-6 font-['Space_Grotesk'] flex items-center space-x-2"
          >
            <div className="w-1 h-8 bg-gradient-to-b from-amber-500 to-amber-600 rounded-full" />
            <Trophy className="w-7 h-7 text-amber-500" />
            <span>Bonus Challenge</span>
          </motion.h2>
          
          <motion.div
            whileHover={pack.bonus_quiz.unlocked && !pack.bonus_quiz.is_locked && pack.bonus_quiz.attempt_count < 3 ? { scale: 1.02, y: -5 } : {}}
            whileTap={pack.bonus_quiz.unlocked && !pack.bonus_quiz.is_locked && pack.bonus_quiz.attempt_count < 3 ? { scale: 0.98 } : {}}
            onClick={() => pack.bonus_quiz.unlocked && !pack.bonus_quiz.is_locked && pack.bonus_quiz.attempt_count < 3 && navigate('/quiz/10')}
            className={`relative overflow-hidden border-3 rounded-3xl p-8 transition-all ${
              pack.bonus_quiz.unlocked
                ? pack.bonus_quiz.is_locked
                  ? 'border-slate-300 bg-slate-50'
                  : pack.bonus_quiz.status === 'completed'
                  ? 'border-amber-300 bg-gradient-to-br from-amber-50 via-white to-amber-50 shadow-xl shadow-amber-500/20 cursor-pointer'
                  : 'border-amber-400 bg-gradient-to-br from-amber-50 via-yellow-50 to-amber-100 shadow-2xl shadow-amber-500/30 cursor-pointer hover:shadow-amber-500/40'
                : 'border-slate-300 bg-slate-100'
            }`}
            data-testid="bonus-quiz-card"
          >
            {/* Animated Background */}
            {pack.bonus_quiz.unlocked && !pack.bonus_quiz.is_locked && (
              <>
                <motion.div
                  animate={{ 
                    scale: [1, 1.5, 1],
                    opacity: [0.3, 0.6, 0.3]
                  }}
                  transition={{ 
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="absolute -top-10 -right-10 w-40 h-40 bg-amber-400/20 rounded-full blur-3xl"
                />
                <motion.div
                  animate={{ 
                    scale: [1, 1.3, 1],
                    opacity: [0.2, 0.5, 0.2]
                  }}
                  transition={{ 
                    duration: 5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1
                  }}
                  className="absolute -bottom-10 -left-10 w-40 h-40 bg-yellow-400/20 rounded-full blur-3xl"
                />
              </>
            )}
            
            <div className="relative z-10">
              {pack.bonus_quiz.unlocked ? (
                <div>
                  <div className="flex items-center space-x-3 mb-4">
                    <motion.div
                      animate={{ 
                        rotate: [0, 10, -10, 0],
                        scale: [1, 1.1, 1]
                      }}
                      transition={{ 
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    >
                      <Trophy className="w-10 h-10 text-amber-500" fill="currentColor" />
                    </motion.div>
                    <div>
                      <h3 className="font-bold text-slate-900 font-['Space_Grotesk'] text-2xl">Bonus Challenge</h3>
                      <p className="text-sm text-amber-700 font-semibold">{pack.bonus_quiz.topic?.name}</p>
                    </div>
                  </div>
                  
                  {pack.bonus_quiz.best_score && (
                    <div className="flex items-center space-x-4 text-sm mb-4">
                      <span className="px-4 py-2 bg-amber-200 text-amber-900 rounded-full font-bold shadow-sm">
                        Best: {pack.bonus_quiz.best_score.percentage.toFixed(0)}%
                      </span>
                      <span className="text-slate-700 font-mono font-semibold">
                        {(pack.bonus_quiz.best_score.time_ms / 1000).toFixed(0)}s
                      </span>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between">
                    {pack.bonus_quiz.is_locked ? (
                      <div className="flex items-center space-x-2 text-slate-600">
                        <Lock className="w-5 h-5" />
                        <span className="text-sm font-medium">Locked after viewing answers</span>
                      </div>
                    ) : pack.bonus_quiz.attempt_count >= 3 ? (
                      <div className="px-4 py-2 bg-amber-100 rounded-lg border border-amber-300">
                        <span className="text-sm font-bold text-amber-800">3/3 attempts used</span>
                      </div>
                    ) : (
                      <div className="px-4 py-2 bg-white rounded-lg border-2 border-amber-400 shadow-sm">
                        <span className="text-sm font-bold text-amber-700">{pack.bonus_quiz.attempt_count}/3 attempts</span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <motion.div
                    animate={{ 
                      rotate: [0, 5, -5, 0]
                    }}
                    transition={{ 
                      duration: 3,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    <Lock className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                  </motion.div>
                  <p className="text-lg text-slate-700 font-semibold mb-2">Complete all 10 quizzes to unlock</p>
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-full max-w-xs bg-slate-200 rounded-full h-3">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(pack.quizzes.filter(q => q.attempt_count > 0).length / 10) * 100}%` }}
                        transition={{ duration: 1 }}
                        className="bg-gradient-to-r from-teal-500 to-cyan-500 h-3 rounded-full"
                      />
                    </div>
                    <span className="text-sm font-bold text-slate-600">{pack.quizzes.filter(q => q.attempt_count > 0).length}/10</span>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
