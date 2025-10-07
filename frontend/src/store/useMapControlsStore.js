import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Map Controls Store
 * Manages map layer visibility, filters, and display preferences
 */
const useMapControlsStore = create(
  persist(
    (set) => ({
      // Layer Visibility
      showEarthquakes: true,
      showVolcanoes: true,
      
      // Filters
      magnitudeFilter: 0,
      
      // Map Style
      basemap: 'street', // 'street', 'satellite', 'dark', 'terrain'
      
      // View State (not persisted)
      isFullscreen: false,
      isLocating: false,
      
      // User Location (not persisted)
      userLocation: null,
      locationStats: null,
      
      // Map Position (not persisted)
      mapCenter: null,
      mapZoom: null,
      shouldFlyTo: false,
      
      // Layer Actions
      setShowEarthquakes: (show) => set({ showEarthquakes: show }),
      setShowVolcanoes: (show) => set({ showVolcanoes: show }),
      toggleShowEarthquakes: () => set((state) => ({ 
        showEarthquakes: !state.showEarthquakes 
      })),
      toggleShowVolcanoes: () => set((state) => ({ 
        showVolcanoes: !state.showVolcanoes 
      })),
      
      // Filter Actions
      setMagnitudeFilter: (magnitude) => set({ magnitudeFilter: magnitude }),
      
      // Basemap Actions
      setBasemap: (basemap) => set({ basemap }),
      
      // View State Actions
      setIsFullscreen: (isFullscreen) => set({ isFullscreen }),
      setIsLocating: (isLocating) => set({ isLocating }),
      
      // User Location Actions
      setUserLocation: (location) => set({ userLocation: location }),
      setLocationStats: (stats) => set({ locationStats: stats }),
      clearUserLocation: () => set({ 
        userLocation: null, 
        locationStats: null 
      }),
      
      // Map Position Actions
      setMapCenter: (center) => set({ mapCenter: center }),
      setMapZoom: (zoom) => set({ mapZoom: zoom }),
      setShouldFlyTo: (shouldFly) => set({ shouldFlyTo: shouldFly }),
      setMapView: (center, zoom, flyTo = true) => set({ 
        mapCenter: center, 
        mapZoom: zoom, 
        shouldFlyTo: flyTo 
      }),
      
      // Reset Actions
      resetFilters: () => set({
        magnitudeFilter: 0,
        showEarthquakes: true,
        showVolcanoes: true,
      }),
      
      resetView: () => set({
        mapCenter: null,
        mapZoom: null,
        shouldFlyTo: false,
      }),
      
      reset: () => set({
        showEarthquakes: true,
        showVolcanoes: true,
        magnitudeFilter: 0,
        basemap: 'street',
        isFullscreen: false,
        isLocating: false,
        userLocation: null,
        locationStats: null,
        mapCenter: null,
        mapZoom: null,
        shouldFlyTo: false,
      }),
    }),
    {
      name: 'map-controls-preferences',
      partialize: (state) => ({
        showEarthquakes: state.showEarthquakes,
        showVolcanoes: state.showVolcanoes,
        magnitudeFilter: state.magnitudeFilter,
        basemap: state.basemap,
        // Don't persist: isFullscreen, isLocating, userLocation, locationStats, map position
      }),
    }
  )
);

export default useMapControlsStore;
