// Performance-optimized selectors for Zustand stores
// These selectors help prevent unnecessary re-renders by using shallow equality

// Data Store Selectors
export const selectEarthquakeData = (state) => ({
  earthquakes: state.earthquakes,
  significantEarthquakes: state.significantEarthquakes,
});

export const selectVolcanoData = (state) => state.volcanoes;

export const selectStatistics = (state) => state.statistics;

export const selectLoadingState = (state) => ({
  loading: state.loading,
  error: state.error,
});

export const selectDataActions = (state) => ({
  fetchData: state.fetchData,
  toggleShowAllEarthquakes: state.toggleShowAllEarthquakes,
  updateCurrentTime: state.updateCurrentTime,
});

export const selectEarthquakesOnly = (state) => state.earthquakes;

export const selectVolcanoesOnly = (state) => state.volcanoes;

export const selectFilterState = (state) => ({
  showAllEarthquakes: state.showAllEarthquakes,
  lastUpdate: state.lastUpdate,
  currentTime: state.currentTime,
});

// Calendar Store Selectors
export const selectCalendarData = (state) => ({
  currentDate: state.currentDate,
  calendarData: state.calendarData,
  selectedDate: state.selectedDate,
  worstYears: state.worstYears,
});

export const selectCalendarActions = (state) => ({
  changeMonth: state.changeMonth,
  setSelectedDate: state.setSelectedDate,
  getEventsForDate: state.getEventsForDate,
});

export const selectCalendarLoading = (state) => state.loading;

// Earthquake List Store Selectors
export const selectEarthquakeListPreferences = (state) => ({
  showSignificant: state.showSignificant,
  sortBy: state.sortBy,
});

export const selectEarthquakeListActions = (state) => ({
  setShowSignificant: state.setShowSignificant,
  setSortBy: state.setSortBy,
  toggleShowSignificant: state.toggleShowSignificant,
});

// Statistics Store Selectors
export const selectStatisticsAnimationState = (state) => ({
  chartKey: state.chartKey,
  showCharts: state.showCharts,
  animateCards: state.animateCards,
});

export const selectStatisticsActions = (state) => ({
  triggerAnimations: state.triggerAnimations,
  setShowCharts: state.setShowCharts,
  setAnimateCards: state.setAnimateCards,
});

// Tab Store Selectors
export const selectActiveTab = (state) => state.activeTab;

export const selectTabActions = (state) => ({
  setActiveTab: state.setActiveTab,
});

export const selectTabState = (state) => ({
  activeTab: state.activeTab,
  tabChangeCount: state.tabChangeCount,
});

// AI Analysis Store Selectors
export const selectAIAnalysis = (state) => ({
  analysis: state.analysis,
  loading: state.loading,
  error: state.error,
  lastGenerated: state.lastGenerated,
});

export const selectAIAnalysisActions = (state) => ({
  generateAnalysis: state.generateAnalysis,
  clearAnalysis: state.clearAnalysis,
});
