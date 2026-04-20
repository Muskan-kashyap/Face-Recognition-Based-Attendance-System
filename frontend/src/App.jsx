import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';

// --- LAYOUTS ---
import DashboardLayout from './layouts/DashboardLayout';

// --- PAGES (Lazy Loaded for Performance) ---
const LandingPage = lazy(() => import('./pages/LandingPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const AttendanceModule = lazy(() => import('./pages/Attendance'));
const Overview = lazy(() => import('./pages/Overview'));
const UserManagement = lazy(() => import('./pages/UserManagement'));
const Reports = lazy(() => import('./pages/Reports'));
const Settings = lazy(() => import('./pages/Settings'));
const Ticketing = lazy(() => import('./pages/Ticketing'));
const Payroll = lazy(() => import('./pages/Payroll'));
const Reimbursements = lazy(() => import('./pages/Reimbursements'));


// --- APP COMPONENT ---
const App = () => {
  return (
    <Router>
      <Suspense fallback={
        <div className="fixed inset-0 bg-bg-deep flex items-center justify-center">
          <motion.div 
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-16 h-16 bg-primary rounded-2xl flex items-center justify-center shadow-2xl shadow-primary-glow"
          >
            <div className="w-8 h-8 border-4 border-white border-t-transparent rounded-full animate-spin" />
          </motion.div>
        </div>
      }>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          {/* Protected Dashboard Routes */}
          <Route path="/dashboard" element={
            <DashboardLayout userRole="Admin">
              <Overview />
            </DashboardLayout>
          } />
          <Route path="/dashboard/attendance" element={
            <DashboardLayout userRole="Admin">
                <AttendanceModule />
            </DashboardLayout>
          } />
          <Route path="/dashboard/users" element={
            <DashboardLayout userRole="Admin">
                <UserManagement />
            </DashboardLayout>
          } />
          <Route path="/dashboard/reports" element={
            <DashboardLayout userRole="Admin">
                <Reports />
            </DashboardLayout>
          } />
          <Route path="/dashboard/settings" element={
            <DashboardLayout userRole="Admin">
                <Settings />
            </DashboardLayout>
          } />
          <Route path="/dashboard/ticketing" element={
            <DashboardLayout userRole="Admin">
                <Ticketing />
            </DashboardLayout>
          } />
          <Route path="/dashboard/payroll" element={
            <DashboardLayout userRole="Admin">
                <Payroll />
            </DashboardLayout>
          } />
          <Route path="/dashboard/reimbursements" element={
            <DashboardLayout userRole="Admin">
                <Reimbursements />
            </DashboardLayout>
          } />


          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;
