import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useMapStore = create(
  devtools(
    (set) => ({
      selectedEarthquake: null,
      
      setSelectedEarthquake: (earthquake) => set({ selectedEarthquake: earthquake }),
      
      clearSelectedEarthquake: () => set({ selectedEarthquake: null }),
    }),
    { name: 'MapStore' }
  )
);

export default useMapStore;
