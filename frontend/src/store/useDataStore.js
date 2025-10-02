import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const useDataStore = create(
  devtools(
    (set, get) => ({
      // State
      earthquakes: [],
      significantEarthquakes: [],
      statistics: null,
      volcanoes: [],
      loading: false,
      lastUpdate: null,
      currentTime: new Date(),
      showAllEarthquakes: false,
      error: null,

      // Computed values (selectors)
      getActiveVolcanoesCount: () => {
        return get().volcanoes.filter(v => v.alert_level > 0).length;
      },

      getMaxMagnitude: () => {
        return get().statistics?.magnitude_stats?.max || 0;
      },

      // Actions
      setEarthquakes: (earthquakes) => set({ earthquakes }),
      
      setSignificantEarthquakes: (significantEarthquakes) => set({ significantEarthquakes }),
      
      setStatistics: (statistics) => set({ statistics }),
      
      setVolcanoes: (volcanoes) => set({ volcanoes }),
      
      setLoading: (loading) => set({ loading }),
      
      setShowAllEarthquakes: (showAllEarthquakes) => set({ showAllEarthquakes }),
      
      setCurrentTime: (currentTime) => set({ currentTime }),
      
      setError: (error) => set({ error }),

      // Update current time (for clock)
      updateCurrentTime: () => set({ currentTime: new Date() }),

      // Fetch all data
      fetchData: async () => {
        set({ loading: true, error: null });
        
        try {
          const { showAllEarthquakes } = get();
          const earthquakeEndpoint = showAllEarthquakes 
            ? '/api/earthquakes/all' 
            : '/api/earthquakes/recent';
          
          const [earthquakesRes, significantRes, statsRes, volcanoesRes] = await Promise.all([
            fetch(`${API_BASE_URL}${earthquakeEndpoint}`),
            fetch(`${API_BASE_URL}/api/earthquakes/significant`),
            fetch(`${API_BASE_URL}/api/earthquakes/statistics`),
            fetch(`${API_BASE_URL}/api/volcanoes/active`)
          ]);

          const earthquakesData = await earthquakesRes.json();
          const significantData = await significantRes.json();
          const statsData = await statsRes.json();
          const volcanoesData = await volcanoesRes.json();

          const updates = {
            loading: false,
            lastUpdate: new Date(),
            error: null,
          };

          if (earthquakesData.success) {
            updates.earthquakes = earthquakesData.earthquakes;
          }
          if (significantData.success) {
            updates.significantEarthquakes = significantData.earthquakes;
          }
          if (statsData.success) {
            updates.statistics = statsData;
          }
          if (volcanoesData.success) {
            updates.volcanoes = volcanoesData.volcanoes;
          }

          set(updates);
        } catch (error) {
          console.error('Error fetching data:', error);
          set({ 
            error: 'Failed to fetch data. Please try again.', 
            loading: false 
          });
        }
      },

      // Toggle show all earthquakes and refetch
      toggleShowAllEarthquakes: async () => {
        const newValue = !get().showAllEarthquakes;
        set({ showAllEarthquakes: newValue });
        await get().fetchData();
      },

      // Reset all data
      reset: () => set({
        earthquakes: [],
        significantEarthquakes: [],
        statistics: null,
        volcanoes: [],
        loading: false,
        lastUpdate: null,
        error: null,
      }),
    }),
    { name: 'DataStore' }
  )
);

export default useDataStore;
