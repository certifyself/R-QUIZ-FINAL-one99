import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Trophy, Clock, Home, Eye, Lock } from 'lucide-react';
import { toast } from 'sonner';
import { formatTime } from '../../lib/utils';
import { useTranslation } from 'react-i18next';

export function ResultsPage() {
  const { quizIndex } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [result, setResult] = useState(location.state?.result);
  const [showAnswers, setShowAnswers] = useState(false);
  const [answers, setAnswers] = useState(null);
  const [locking, setLocking] = useState(false);
  const { t, i18n } = useTranslation();

  const canViewAnswers = result?.can_view_answers;  // Can view after any attempt now
  const canRetry = result?.attempts_remaining > 0 && !result?.quiz_locked;
  const isPerfect = result?.is_perfect || result?.score?.percentage === 100;
  const isLocked = result?.quiz_locked || result?.attempt_number >= 3;

  // Debug logging
  console.log('Results Debug:', {
    attempt_number: result?.attempt_number,
    can_view_answers: result?.can_view_answers,
    attempts_remaining: result?.attempts_remaining,
    is_perfect: isPerfect,
    quiz_locked: isLocked,
    canViewAnswers,
    canRetry
  });

  const handleViewAnswers = async () => {
    try {
      const currentLang = i18n.language.startsWith('sk') ? 'sk' : 'en';
      const res = await userAPI.getAnswers(quizIndex, currentLang);
      setAnswers(res.data.questions);
      setShowAnswers(true);
    } catch (error) {
      toast.error('Failed to load answers');
    }
  };

  const handleLockQuiz = async () => {
    // Quiz is already locked after 3rd attempt, just navigate away
    if (isLocked) {
      toast.info('Quiz is now locked. You cannot attempt it again.');
      setTimeout(() => navigate('/'), 1500);
      return;
    }
    
    // Manual lock (when viewing answers before 3 attempts)
    setLocking(true);
    try {
      await userAPI.lockQuiz(quizIndex);
      toast.success('Quiz locked. You can no longer attempt this quiz.');
      setTimeout(() => navigate('/'), 1500);
    } catch (error) {
      toast.error('Failed to lock quiz');
      setLocking(false);
    }
  };

  if (!result) {
    navigate('/');
    return null;
  }

  const percentage = result.score.percentage;
  const isExcellent = percentage >= 90;
  const isGood = percentage >= 70;
  const isFair = percentage >= 50;
  
  // Helper to get next quiz index
  const getNextQuizIndex = () => {
    const currentIndex = parseInt(quizIndex);
    if (currentIndex < 9) return currentIndex + 1;  // Next regular quiz
    if (currentIndex === 9) return 10;  // Go to bonus
    return null;  // No next quiz (already at bonus)
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Results Card */}
      <div className="bg-white rounded-2xl p-8 border border-slate-200 text-center">
        <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center">
          <Trophy className="w-12 h-12 text-white" />
        </div>

        <h1 className="text-3xl font-bold text-slate-900 mb-2 font-['Space_Grotesk']">Quiz Complete!</h1>
        <p className="text-slate-600 mb-8">Attempt {result.attempt_number} of 3</p>

        {/* Score */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-slate-50 rounded-xl p-6">
            <p className="text-sm text-slate-600 mb-2">Accuracy</p>
            <p className={`text-4xl font-bold font-['Azeret_Mono'] ${
              isExcellent ? 'text-emerald-600' : isGood ? 'text-teal-600' : isFair ? 'text-amber-600' : 'text-rose-600'
            }`}>
              {percentage.toFixed(0)}%
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {result.score.correct_count}/{result.score.total} correct
            </p>
          </div>

          <div className="bg-slate-50 rounded-xl p-6">
            <p className="text-sm text-slate-600 mb-2">Time</p>
            <p className="text-4xl font-bold text-slate-900 font-['Azeret_Mono']">
              {(result.score.total * 1000 / 1000).toFixed(0)}s
            </p>
          </div>
        </div>

        {/* Rank */}
        {result.rank && (
          <div className="bg-gradient-to-r from-teal-50 to-teal-100 rounded-xl p-4 mb-6">
            <p className="text-sm text-teal-700 mb-1">Current Rank</p>
            <p className="text-2xl font-bold text-teal-900 font-['Azeret_Mono']">#{result.rank}</p>
          </div>
        )}

        {/* Is Best */}
        {result.is_best && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-6">
            <p className="text-sm text-amber-800 font-medium">🎉 New Personal Best!</p>
          </div>
        )}

        {/* Feedback */}
        <div className="text-center mb-6">
          {isPerfect && result.attempt_number === 1 && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 mb-4">
              <p className="text-lg font-bold text-emerald-800 mb-2">🎉 Perfect Score!</p>
              <p className="text-sm text-emerald-700">
                Excellent! You scored 100%. Do you want to improve your time?
              </p>
            </div>
          )}
          {isExcellent && !isPerfect && <p className="text-emerald-600 font-medium">Excellent work! Outstanding performance!</p>}
          {isGood && !isExcellent && <p className="text-teal-600 font-medium">Great job! Well done!</p>}
          {isFair && !isGood && <p className="text-amber-600 font-medium">Good effort! Keep practicing!</p>}
          {!isFair && <p className="text-rose-600 font-medium">Nice try! Practice makes perfect!</p>}
        </div>

        {/* Actions */}
        <div className="space-y-3">
          {/* Perfect Score - Show both options */}
          {isPerfect && canRetry && (
            <>
              <Button
                onClick={() => navigate(`/quiz/${quizIndex}`)}
                className="w-full bg-gradient-to-r from-teal-500 to-teal-600"
                data-testid="improve-time-button"
              >
                ⚡ Improve Time ({result.attempts_remaining} attempts left)
              </Button>
              
              {getNextQuizIndex() !== null && (
                <Button
                  onClick={() => navigate(`/quiz/${getNextQuizIndex()}`)}
                  variant="outline"
                  className="w-full border-teal-500 text-teal-700 hover:bg-teal-50"
                  data-testid="next-quiz-button"
                >
                  Next Quiz →
                </Button>
              )}
            </>
          )}
          
          {/* Not Perfect - Show retry only */}
          {!isPerfect && canRetry && (
            <Button
              onClick={() => navigate(`/quiz/${quizIndex}`)}
              className="w-full bg-gradient-to-r from-teal-500 to-teal-600"
              data-testid="retry-button"
            >
              Try Again ({result.attempts_remaining} attempts left)
            </Button>
          )}

          {/* View Answers - Always available after submitting */}
          {canViewAnswers && !showAnswers && !isLocked && (
            <Button
              onClick={handleViewAnswers}
              variant="outline"
              className="w-full"
              data-testid="view-answers-button"
            >
              <Eye className="w-4 h-4 mr-2" />
              View Correct Answers (Optional)
            </Button>
          )}
          
          {/* After 3 attempts - Show answers and locked message */}
          {isLocked && !showAnswers && (
            <>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <p className="text-sm text-amber-800 font-medium">
                  🔒 All 3 attempts used. Quiz is now locked.
                </p>
              </div>
              <Button
                onClick={handleViewAnswers}
                className="w-full bg-gradient-to-r from-teal-500 to-teal-600"
                data-testid="view-answers-button"
              >
                <Eye className="w-4 h-4 mr-2" />
                View All Correct Answers
              </Button>
            </>
          )}

          <Button
            onClick={() => navigate('/')}
            variant="outline"
            className="w-full"
            data-testid="home-button"
          >
            <Home className="w-4 h-4 mr-2" />
            {t('results.back_to_quest')}
          </Button>
        </div>
      </div>

      {/* Answers Review */}
      {showAnswers && answers && (
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4 font-['Space_Grotesk']">Answer Review</h2>
          
          <div className="space-y-6">
            {answers.map((q, idx) => (
              <div key={q._id} className="border-b border-slate-200 pb-6 last:border-0">
                {/* Question Image (if available) */}
                {q.image_url && (
                  <div className="mb-4 rounded-lg overflow-hidden border border-slate-200">
                    <img 
                      src={q.image_url} 
                      alt="Question visual" 
                      className="w-full h-48 object-cover"
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  </div>
                )}
                
                <h3 className="font-medium text-slate-900 mb-3">
                  {idx + 1}. {q.text}
                </h3>
                
                <div className="space-y-2">
                  {q.options.map((opt) => {
                    const isCorrect = opt.key === q.correct_key;
                    const isUserAnswer = opt.key === q.user_answer;
                    
                    return (
                      <div
                        key={opt.key}
                        className={`p-3 rounded-lg border-2 ${
                          isCorrect
                            ? 'border-emerald-500 bg-emerald-50'
                            : isUserAnswer
                            ? 'border-rose-500 bg-rose-50'
                            : 'border-slate-200 bg-slate-50'
                        }`}
                      >
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold">{opt.key}.</span>
                          <span>{opt.label}</span>
                          {isCorrect && <span className="text-emerald-600 text-xs font-medium ml-auto">✓ Correct</span>}
                          {isUserAnswer && !isCorrect && <span className="text-rose-600 text-xs font-medium ml-auto">✗ Your answer</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Lock Info (only show if quiz is locked) */}
          {isLocked && (
            <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="text-sm text-amber-800">
                <Lock className="w-4 h-4 inline mr-1" />
                This quiz is now locked. You cannot attempt it again.
              </p>
            </div>
          )}
          
          {/* Manual lock warning (if viewing answers before 3 attempts) */}
          {!isLocked && showAnswers && (
            <div className="mt-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="text-sm text-amber-800 mb-3">
                <Lock className="w-4 h-4 inline mr-1" />
                After viewing answers, this quiz will be locked and you won't be able to attempt it again.
              </p>
              <Button
                onClick={handleLockQuiz}
                disabled={locking}
                variant="outline"
                className="w-full border-amber-300 text-amber-800 hover:bg-amber-100"
                data-testid="lock-quiz-button"
              >
                {locking ? 'Locking...' : 'I Understand, Lock Quiz'}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
