import MainChat from "./views/MainChat";
import { useAuthCheck } from './hooks';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import AccountAccess from "./views/AccountAccess";

import React from 'react';
import { Navigate, useNavigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from './store'; // Adjust this import based on your store setup

// Root component that checks auth and renders children or redirects
const AuthAwareRoot: React.FC = () => {
  useAuthCheck();
  const isAuthenticated = useSelector((state: RootState) => state.auth.user);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat');
    }
  }, [isAuthenticated, navigate]);

  return <Outlet />;
};

// Protected route component
const ProtectedRoute: React.FC<{ allowGuest: boolean; children: React.ReactNode }> = ({ allowGuest, children }) => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.user);

  if (!isAuthenticated && !allowGuest) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

// Router configuration
const router = createBrowserRouter([
  {
    path: "/",
    element: <AuthAwareRoot />,
    children: [
      {
        index: true,
        element: <AccountAccess />
      },
      {
        path: "chat",
        element: (
          <ProtectedRoute allowGuest={false}>
            <MainChat />
          </ProtectedRoute>
        )
      }
    ]
  }
]);

const App = () => {
  useAuthCheck();
  return <RouterProvider router={router} />
}

export default App;