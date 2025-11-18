import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Home, Trophy, Users, User, LogOut, LayoutDashboard } from 'lucide-react';
import { Button } from '../components/ui/button';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';

export function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-teal-50 to-slate-100">
      {/* Header */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-white/80 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-50 shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link to="/" className="flex items-center space-x-3 group">
              <motion.div 
                whileHover={{ scale: 1.05, rotate: 5 }}
                whileTap={{ scale: 0.95 }}
                className="relative"
              >
                <img 
                  src="/logo.jpeg" 
                  alt="SocraQuest" 
                  className="w-14 h-14 rounded-full object-cover shadow-lg ring-2 ring-teal-500/20 group-hover:ring-teal-500/40 transition-all"
                />
                <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-teal-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              </motion.div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-teal-700 via-teal-600 to-teal-500 bg-clip-text text-transparent font-['Space_Grotesk']">
                  SocraQuest
                </span>
                <p className="text-xs text-slate-500 font-medium">Daily Trivia Challenge</p>
              </div>
            </Link>
            
            <div className="flex items-center space-x-4">
              {/* Language Switcher - Always visible */}
              <LanguageSwitcher />
              
              {user && (
                <>
                  <motion.div 
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="hidden sm:flex items-center space-x-3 px-4 py-2 bg-gradient-to-r from-teal-50 to-teal-100 rounded-full"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center text-white font-bold text-sm shadow-lg">
                      {user.nickname?.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-sm font-medium text-teal-900">{user.nickname}</span>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button 
                      onClick={handleLogout} 
                      variant="ghost" 
                      size="sm" 
                      className="text-slate-700 hover:text-teal-700 hover:bg-teal-50"
                      data-testid="logout-button"
                      title={t('auth.logout')}
                    >
                      <LogOut className="w-4 h-4" />
                    </Button>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:ml-64">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Bottom Navigation (Mobile) */}
      {user && (
        <motion.nav 
          initial={{ y: 100 }}
          animate={{ y: 0 }}
          className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-slate-200 z-50 md:hidden shadow-lg"
        >
          <div className="flex justify-around items-center h-16">
            {[
              { to: '/', icon: Home, label: t('nav.home'), testId: 'nav-home' },
              { to: '/rankings', icon: Trophy, label: t('nav.rankings'), testId: 'nav-rankings' },
              { to: '/groups', icon: Users, label: t('nav.groups'), testId: 'nav-groups' },
              { to: '/profile', icon: User, label: t('nav.profile'), testId: 'nav-profile' },
              ...(isAdmin ? [{ to: '/admin', icon: LayoutDashboard, label: t('nav.admin'), testId: 'nav-admin' }] : [])
            ].map(({ to, icon: Icon, label, testId }) => (
              <Link
                key={to}
                to={to}
                className={`flex flex-col items-center justify-center flex-1 h-full transition-all ${
                  isActive(to) || (to === '/admin' && location.pathname.startsWith('/admin'))
                    ? 'text-teal-600 scale-110' 
                    : 'text-slate-600 hover:text-teal-500'
                }`}
                data-testid={testId}
              >
                <motion.div whileTap={{ scale: 0.9 }}>
                  <Icon className="w-6 h-6" />
                  <span className="text-xs mt-1 font-medium">{label}</span>
                </motion.div>
              </Link>
            ))}
          </div>
        </motion.nav>
      )}

      {/* Desktop Navigation (Sidebar) */}
      {user && (
        <motion.nav 
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          className="hidden md:block fixed left-0 top-20 bottom-0 w-64 bg-white/80 backdrop-blur-lg border-r border-slate-200 z-40 shadow-xl"
        >
          <div className="p-6 space-y-2">
            {[
              { to: '/', icon: Home, label: 'Home', testId: 'desktop-nav-home' },
              { to: '/rankings', icon: Trophy, label: 'Rankings', testId: 'desktop-nav-rankings' },
              { to: '/groups', icon: Users, label: 'Groups', testId: 'desktop-nav-groups' },
              { to: '/profile', icon: User, label: 'Profile', testId: 'desktop-nav-profile' },
              ...(isAdmin ? [{ to: '/admin', icon: LayoutDashboard, label: 'Admin', testId: 'desktop-nav-admin' }] : [])
            ].map(({ to, icon: Icon, label, testId }) => (
              <Link
                key={to}
                to={to}
                data-testid={testId}
              >
                <motion.div
                  whileHover={{ x: 8, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                    isActive(to) || (to === '/admin' && location.pathname.startsWith('/admin'))
                      ? 'bg-gradient-to-r from-teal-500 to-teal-600 text-white shadow-lg shadow-teal-500/50' 
                      : 'text-slate-700 hover:bg-teal-50 hover:text-teal-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-semibold">{label}</span>
                </motion.div>
              </Link>
            ))}
          </div>
        </motion.nav>
      )}
      
      {/* Padding for bottom nav on mobile */}
      {user && <div className="h-16 md:hidden" />}
    </div>
  );
}
