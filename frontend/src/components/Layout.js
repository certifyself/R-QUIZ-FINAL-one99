import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Home, Trophy, Users, User, LogOut, LayoutDashboard } from 'lucide-react';
import { Button } from '../components/ui/button';

export function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">?</span>
              </div>
              <span className="text-xl font-bold text-slate-900 font-['Space_Grotesk']">SocraQuest</span>
            </Link>
            
            <div className="flex items-center space-x-4">
              {user && (
                <>
                  <span className="text-sm text-slate-600 hidden sm:block">{user.nickname}</span>
                  <Button onClick={handleLogout} variant="ghost" size="sm" data-testid="logout-button">
                    <LogOut className="w-4 h-4" />
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:ml-64">
        {children}
      </main>

      {/* Bottom Navigation (Mobile) */}
      {user && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-50 md:hidden">
          <div className="flex justify-around items-center h-16">
            <Link
              to="/"
              className={`flex flex-col items-center justify-center flex-1 h-full ${
                isActive('/') ? 'text-teal-600' : 'text-slate-600'
              }`}
              data-testid="nav-home"
            >\n              <Home className="w-6 h-6" />
              <span className="text-xs mt-1">Home</span>
            </Link>
            
            <Link
              to="/rankings"
              className={`flex flex-col items-center justify-center flex-1 h-full ${
                isActive('/rankings') ? 'text-teal-600' : 'text-slate-600'
              }`}
              data-testid="nav-rankings"
            >
              <Trophy className="w-6 h-6" />
              <span className="text-xs mt-1">Rankings</span>
            </Link>
            
            <Link
              to="/groups"
              className={`flex flex-col items-center justify-center flex-1 h-full ${
                isActive('/groups') ? 'text-teal-600' : 'text-slate-600'
              }`}
              data-testid="nav-groups"
            >
              <Users className="w-6 h-6" />
              <span className="text-xs mt-1">Groups</span>
            </Link>
            
            <Link
              to="/profile"
              className={`flex flex-col items-center justify-center flex-1 h-full ${
                isActive('/profile') ? 'text-teal-600' : 'text-slate-600'
              }`}
              data-testid="nav-profile"
            >
              <User className="w-6 h-6" />
              <span className="text-xs mt-1">Profile</span>
            </Link>

            {isAdmin && (
              <Link
                to="/admin"
                className={`flex flex-col items-center justify-center flex-1 h-full ${
                  location.pathname.startsWith('/admin') ? 'text-teal-600' : 'text-slate-600'
                }`}
                data-testid="nav-admin"
              >
                <LayoutDashboard className="w-6 h-6" />
                <span className="text-xs mt-1">Admin</span>
              </Link>
            )}
          </div>
        </nav>
      )}

      {/* Desktop Navigation (Tablet and above) */}
      {user && (
        <nav className="hidden md:block fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-slate-200 z-40">
          <div className="p-4 space-y-2">
            <Link
              to="/"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive('/') ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-100'
              }`}
              data-testid="desktop-nav-home"
            >
              <Home className="w-5 h-5" />
              <span className="font-medium">Home</span>
            </Link>
            
            <Link
              to="/rankings"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive('/rankings') ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-100'
              }`}
              data-testid="desktop-nav-rankings"
            >
              <Trophy className="w-5 h-5" />
              <span className="font-medium">Rankings</span>
            </Link>
            
            <Link
              to="/groups"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive('/groups') ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-100'
              }`}
              data-testid="desktop-nav-groups"
            >
              <Users className="w-5 h-5" />
              <span className="font-medium">Groups</span>
            </Link>
            
            <Link
              to="/profile"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive('/profile') ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-100'
              }`}
              data-testid="desktop-nav-profile"
            >
              <User className="w-5 h-5" />
              <span className="font-medium">Profile</span>
            </Link>

            {isAdmin && (
              <Link
                to="/admin"
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  location.pathname.startsWith('/admin') ? 'bg-teal-50 text-teal-700' : 'text-slate-700 hover:bg-slate-100'
                }`}
                data-testid="desktop-nav-admin"
              >
                <LayoutDashboard className="w-5 h-5" />
                <span className="font-medium">Admin</span>
              </Link>
            )}
          </div>
        </nav>
      )}
      
      {/* Padding for bottom nav on mobile */}
      {user && <div className="h-16 md:hidden" />}
    </div>
  );
}
