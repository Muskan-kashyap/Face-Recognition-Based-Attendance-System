import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ProtectedRoute } from './components/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';
import { Spinner } from './components/ui/Spinner';

const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

// Lazy-loaded pages for code splitting
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const Overview = lazy(() => import('./pages/Overview'));
const Attendance = lazy(() => import('./pages/Attendance'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const Reports = lazy(() => import('./pages/Reports'));
const Settings = lazy(() => import('./pages/Settings'));
const Ticketing = lazy(() => import('./pages/Ticketing'));
const Payroll = lazy(() => import('./pages/Payroll'));
const Reimbursements = lazy(() => import('./pages/Reimbursements'));

const LoadingFallback = () => (
  <div className="min-h-screen bg-gray-950 flex items-center justify-center">
    <Spinner size="xl" className="text-indigo-500" />
  </div>
);

const AppRoutes = () => {
  const location = useLocation();

  return (
    <Routes location={location}>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Protected Dashboard Routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout><Overview /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/attendance" element={
        <ProtectedRoute>
          <DashboardLayout><Attendance /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/users" element={
        <ProtectedRoute requiredRole="Admin">
          <DashboardLayout><UserManagement /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/reports" element={
        <ProtectedRoute requiredRole="Admin">
          <DashboardLayout><Reports /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/settings" element={
        <ProtectedRoute>
          <DashboardLayout><Settings /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/ticketing" element={
        <ProtectedRoute>
          <DashboardLayout><Ticketing /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/payroll" element={
        <ProtectedRoute requiredRole="Admin">
          <DashboardLayout><Payroll /></DashboardLayout>
        </ProtectedRoute>
      } />
      <Route path="/dashboard/reimbursements" element={
        <ProtectedRoute>
          <DashboardLayout><Reimbursements /></DashboardLayout>
        </ProtectedRoute>
      } />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App = () => {
  const { hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <Router>
      <ScrollToTop />
      <Suspense fallback={<LoadingFallback />}>
        <AppRoutes />
      </Suspense>
    </Router>
  );
};

export default App;
