import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { DashboardSkeleton } from './SkeletonLoader';

/**
 * Role hierarchy for frontend protection
 * Must match backend/app/api/deps.py
 */
const ROLE_HIERARCHY = {
  'superadmin': 4,
  'admin': 3,
  'manager': 2,
  'employee': 1
};

/**
 * ProtectedRoute - Guards routes based on authentication and role requirements.
 * @param {React.ReactNode} children - The component to render if authorized
 * @param {string|string[]} requiredRole - Optional role requirement or list of roles
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
    const userRole = user?.role?.name?.toLowerCase();
    const requiredRoles = Array.isArray(requiredRole) 
      ? requiredRole.map(r => r.toLowerCase()) 
      : [requiredRole.toLowerCase()];

    // Check if user has direct role or a higher role in hierarchy
    const hasAccess = requiredRoles.some(req => {
      const userLevel = ROLE_HIERARCHY[userRole] || 0;
      const requiredLevel = ROLE_HIERARCHY[req] || 0;
      return userLevel >= requiredLevel;
    });

    if (!hasAccess) {
      console.warn(`Access denied for role: ${userRole}. Required: ${requiredRoles}`);
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
};


