import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

import { useEffect } from 'react';
import { setUser, User } from "./features/auth/authSlice";
import { jwtDecode } from 'jwt-decode';

export const useAuthCheck = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const checkAuth = () => {
      const accessToken = localStorage.getItem('access_token');
      console.log("LOAD ACCESS TOKEN: ", accessToken);

      if (accessToken) {
        try {
          const decoded = jwtDecode(accessToken);
          console.log("DECODED TOKEN: ", decoded);
          dispatch(setUser(decoded as User));
        } catch (error) {
          console.error("Error decoding token:", error);
        }
      }
    };

    checkAuth();
  }, [dispatch]);

  return null;
};