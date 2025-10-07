import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Header UI Store
 * Manages header compact/expand state with persistence
 */
const useHeaderStore = create(
  persist(
    (set) => ({
      // State
      compactHeader: false,
      
      // Actions
      setCompactHeader: (isCompact) => set({ compactHeader: isCompact }),
      
      toggleCompactHeader: () => set((state) => ({ 
        compactHeader: !state.compactHeader 
      })),
      
      // Reset to defaults
      reset: () => set({
        compactHeader: false,
      }),
    }),
    {
      name: 'header-preferences',
      partialize: (state) => ({
        compactHeader: state.compactHeader,
      }),
    }
  )
);

export default useHeaderStore;
