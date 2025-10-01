import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAIAnalysisStore = create(
  persist(
    (set) => ({
      // State
      analysis: null,
      loading: false,
      error: null,
      lastGenerated: null,

      // Actions
      setAnalysis: (analysis) => set({ 
        analysis, 
        error: null,
        lastGenerated: new Date().toISOString()
      }),
      
      setLoading: (loading) => set({ loading }),
      
      setError: (error) => set({ error, loading: false }),
      
      clearAnalysis: () => set({ 
        analysis: null, 
        error: null, 
        loading: false,
        lastGenerated: null 
      }),
      
      // Fetch analysis from API
      generateAnalysis: async () => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          const data = await response.json();

          if (data.success) {
            set({ 
              analysis: data, 
              loading: false, 
              error: null,
              lastGenerated: new Date().toISOString()
            });
          } else {
            set({ 
              error: data.error || 'Failed to generate analysis', 
              loading: false 
            });
          }
        } catch (err) {
          set({ 
            error: 'Failed to connect to the server. Please try again.', 
            loading: false 
          });
          console.error('Error generating AI analysis:', err);
        }
      },
    }),
    {
      name: 'ai-analysis-storage', // localStorage key
      partialize: (state) => ({ 
        analysis: state.analysis,
        lastGenerated: state.lastGenerated
      }), // Only persist these fields
    }
  )
);

export default useAIAnalysisStore;
