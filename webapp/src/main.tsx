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
import ProtectedRoute from './ProtectedRoute';
import { Provider } from 'react-redux';
import { store } from './store';


const router = createBrowserRouter([
  {
    path: "/",
    element: <AccountAccess />
  },
  {
    path: "/chat",
    element:
      <ProtectedRoute allowGuest={true}>
        <MainChat />
      </ProtectedRoute>
  },
])

createRoot(document.getElementById('root')!).render(
  <Provider store={store}>
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
  </Provider>
)
