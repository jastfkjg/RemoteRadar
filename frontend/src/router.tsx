import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { JobsPage } from './pages/JobsPage';
import { JobDetailPage } from './pages/JobDetailPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { AuthProvider } from './contexts/AuthContext';

const router = createBrowserRouter([
  {
    path: '/',
    element: <JobsPage />,
  },
  {
    path: '/jobs',
    element: <JobsPage />,
  },
  {
    path: '/jobs/:jobId',
    element: <JobDetailPage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/recommendations',
    element: <RecommendationsPage />,
  },
]);

export const AppRouter: React.FC = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
};
