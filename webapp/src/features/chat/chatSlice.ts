
// src/features/chat/chatSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface MessageResponse {
  id?: string;
  messages?: Message[];
  title?: string;
  user_id?: string
}

interface MessageState {
  chat: MessageResponse[];
  loading: boolean;
}

const initialState: MessageState = {
  chat: [],
  loading: true,
};

const authSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setChat: (state, action: PayloadAction<MessageResponse[]>) => {
      state.chat = action.payload;
      state.loading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setChat, setLoading } = authSlice.actions;
export default authSlice.reducer;
