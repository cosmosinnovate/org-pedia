import MainChat from "./views/MainChat";
import { useAuthCheck } from './hooks';
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import AccountAccess from "./views/AccountAccess";
import React from 'react';
import { Navigate, useNavigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from './store';
import ErrorBoundary from "./views/ErrorComponent";

const AuthAwareRoot: React.FC = () => {
  useAuthCheck();
  const isAuthenticated = useSelector((state: RootState) => state.auth.user);
  const navigate = useNavigate();
  
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/new');
    }
  }, [isAuthenticated, navigate]);
  return <Outlet />;
};

const ProtectedRoute: React.FC<{ allowGuest: boolean; children: React.ReactNode }> = ({ allowGuest, children }) => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.user);
  if (!isAuthenticated && !allowGuest) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <AuthAwareRoot />,
    errorElement: <ErrorBoundary><Outlet /></ErrorBoundary>,
    children: [
      {
        index: true,
        element: <AccountAccess />
      },
      {
        path: "new",
        element: (
          <ProtectedRoute allowGuest={false}>
            <ErrorBoundary><MainChat /></ErrorBoundary>
          </ProtectedRoute>
        )
      },
      {
        path: "/o/chat/:chatId",
        element: (
          <ProtectedRoute allowGuest={false}>
            <ErrorBoundary><MainChat /></ErrorBoundary>
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