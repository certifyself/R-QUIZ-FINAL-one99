import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { LanguageSwitcher } from '../../components/LanguageSwitcher';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Mail, Lock as LockIcon, User as UserIcon, Sparkles } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register({ email, password, nickname });
      toast.success('Account created successfully!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-slate-50 to-cyan-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <motion.div
        animate={{ 
          scale: [1, 1.2, 1],
          rotate: [0, 90, 180, 270, 360]
        }}
        transition={{ 
          duration: 30,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute top-10 right-10 w-64 h-64 bg-teal-200/30 rounded-full blur-3xl"
      />
      <motion.div
        animate={{ 
          scale: [1, 1.3, 1],
          rotate: [360, 270, 180, 90, 0]
        }}
        transition={{ 
          duration: 25,
          repeat: Infinity,
          ease: "linear"
        }}
        className="absolute bottom-10 left-10 w-80 h-80 bg-cyan-200/30 rounded-full blur-3xl"
      />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full bg-white/80 backdrop-blur-xl rounded-3xl p-10 border border-slate-200 shadow-2xl relative z-10"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', duration: 0.8 }}
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="w-20 h-20 mx-auto mb-4 relative"
          >
            <img 
              src="/logo.jpeg" 
              alt="SocraQuest" 
              className="w-full h-full rounded-full object-cover shadow-xl ring-4 ring-teal-500/30"
            />
            <motion.div
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [0.5, 0.8, 0.5]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="absolute inset-0 rounded-full bg-gradient-to-tr from-teal-500/20 to-cyan-500/20"
            />
          </motion.div>
          <motion.h2 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold mb-4 font-['Space_Grotesk']"
          >
            <span className="bg-gradient-to-r from-teal-700 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
              SocraQuest
            </span>
          </motion.h2>
          <h1 className="text-3xl font-bold mb-2 font-['Space_Grotesk']">
            <span className="bg-gradient-to-r from-teal-700 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
              Join SocraQuest
            </span>
          </h1>
          <p className="text-slate-600 flex items-center justify-center space-x-2">
            <Sparkles className="w-4 h-4 text-teal-500" />
            <span>Start your learning journey</span>
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Label htmlFor="nickname" className="text-slate-700 font-semibold">Nickname</Label>
            <div className="relative mt-2">
              <UserIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                id="nickname"
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                className="pl-10 h-12 bg-white border-slate-300 focus:border-teal-500 focus:ring-teal-500"
                placeholder="Your name"
                required
                data-testid="nickname-input"
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Label htmlFor="email" className="text-slate-700 font-semibold">Email</Label>
            <div className="relative mt-2">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 h-12 bg-white border-slate-300 focus:border-teal-500 focus:ring-teal-500"
                placeholder="you@example.com"
                required
                data-testid="email-input"
              />
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Label htmlFor="password" className="text-slate-700 font-semibold">Password</Label>
            <div className="relative mt-2">
              <LockIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={6}
                className="pl-10 h-12 bg-white border-slate-300 focus:border-teal-500 focus:ring-teal-500"
                placeholder="••••••••"
                required
                data-testid="password-input"
              />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-gradient-to-r from-teal-600 via-teal-500 to-cyan-600 hover:from-teal-700 hover:via-teal-600 hover:to-cyan-700 text-white font-bold text-lg shadow-lg hover:shadow-xl transition-all"
              data-testid="register-button"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </motion.div>
        </form>

        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center text-sm text-slate-600 mt-6"
        >
          Already have an account?{' '}
          <Link to="/login" className="text-teal-600 font-bold hover:text-teal-700 hover:underline">
            Sign in
          </Link>
        </motion.p>
      </motion.div>
    </div>
  );
}
