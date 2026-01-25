import { create } from 'zustand';
import toast from 'react-hot-toast';
import { axiosInstance } from '../lib/axios';

export const useChatStore = create((set) => ({
  messages: [],
  isLoading: false,
  sources: [],

  sendMessage: async (userData, question) => {
    try {
      set({ isLoading: true });

      // Add user message immediately
      set(state => ({
        messages: [
          ...state.messages,
          { role: 'user', content: question }
        ]
      }));

      // Call backend
      const res = await axiosInstance.post('/api/test-eligibility', {
        user_data: userData,
        question: question
      });

      //Add assistant response
      set(state => ({
        messages: [
          ...state.messages,
          {
            role: 'assistant',
            content: res.data.response
          }
        ],
        sources: res.data.sources
      }));

      return { success: true };

    } catch (error) {
      console.error(error);
      toast.error("Failed to get eligibility response");
      return { success: false };
    } finally {
      set({ isLoading: false });
    }
  },

  clearChat: () => {
    set({ messages: [], sources: [] });
  }
}));
