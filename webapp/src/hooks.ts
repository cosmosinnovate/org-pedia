import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

import { useEffect } from 'react';
import { setUser, User } from "./features/auth/authSlice";
import { jwtDecode } from 'jwt-decode';


export const useAuthCheck = (): User | null => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const checkAuth = () => {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        try {
          const decoded = jwtDecode(accessToken) as User;
          
          // Check if the token is expired
          const currentTime = Date.now() / 1000;
          if (decoded.exp < currentTime) {
            console.log("Token is expired");
            localStorage.removeItem('access_token');
            return null;
          }

          const user: User = {
            id: decoded.id,
            email: decoded.email,
            photo_url: decoded.photo_url,
            display_name: decoded.display_name,
            access_token: accessToken,
            user_google_id: decoded.user_google_id,
            exp: decoded.exp,
          };

          dispatch(setUser(user));
          return user;
        } catch (error) {
          console.error("Error decoding token:", error);
        }
      }
      return null;
    };

    checkAuth();
  }, [dispatch]);

  return null;
};