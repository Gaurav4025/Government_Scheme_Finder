import { create } from 'zustand';
import toast from 'react-hot-toast';
import axios from '../lib/axios';

export const useAuthStore = create((set) => ({
  authUser: null,
  isCheckingAuth: false,
  isLoading: false,

  checkAuth: async () => {
    try {
      set({ isCheckingAuth: true });
      // Check localStorage for existing auth
      const savedUser = localStorage.getItem('authUser');
      const token = localStorage.getItem('authToken');
      if (savedUser && token) {
        set({
          authUser: JSON.parse(savedUser)
        });
      }
    } catch (error) {
      console.error("Check auth error:", error);
      set({
        authUser: null
      });
    } finally {
      set({ isCheckingAuth: false });
    }
  },

  login: async (credentials) => {
    try {
      set({ isLoading: true });
      const response = await axios.post('/api/login', credentials);
      const { token, user_id } = response.data;

      const user = {
        _id: user_id,
        email: credentials.email,
        profileCompleted:false
      };

      localStorage.setItem('authUser', JSON.stringify(user));
      localStorage.setItem('authToken', token);

      set({
        authUser: user
      });

      toast.success("Login successful");
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      const message = error.response?.data?.detail || "Login failed";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (credentials) => {
    try {
      set({ isLoading: true });
      const response = await axios.post('/api/register', credentials);
      const { token, user_id } = response.data;

      const user = {
        _id: user_id,
        email: credentials.email,
        profileCompleted: false


      };

      localStorage.setItem('authUser', JSON.stringify(user));
      localStorage.setItem('authToken', token);

      set({
        authUser: user
      });

      toast.success("Registration successful");
      return { success: true };
    } catch (error) {
      console.error("Register error:", error);
      const message = error.response?.data?.detail || "Registration failed";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    localStorage.removeItem('authUser');
    localStorage.removeItem('authToken');
    set({ authUser: null });
    toast.success("Logged out successfully");
  }
}));
