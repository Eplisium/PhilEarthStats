import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useEarthquakeListStore = create(
  persist(
    (set) => ({
      // State
      showSignificant: false,
      sortBy: 'time', // 'time', 'magnitude', 'depth'

      // Actions
      setShowSignificant: (showSignificant) => set({ showSignificant }),
      
      setSortBy: (sortBy) => set({ sortBy }),
      
      toggleShowSignificant: () => set((state) => ({ 
        showSignificant: !state.showSignificant 
      })),

      // Reset to defaults
      reset: () => set({
        showSignificant: false,
        sortBy: 'time',
      }),
    }),
    {
      name: 'earthquake-list-preferences',
      partialize: (state) => ({
        sortBy: state.sortBy,
        // Don't persist showSignificant as it should reset on page load
      }),
    }
  )
);

export default useEarthquakeListStore;
