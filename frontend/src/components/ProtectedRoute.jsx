import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { DashboardSkeleton } from './SkeletonLoader';

/**
 * ProtectedRoute - Guards routes based on authentication and role requirements.
 * @param {React.ReactNode} children - The component to render if authorized
 * @param {string} requiredRole - Optional role requirement ('Admin' allows Managers too)
 */
export const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user, isHydrated } = useAuthStore();
  const location = useLocation();

  // Show loading spinner while auth state is being restored from storage
  if (!isHydrated) {
    return <DashboardSkeleton />;
  }

  // Redirect unauthenticated users to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Role-based access control
  if (requiredRole) {
    const userRole = user?.role?.name;
    const allowedRoles = requiredRole === 'Admin'
      ? ['Admin', 'Manager']  // Managers can access Admin routes
      : [requiredRole];

    if (!allowedRoles.includes(userRole)) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
};

