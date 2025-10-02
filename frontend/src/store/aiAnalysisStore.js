import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { prepareAIOutput } from '../utils/formatAIOutput';

const useAIAnalysisStore = create(
  persist(
    (set, get) => ({
      // State
      analysis: null,
      loading: false,
      error: null,
      lastGenerated: null,
      availableModels: [],
      selectedModel: null,
      loadingModels: false,

      // Actions
      setAnalysis: (analysis) => set({ 
        analysis, 
        error: null,
        lastGenerated: new Date().toISOString()
      }),
      
      setLoading: (loading) => set({ loading }),
      
      setError: (error) => set({ error, loading: false }),
      
      setSelectedModel: (model) => set({ selectedModel: model }),
      
      clearAnalysis: () => set({ 
        analysis: null, 
        error: null, 
        loading: false,
        lastGenerated: null 
      }),
      
      // Fetch available AI models
      fetchAvailableModels: async () => {
        set({ loadingModels: true });
        
        try {
          const response = await fetch('/api/ai/models');
          const data = await response.json();

          if (data.success) {
            set({ 
              availableModels: data.models,
              selectedModel: get().selectedModel || data.default_model,
              loadingModels: false
            });
          } else {
            console.error('Failed to fetch AI models:', data.error);
            set({ loadingModels: false });
          }
        } catch (err) {
          console.error('Error fetching AI models:', err);
          set({ loadingModels: false });
        }
      },
      
      // Fetch analysis from API
      generateAnalysis: async () => {
        set({ loading: true, error: null });
        
        try {
          const selectedModel = get().selectedModel;
          
          const response = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              model: selectedModel
            }),
          });

          const data = await response.json();

          if (data.success) {
            // Preprocess AI output for consistent formatting across all models
            const processedData = {
              ...data,
              analysis: prepareAIOutput(data.analysis)
            };
            
            set({ 
              analysis: processedData, 
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
        lastGenerated: state.lastGenerated,
        selectedModel: state.selectedModel
      }), // Only persist these fields
    }
  )
);

export default useAIAnalysisStore;
