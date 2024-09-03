import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import { ToastContainer } from 'react-toastify';
import MainChat from './views/MainChat'
import AccountAccess from './views/AccountAccess';

const router = createBrowserRouter([
  {
    path: "/",
    element: <AccountAccess />
  },
  {
    path: "/chat",
    element: <MainChat />
  }
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ToastContainer
      position="top-right"
      autoClose={5000}
      hideProgressBar={false}
      newestOnTop={false}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      className="z-50"
    />
    <RouterProvider router={router} />
  </StrictMode>,
)
