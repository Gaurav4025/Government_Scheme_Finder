import { create } from 'zustand';
import toast from 'react-hot-toast';

// Dummy user for testing
const DUMMY_USER = {
  _id: '123456',
  name: 'Test User',
  email: 'test@example.com'
};

export const useAuthStore = create((set) => ({
  authUser: null,
  isCheckingAuth: false,
  isLoading: false,

  checkAuth: async () => {
    try {
      set({ isCheckingAuth: true });
      // Check localStorage for existing auth
      const savedUser = localStorage.getItem('authUser');
      if (savedUser) {
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
      // Dummy login - accept any credentials
      const user = {
        ...DUMMY_USER,
        name: credentials.email.split('@')[0],
        email: credentials.email
      };
      
      localStorage.setItem('authUser', JSON.stringify(user));
      localStorage.setItem('authToken', 'dummy-token-123');
      
      set({ 
        authUser: user
      });
      
      toast.success("Login successful");
      return { success: true };
    } catch (error) {
      console.error("Login error:", error);
      const message = error.message || "Login failed";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (credentials) => {
    try {
      set({ isLoading: true });
      // Dummy register - accept any credentials
      const user = {
        _id: Math.random().toString(36).substr(2, 9),
        name: credentials.name,
        email: credentials.email
      };
      
      localStorage.setItem('authUser', JSON.stringify(user));
      localStorage.setItem('authToken', 'dummy-token-123');
      
      set({ 
        authUser: user
      });
      
      toast.success("Registration successful");
      return { success: true };
    } catch (error) {
      console.error("Register error:", error);
      const message = error.message || "Registration failed";
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