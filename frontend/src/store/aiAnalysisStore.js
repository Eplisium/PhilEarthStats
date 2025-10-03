import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { prepareAIOutput } from '../utils/formatAIOutput';

// Generate or retrieve session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('philEarthStats_sessionId');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('philEarthStats_sessionId', sessionId);
  }
  return sessionId;
};

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
      
      // Phase 4.3: Progress tracking
      progress: {
        stage: '',
        percentage: 0,
        message: ''
      },
      
      // Phase 4.4: Analysis history
      history: [],
      loadingHistory: false,
      sessionId: getSessionId(),

      // Actions
      setAnalysis: (analysis) => set({ 
        analysis, 
        error: null,
        lastGenerated: new Date().toISOString()
      }),
      
      setLoading: (loading) => set({ loading }),
      
      setError: (error) => set({ error, loading: false }),
      
      setSelectedModel: (model) => set({ selectedModel: model }),
      
      // Phase 4.3: Update progress
      setProgress: (stage, percentage, message) => set({
        progress: { stage, percentage, message }
      }),
      
      clearProgress: () => set({
        progress: { stage: '', percentage: 0, message: '' }
      }),
      
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
      
      // Fetch analysis from API with progress tracking
      generateAnalysis: async () => {
        set({ loading: true, error: null });
        get().clearProgress();
        
        try {
          const selectedModel = get().selectedModel;
          const sessionId = get().sessionId;
          
          // Simulate progress updates (in production, these would come from backend)
          const progressStages = [
            { stage: 'fetch', percentage: 10, message: 'Fetching earthquake data...' },
            { stage: 'regional', percentage: 25, message: 'Processing regional statistics...' },
            { stage: 'clusters', percentage: 40, message: 'Detecting seismic clusters...' },
            { stage: 'sequences', percentage: 55, message: 'Analyzing aftershock sequences...' },
            { stage: 'risk', percentage: 70, message: 'Calculating risk scores...' },
            { stage: 'ai', percentage: 85, message: 'Running AI analysis...' },
          ];
          
          // Start progress simulation
          let currentStageIndex = 0;
          const progressInterval = setInterval(() => {
            if (currentStageIndex < progressStages.length) {
              const stage = progressStages[currentStageIndex];
              get().setProgress(stage.stage, stage.percentage, stage.message);
              currentStageIndex++;
            }
          }, 2000);
          
          const response = await fetch('/api/ai/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              model: selectedModel,
              session_id: sessionId
            }),
          });

          clearInterval(progressInterval);
          get().setProgress('complete', 100, 'Finalizing results...');

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
            
            // Clear progress after short delay
            setTimeout(() => get().clearProgress(), 1000);
            
            // Refresh history
            get().fetchHistory();
          } else {
            set({ 
              error: data.error || 'Failed to generate analysis', 
              loading: false 
            });
            get().clearProgress();
          }
        } catch (err) {
          set({ 
            error: 'Failed to connect to the server. Please try again.', 
            loading: false 
          });
          get().clearProgress();
          console.error('Error generating AI analysis:', err);
        }
      },
      
      // Phase 4.4: Fetch analysis history
      fetchHistory: async () => {
        set({ loadingHistory: true });
        
        try {
          const sessionId = get().sessionId;
          const response = await fetch(`/api/ai/history?session_id=${sessionId}`);
          const data = await response.json();
          
          if (data.success) {
            set({ history: data.history, loadingHistory: false });
          } else {
            console.error('Failed to fetch history:', data.error);
            set({ loadingHistory: false });
          }
        } catch (err) {
          console.error('Error fetching history:', err);
          set({ loadingHistory: false });
        }
      },
      
      // Phase 4.4: Load analysis from history
      loadAnalysisFromHistory: async (analysisId) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`/api/ai/history/${analysisId}`);
          const data = await response.json();
          
          if (data.success) {
            // Reconstruct the analysis object
            const processedData = {
              success: true,
              analysis: prepareAIOutput(data.analysis.analysis_text),
              statistics: data.analysis.statistics,
              regional_breakdown: data.analysis.regional_stats,
              risk_scores: data.analysis.risk_scores,
              historical_comparison: data.analysis.historical_comparison,
              clusters: [],
              sequences: [],
              trends: { overall_trend: data.analysis.trend },
              b_value: data.analysis.b_value,
              volcano_correlation: {},
              significant_earthquakes: [],
              metadata: {
                model: data.analysis.model_used,
                generated: data.analysis.created_at_timestamp,
                period: `${data.analysis.period_days} days`,
                data_points: data.analysis.statistics.total_count
              }
            };
            
            set({ 
              analysis: processedData, 
              loading: false,
              lastGenerated: data.analysis.created_at
            });
          } else {
            set({ 
              error: data.error || 'Failed to load analysis', 
              loading: false 
            });
          }
        } catch (err) {
          set({ 
            error: 'Failed to load analysis from history', 
            loading: false 
          });
          console.error('Error loading analysis:', err);
        }
      },
      
      // Phase 4.4: Delete analysis from history
      deleteAnalysisFromHistory: async (analysisId) => {
        try {
          const sessionId = get().sessionId;
          const response = await fetch(`/api/ai/history/${analysisId}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId }),
          });
          
          const data = await response.json();
          
          if (data.success) {
            // Refresh history
            get().fetchHistory();
            
            // Clear current analysis if it was the deleted one
            const current = get().analysis;
            if (current && current.metadata && 
                current.metadata.generated === analysisId) {
              get().clearAnalysis();
            }
          } else {
            console.error('Failed to delete analysis:', data.error);
          }
        } catch (err) {
          console.error('Error deleting analysis:', err);
        }
      },
      
      // Phase 4.4: Compare analyses
      compareAnalyses: (analysisId1, analysisId2) => {
        // This would open a comparison view
        // Implementation depends on UI design
        console.log('Comparing analyses:', analysisId1, analysisId2);
      },
    }),
    {
      name: 'ai-analysis-storage', // localStorage key
      partialize: (state) => ({ 
        analysis: state.analysis,
        lastGenerated: state.lastGenerated,
        selectedModel: state.selectedModel,
        sessionId: state.sessionId
      }), // Only persist these fields
    }
  )
);

export default useAIAnalysisStore;
