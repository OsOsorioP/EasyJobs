import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useAuthStore } from './hooks/useAuthStore';
import Login from './components/features/auth/Login';
import Register from './components/features/auth/Register';
import DashboardLayout from './components/layout/Dashboard';

export default function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();

  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard/cognitive" replace />
          ) : (
            <Login onNavigateToRegister={() => navigate('/register')} />
          )
        } 
      />
      <Route 
        path="/register" 
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard/cognitive" replace />
          ) : (
            <Register onBackToLogin={() => navigate('/login')} />
          )
        } 
      />
      <Route 
        path="/dashboard/*" 
        element={
          isAuthenticated ? (
            <DashboardLayout />
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      <Route path="*" element={<Navigate to="/dashboard/cognitive" replace />} />
    </Routes>
  );
}