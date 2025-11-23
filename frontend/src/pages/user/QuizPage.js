import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { userAPI } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { BannerAdPlaceholder } from '../../components/BannerAdPlaceholder';
import { RewardedGate } from '../../components/RewardedGate';
import { Clock, CheckCircle, XCircle, ArrowLeft, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';
import { formatTime } from '../../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

export function QuizPage() {
  const { quizIndex } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [showAdGate, setShowAdGate] = useState(false);
  const [adShown, setAdShown] = useState(false);
  const [questionTimer, setQuestionTimer] = useState(30); // 30 seconds per question
  const QUESTION_TIME_LIMIT = 30; // seconds

  useEffect(() => {
    loadQuiz();
  }, [quizIndex]);

  useEffect(() => {
    if (startTime) {
      const timer = setInterval(() => {
        setElapsedTime(Date.now() - startTime);
      }, 100);
      return () => clearInterval(timer);
    }
  }, [startTime]);

  // Question timer - 12 seconds per question
  useEffect(() => {
    if (!quiz) return;
    
    // Reset timer when question changes
    setQuestionTimer(QUESTION_TIME_LIMIT);
    
    const timer = setInterval(() => {
      setQuestionTimer((prev) => {
        if (prev <= 1) {
          // Time's up - auto advance to next question
          clearInterval(timer);
          handleTimeExpired();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(timer);
  }, [currentQuestion, quiz]);

  const loadQuiz = async () => {
    try {
      // Ensure language is 'en' or 'sk' only
      const currentLang = i18n.language.startsWith('sk') ? 'sk' : 'en';
      const res = await userAPI.getQuiz(quizIndex, currentLang);
      setQuiz(res.data);
      setStartTime(Date.now());
      
      // Show ad gate if attempt 2 or 3
      if (res.data.attempt_number >= 2 && !adShown) {
        setShowAdGate(true);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load quiz');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, optionKey) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: optionKey
    }));
    
    // Auto-advance to next question after answering
    setTimeout(() => {
      if (currentQuestion < quiz.questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
      } else {
        // Last question - auto submit
        handleSubmit();
      }
    }, 500); // Small delay for animation
  };

  const handleTimeExpired = () => {
    // Time expired - move to next question or submit
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      toast.warning('Time expired! Moving to next question.');
    } else {
      // Last question - auto submit
      toast.warning('Time expired! Auto-submitting quiz.');
      handleSubmit();
    }
  };

  const handleNext = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    const timeMs = Date.now() - startTime;

    setSubmitting(true);
    try {
      const res = await userAPI.submitQuiz(quizIndex, {
        answers: quiz.questions.map(q => ({
          question_id: q._id,
          choice_key: answers[q._id] || 'UNANSWERED' // Mark as unanswered if no answer
        })),
        time_ms: timeMs
      });
      
      toast.success('Quiz submitted successfully!');
      navigate(`/results/${quizIndex}`, { state: { result: res.data } });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner className="py-20" />;
  }

  if (!quiz) {
    return null;
  }

  const currentQ = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  // Show ad gate
  if (showAdGate) {
    return (
      <RewardedGate
        seconds={15}
        onFinish={() => {
          setShowAdGate(false);
          setAdShown(true);
        }}
      />
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          onClick={() => navigate('/')}
          variant="ghost"
          size="sm"
          data-testid="back-button"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('quiz.back')}
        </Button>
        
        <div className="flex items-center space-x-2 bg-white px-3 py-1 rounded-lg border border-slate-200">
          <Clock className="w-4 h-4 text-teal-600" />
          <span className="font-mono font-semibold text-teal-600 text-sm">{formatTime(elapsedTime)}</span>
        </div>
      </div>

      {/* Quiz Info - Compact */}
      <div className="bg-white rounded-xl p-4 border border-slate-200">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">
              {quizIndex === '10' ? t('quiz.bonus_quiz') : `Quiz ${parseInt(quizIndex) + 1}`}
            </h1>
            <p className="text-xs text-slate-600">{quiz.topic_count} topics • {quiz.total_questions} questions</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-600">{t('quiz.attempt')} {quiz.attempt_number}/3</p>
          </div>
        </div>

        {/* Question Timer - 30 seconds */}
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-medium text-slate-700">Timer</span>
            <span className={`text-xl font-bold font-['Azeret_Mono'] ${
              questionTimer <= 5 ? 'text-rose-600' : 'text-teal-600'
            }`}>
              {questionTimer}s
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 ${
                questionTimer <= 5 ? 'bg-rose-500' : 'bg-gradient-to-r from-teal-500 to-teal-600'
              }`}
              style={{ width: `${(questionTimer / QUESTION_TIME_LIMIT) * 100}%` }}
            />
          </div>
        </div>

        {/* Progress Bar - Compact */}
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-teal-500 to-teal-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-slate-600 mt-1 text-center">
          {t('quiz.question')} {currentQuestion + 1} {t('quiz.of')} {quiz.questions.length}
        </p>
      </div>

      {/* Question Card - Compact */}
      <motion.div 
        key={currentQuestion}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        className="bg-white rounded-xl p-5 border border-slate-200 shadow-lg"
      >
        {/* Current Topic Badge */}
        <div className="mb-3">
          <span className="px-3 py-1 bg-teal-100 text-teal-900 rounded-full text-xs font-bold">
            Topic {currentQ.topic_index + 1}: {currentQ.topic_name}
          </span>
        </div>
        
        {/* Question Image (if available) */}
        {currentQ.image_url && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-3 rounded-lg overflow-hidden border border-slate-200"
          >
            <img 
              src={currentQ.image_url} 
              alt="Question visual" 
              className="w-full h-48 object-cover"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          </motion.div>
        )}
        
        <motion.h2 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-lg font-medium text-slate-900 mb-4 font-['Space_Grotesk'] leading-relaxed"
        >
          {currentQ.text}
        </motion.h2>

        <div className="space-y-2">
          <AnimatePresence mode="wait">
            {currentQ.options.map((option, idx) => (
              <motion.button
                key={option.key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ scale: 1.02, x: 5 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleAnswer(currentQ._id, option.key)}
                className={`w-full text-left p-3 rounded-lg border-2 transition-all shadow-sm hover:shadow-md ${
                  answers[currentQ._id] === option.key
                    ? 'border-teal-500 bg-gradient-to-r from-teal-50 to-cyan-50 shadow-lg shadow-teal-500/20'
                    : 'border-slate-200 bg-white hover:border-teal-300'
                }`}
                data-testid={`option-${option.key}`}
              >
                <div className="flex items-center space-x-3">
                  <motion.div 
                    animate={answers[currentQ._id] === option.key ? {
                      scale: [1, 1.2, 1],
                      rotate: [0, 360]
                    } : {}}
                    transition={{ duration: 0.5 }}
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-base ${
                      answers[currentQ._id] === option.key
                        ? 'bg-gradient-to-br from-teal-600 to-cyan-600 text-white shadow-lg'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {option.key}
                  </motion.div>
                  <span className="text-slate-700 text-sm font-medium">{option.label}</span>
                </div>
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Button
            onClick={handlePrevious}
            variant="outline"
            disabled={currentQuestion === 0}
            className="px-6"
            data-testid="previous-button"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('quiz.previous')}
          </Button>
        </motion.div>

        {currentQuestion === quiz.questions.length - 1 ? (
          <motion.div 
            whileHover={{ scale: 1.05 }} 
            whileTap={{ scale: 0.95 }}
            animate={quiz.questions.every(q => answers[q._id]) ? {
              boxShadow: [
                '0 0 0 0 rgba(8, 131, 149, 0.4)',
                '0 0 0 10px rgba(8, 131, 149, 0)',
              ]
            } : {}}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <Button
              onClick={handleSubmit}
              disabled={submitting || !quiz.questions.every(q => answers[q._id])}
              className="bg-gradient-to-r from-teal-600 via-teal-500 to-cyan-600 px-8 shadow-lg"
              data-testid="submit-button"
            >
              {submitting ? t('quiz.submitting') : t('quiz.submit_quiz')}
            </Button>
          </motion.div>
        ) : (
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              onClick={handleNext}
              disabled={!answers[currentQ._id]}
              className="bg-gradient-to-r from-teal-500 to-cyan-600 px-6"
              data-testid="next-button"
            >
              {t('quiz.next')}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </motion.div>
        )}
      </div>

      {/* Banner Ad */}
      <BannerAdPlaceholder />
    </div>
  );
}
