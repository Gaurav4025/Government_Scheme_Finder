import { create } from 'zustand';
import toast from 'react-hot-toast';

// Dummy sources for testing
const DUMMY_SOURCES = [
  {
    _id: '1',
    title: 'Getting Started with React',
    content: 'React is a JavaScript library for building user interfaces with reusable components...',
    summary: 'Learn the basics of React and how to build component-based UIs.',
    type: 'text',
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    _id: '2',
    title: 'JavaScript ES6 Features',
    content: 'ES6 introduced many new features like arrow functions, classes, destructuring, and more...',
    summary: 'An overview of modern JavaScript features introduced in ES6.',
    type: 'text',
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    _id: '3',
    title: 'Web Development Best Practices',
    content: 'Follow these best practices for better web development: use semantic HTML, optimize images, etc...',
    summary: 'Key best practices for modern web development.',
    type: 'text',
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
  }
];

export const useSourceStore = create((set, get) => ({
  sources: [],
  selectedSource: null,
  isLoading: false,
  isUploading: false,

  fetchSources: async () => {
    try {
      set({ isLoading: true });
      // Load from localStorage or use dummy sources
      const savedSources = localStorage.getItem('sources');
      let sources = savedSources ? JSON.parse(savedSources) : [...DUMMY_SOURCES];
      sources = sources.reverse();
      
      set((state) => ({
        sources,
        selectedSource:
          state.selectedSource && sources.find((s) => s._id === state.selectedSource._id)
            ? state.selectedSource
            : (sources[0] || null),
      }));
    } catch (error) {
      console.error('Fetch sources error:', error);
      const message = 'Failed to fetch sources';
      toast.error(message);
    } finally {
      set({ isLoading: false });
    }
  },

  addTextSource: async (text) => {
    try {
      set({ isUploading: true });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 600));
      
      // Create dummy source
      const newSource = {
        _id: Math.random().toString(36).substr(2, 9),
        title: text.substring(0, 50) + '...',
        content: text,
        summary: 'This is a summary of the provided text source.',
        type: 'text',
        createdAt: new Date().toISOString()
      };
      
      set(state => {
        const updatedSources = [newSource, ...state.sources];
        localStorage.setItem('sources', JSON.stringify(updatedSources));
        return {
          sources: updatedSources,
          selectedSource: newSource
        };
      });
      
      toast.success("Text source added successfully");
      return { success: true, source: newSource };
    } catch (error) {
      console.error("Add text source error:", error);
      const message = "Failed to add text source";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isUploading: false });
    }
  },

  addFileSource: async (file) => {
    try {
      set({ isUploading: true });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Create dummy source from file
      const newSource = {
        _id: Math.random().toString(36).substr(2, 9),
        title: file.name,
        content: `File content from ${file.name}`,
        summary: 'This is a summary of the uploaded file.',
        type: 'file',
        fileName: file.name,
        fileSize: file.size,
        createdAt: new Date().toISOString()
      };
      
      set(state => {
        const updatedSources = [newSource, ...state.sources];
        localStorage.setItem('sources', JSON.stringify(updatedSources));
        return {
          sources: updatedSources,
          selectedSource: newSource
        };
      });
      
      toast.success("File uploaded successfully");
      return { success: true, source: newSource };
    } catch (error) {
      console.error("Add file source error:", error);
      const message = "Failed to upload file";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isUploading: false });
    }
  },

  addUrlSource: async (url) => {
    try {
      set({ isUploading: true });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Create dummy source from URL
      const newSource = {
        _id: Math.random().toString(36).substr(2, 9),
        title: new URL(url).hostname,
        content: `Content from ${url}`,
        summary: 'This is a summary of the web page content.',
        type: 'url',
        url: url,
        createdAt: new Date().toISOString()
      };
      
      set(state => {
        const updatedSources = [newSource, ...state.sources];
        localStorage.setItem('sources', JSON.stringify(updatedSources));
        return {
          sources: updatedSources,
          selectedSource: newSource
        };
      });
      
      toast.success("URL source added successfully");
      return { success: true, source: newSource };
    } catch (error) {
      console.error("Add URL source error:", error);
      const message = "Failed to add URL source";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      set({ isUploading: false });
    }
  },

  selectSource: (source) => {
    set({ selectedSource: source });
  },

  clearSources: () => {
    set({ sources: [], selectedSource: null });
    localStorage.removeItem('sources');
  }
}));