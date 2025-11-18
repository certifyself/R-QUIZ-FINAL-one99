import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { PageLoading } from './components/LoadingSpinner';
import { Toaster } from 'sonner';

// Auth Pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';

// User Pages
import { HomePage } from './pages/user/HomePage';
import { QuizPage } from './pages/user/QuizPage';
import { ResultsPage } from './pages/user/ResultsPage';
import { RankingsPage } from './pages/user/RankingsPage';
import { GroupsPage } from './pages/user/GroupsPage';
import { ProfilePage } from './pages/user/ProfilePage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <PageLoading />;
  }

  return user ? children : <Navigate to="/login" />;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <PageLoading />;
  }

  return !user ? children : <Navigate to="/" />;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-center" richColors />
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />

          {/* Private Routes */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <HomePage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/quiz/:quizIndex"
            element={
              <PrivateRoute>
                <Layout>
                  <QuizPage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/results/:quizIndex"
            element={
              <PrivateRoute>
                <Layout>
                  <ResultsPage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/rankings"
            element={
              <PrivateRoute>
                <Layout>
                  <RankingsPage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/groups"
            element={
              <PrivateRoute>
                <Layout>
                  <GroupsPage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <Layout>
                  <ProfilePage />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <Layout>
                  <AdminDashboard />
                </Layout>
              </PrivateRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
