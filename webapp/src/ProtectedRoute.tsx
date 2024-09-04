import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from './hooks';
import { RootState } from './store';

interface ProtectedRouteProps {
  allowGuest?: boolean;
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowGuest = false, children }) => {
  const user = useAppSelector((state: RootState) => state.auth.user);

  // Allow access if the user is logged in or guest access is permitted
  if (!user && !allowGuest) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
