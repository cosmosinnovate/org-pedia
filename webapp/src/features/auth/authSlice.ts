
// src/features/auth/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface User {
  id?: number | string;
  user_id: string;
  display_name: string;
  email: string;
  photo_url: string;
  access_token: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
}

const initialState: AuthState = {
  user: null,
  loading: true,
};

const removeAccessToken = () => localStorage.removeItem("access_token")

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User | null>) => {
      state.user = action.payload;
      state.loading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    logoutUser: (state) => {
      state.user = null;
      state.loading = false;
      removeAccessToken()
    },
  },
});

export const { setUser, setLoading, logoutUser } = authSlice.actions;
export default authSlice.reducer;
