import { create } from 'zustand';
import toast from 'react-hot-toast';

// Dummy responses for testing
const DUMMY_RESPONSES = [
  "This is a great question! Based on the content provided, I can tell you that...",
  "That's an interesting point. Looking at the source material, I found that...",
  "Excellent observation! The key information about this is...",
  "Based on my analysis of the source, here's what I found...",
  "This relates to an important concept mentioned in the source..."
];

export const useChatStore = create((set, get) => ({
  messages: [],
  isLoading: false,
  currentSourceId: null,

  sendMessage: async (message, sourceId) => {
    try {
      set({ isLoading: true });
      
      // Add user message immediately
      const userMessage = { role: 'user', content: message };
      set(state => ({ 
        messages: [...state.messages, userMessage],
        currentSourceId: sourceId
      }));
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Add dummy assistant response
      const dummyResponse = DUMMY_RESPONSES[Math.floor(Math.random() * DUMMY_RESPONSES.length)];
      const assistantMessage = { 
        role: 'assistant', 
        content: dummyResponse
      };
      
      set(state => ({ 
        messages: [...state.messages, assistantMessage]
      }));
      
      return { success: true };
    } catch (error) {
      console.error("Send message error:", error);
      const errorMessage = "Failed to send message";
      toast.error(errorMessage);
      
      // Remove the user message that failed
      set(state => ({ 
        messages: state.messages.slice(0, -1)
      }));
      
      return { success: false, error: errorMessage };
    } finally {
      set({ isLoading: false });
    }
  },

  clearChat: () => {
    set({ messages: [], currentSourceId: null });
  },

  loadChatForSource: async (sourceId) => {
    try {
      set({ isLoading: true, messages: [], currentSourceId: sourceId });
      // Dummy chat load - start with empty messages
      set({ messages: [] });
    } catch (error) {
      console.error("Load chat error:", error);
      const message = "Failed to load chat";
      toast.error(message);
    } finally {
      set({ isLoading: false });
    }
  }
}));