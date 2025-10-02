import { create } from 'zustand';

const useStatisticsStore = create((set, get) => ({
  // State for animation control
  chartKey: 0,
  showCharts: false,
  animateCards: false,

  // Actions
  incrementChartKey: () => set((state) => ({ chartKey: state.chartKey + 1 })),

  setShowCharts: (showCharts) => set({ showCharts }),

  setAnimateCards: (animateCards) => set({ animateCards }),

  // Trigger animations when statistics tab becomes active
  triggerAnimations: () => {
    set({ showCharts: false, animateCards: false });
    
    // Return cleanup function
    const cardTimer = setTimeout(() => {
      set({ animateCards: true });
    }, 100);
    
    const chartTimer = setTimeout(() => {
      set((state) => ({ 
        chartKey: state.chartKey + 1,
        showCharts: true 
      }));
    }, 800);
    
    return () => {
      clearTimeout(cardTimer);
      clearTimeout(chartTimer);
    };
  },

  // Reset animations
  reset: () => set({
    chartKey: 0,
    showCharts: false,
    animateCards: false,
  }),
}));

export default useStatisticsStore;
