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

export function QuizPage() {
  const { quizIndex } = useParams();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startTime, setStartTime] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [showAdGate, setShowAdGate] = useState(false);
  const [adShown, setAdShown] = useState(false);

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

  const loadQuiz = async () => {
    try {
      const res = await userAPI.getQuiz(quizIndex);
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
    // Check all questions answered
    const allAnswered = quiz.questions.every(q => answers[q._id]);
    if (!allAnswered) {
      toast.error('Please answer all questions before submitting');
      return;
    }

    const timeMs = Date.now() - startTime;

    setSubmitting(true);
    try {
      const res = await userAPI.submitQuiz(quizIndex, {
        answers: quiz.questions.map(q => ({
          question_id: q._id,
          choice_key: answers[q._id]
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
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          onClick={() => navigate('/')}
          variant="ghost"
          size="sm"
          data-testid="back-button"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        
        <div className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg border border-slate-200">
          <Clock className="w-4 h-4 text-teal-600" />
          <span className="font-mono font-semibold text-teal-600">{formatTime(elapsedTime)}</span>
        </div>
      </div>

      {/* Quiz Info */}
      <div className="bg-white rounded-xl p-6 border border-slate-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 font-['Space_Grotesk']">
              {quizIndex === '10' ? 'Bonus Quiz' : `Quiz ${parseInt(quizIndex) + 1}`}
            </h1>
            <p className="text-sm text-slate-600">{quiz.topic?.name}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-600">Attempt {quiz.attempt_number}/3</p>
            <p className="text-xs text-slate-500">{quiz.attempts_remaining} remaining</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-teal-500 to-teal-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-slate-600 mt-2 text-center">
          Question {currentQuestion + 1} of {quiz.questions.length}
        </p>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-xl p-8 border border-slate-200">
        <h2 className="text-xl font-medium text-slate-900 mb-6 font-['Space_Grotesk']">
          {currentQ.text}
        </h2>

        <div className="space-y-3">
          {currentQ.options.map((option) => (
            <button
              key={option.key}
              onClick={() => handleAnswer(currentQ._id, option.key)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                answers[currentQ._id] === option.key
                  ? 'border-teal-500 bg-teal-50'
                  : 'border-slate-200 bg-white hover:border-teal-300'
              }`}
              data-testid={`option-${option.key}`}
            >
              <div className="flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                  answers[currentQ._id] === option.key
                    ? 'bg-teal-600 text-white'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {option.key}
                </div>
                <span className="text-slate-700">{option.label}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <Button
          onClick={handlePrevious}
          variant="outline"
          disabled={currentQuestion === 0}
          data-testid="previous-button"
        >
          Previous
        </Button>

        {currentQuestion === quiz.questions.length - 1 ? (
          <Button
            onClick={handleSubmit}
            disabled={submitting || !quiz.questions.every(q => answers[q._id])}
            className="bg-gradient-to-r from-teal-500 to-teal-600"
            data-testid="submit-button"
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </Button>
        ) : (
          <Button
            onClick={handleNext}
            disabled={!answers[currentQ._id]}
            className="bg-gradient-to-r from-teal-500 to-teal-600"
            data-testid="next-button"
          >
            Next
          </Button>
        )}
      </div>

      {/* Banner Ad */}
      <BannerAdPlaceholder />
    </div>
  );
}
