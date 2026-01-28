import { create } from 'zustand';
import toast from 'react-hot-toast';
import axiosInstance from '../lib/axios';

export const useSourceStore = create((set) => ({
  sources: [],
  selectedSource: null,
  isUploading: false,


  fetchSources: async () => {
    set({ sources: [], selectedSource: null });
  },

  addFileSource: async (file) => {
    try {
      set({ isUploading: true });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', 'marksheet');

      const res = await axiosInstance.post(
        '/api/upload-document',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      const newSource = {
        _id: res.data.doc_id,
        title: '12th Marksheet',
        content: res.data.extracted_preview,
        type: 'document',
        createdAt: new Date().toISOString(),
      };

      set((state) => ({
        sources: [newSource, ...state.sources],
        selectedSource: newSource,
      }));

      toast.success('Document uploaded');
      return { success: true };
    } catch (e) {
      console.error(e);
      toast.error('Upload failed');
      return { success: false };
    } finally {
      set({ isUploading: false });
    }
  },

  selectSource: (source) => set({ selectedSource: source }),

  clearSources: () => set({ sources: [], selectedSource: null }),
}));
