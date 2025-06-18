import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Subjects from './pages/Subjects';
import Questions from './pages/Questions';
import Achievements from './pages/Achievements';
import Leaderboard from './pages/Leaderboard';
import Store from './pages/Store';
import Quizzes from './pages/Quizzes';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import AIAssistant from './pages/AIAssistant';
import AdminPanel from './pages/AdminPanel';
import Gamification from './pages/Gamification';
import StudyPlan from './pages/StudyPlan';
import ExamSimulator from './pages/ExamSimulator';
import Library from './pages/Library';
import Mentorship from './pages/Mentorship';
import ContentManager from './pages/ContentManager';

// Componente para rotas protegidas
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  // Reduce o tempo de loading para evitar loops infinitos
  if (loading.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Componente para rotas públicas (quando já logado, redireciona)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  // Para rotas públicas como login, sempre mostra o componente
  // Só redireciona se já estiver autenticado E não estiver carregando
  if (isAuthenticated && !loading.isLoading) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

// Componente principal da aplicação
const AppContent: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Rotas Públicas */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Rotas Protegidas */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Rotas implementadas */}
        <Route
          path="/subjects"
          element={
            <ProtectedRoute>
              <Layout>
                <Subjects />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/questions"
          element={
            <ProtectedRoute>
              <Layout>
                <Questions />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/achievements"
          element={
            <ProtectedRoute>
              <Layout>
                <Achievements />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/leaderboard"
          element={
            <ProtectedRoute>
              <Layout>
                <Leaderboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/store"
          element={
            <ProtectedRoute>
              <Layout>
                <Store />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/quizzes"
          element={
            <ProtectedRoute>
              <Layout>
                <Quizzes />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Layout>
                <Analytics />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/ai-assistant"
          element={
            <ProtectedRoute>
              <Layout>
                <AIAssistant />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <Layout>
                <AdminPanel />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/gamification"
          element={
            <ProtectedRoute>
              <Layout>
                <Gamification />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/study-plan"
          element={
            <ProtectedRoute>
              <Layout>
                <StudyPlan />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/exam-simulator"
          element={
            <ProtectedRoute>
              <Layout>
                <ExamSimulator />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/library"
          element={
            <ProtectedRoute>
              <Layout>
                <Library />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/mentorship"
          element={
            <ProtectedRoute>
              <Layout>
                <Mentorship />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/content-manager"
          element={
            <ProtectedRoute>
              <Layout>
                <ContentManager />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Rota 404 */}
        <Route
          path="*"
          element={
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900">404</h1>
                <p className="text-gray-600 mt-2">Página não encontrada</p>
                <a
                  href="/"
                  className="mt-4 inline-block bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Voltar ao início
                </a>
              </div>
            </div>
          }
        />
      </Routes>
    </Router>
  );
};

// App principal com Provider
const App: React.FC = () => {
  return (
    <AuthProvider>
      <NotificationProvider>
        <AppContent />
      </NotificationProvider>
    </AuthProvider>
  );
};

export default App;
