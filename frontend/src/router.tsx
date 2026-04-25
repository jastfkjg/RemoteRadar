import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { JobsPage } from './pages/JobsPage';
import { JobDetailPage } from './pages/JobDetailPage';

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
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};
