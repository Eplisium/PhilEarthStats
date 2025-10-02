import { create } from 'zustand';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const useCalendarStore = create((set, get) => ({
  // State
  currentDate: new Date(),
  calendarData: [],
  selectedDate: null,
  loading: false,
  worstYears: [],
  error: null,
  syncing: false,
  syncStatus: null,

  // Actions
  setCurrentDate: (currentDate) => {
    set({ currentDate, selectedDate: null });
    get().fetchCalendarData();
  },

  setSelectedDate: (selectedDate) => set({ selectedDate }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  // Change month
  changeMonth: (offset) => {
    const { currentDate } = get();
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + offset, 1);
    get().setCurrentDate(newDate);
  },

  // Fetch calendar data for current month
  fetchCalendarData: async () => {
    set({ loading: true, error: null });
    
    try {
      const { currentDate } = get();
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;
      const response = await fetch(`${API_BASE_URL}/api/calendar?year=${year}&month=${month}`);
      const data = await response.json();
      
      if (data.success) {
        const hasData = data.calendar_data && data.calendar_data.length > 0;
        set({ calendarData: data.calendar_data, loading: false });
        
        // If no data exists for historical months (not future), auto-sync from USGS
        const now = new Date();
        const isPastMonth = year < now.getFullYear() || 
                           (year === now.getFullYear() && month < now.getMonth() + 1);
        const isFutureMonth = year > now.getFullYear() || 
                             (year === now.getFullYear() && month > now.getMonth() + 1);
        
        // Only auto-sync for past months (not current or future months)
        if (!hasData && isPastMonth && !isFutureMonth && year >= 2000) {
          await get().syncHistoricalMonth(year, month);
        }
      } else {
        set({ error: 'Failed to fetch calendar data', loading: false });
      }
    } catch (error) {
      console.error('Error fetching calendar data:', error);
      set({ error: 'Failed to fetch calendar data', loading: false });
    }
  },

  // Sync historical data from USGS for a specific month
  syncHistoricalMonth: async (year, month) => {
    set({ syncing: true, syncStatus: `Fetching historical data for ${month}/${year}...` });
    
    try {
      // Calculate start and end dates for the month
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const lastDay = new Date(year, month, 0).getDate();
      const endDate = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
      
      const response = await fetch(`${API_BASE_URL}/api/history/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        set({ 
          syncStatus: `Synced ${data.synced_count} events from ${month}/${year}`,
          syncing: false 
        });
        
        // Refresh calendar data
        await get().fetchCalendarData();
        
        // Clear sync status after 3 seconds
        setTimeout(() => {
          set({ syncStatus: null });
        }, 3000);
      } else {
        set({ 
          syncStatus: 'Failed to sync historical data',
          syncing: false 
        });
      }
    } catch (error) {
      console.error('Error syncing historical data:', error);
      set({ 
        syncStatus: 'Error syncing historical data',
        syncing: false 
      });
    }
  },

  // Manually sync a date range
  syncDateRange: async (startDate, endDate) => {
    set({ syncing: true, syncStatus: 'Syncing historical data...' });
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/history/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        set({ 
          syncStatus: `Successfully synced ${data.synced_count} events`,
          syncing: false 
        });
        
        await get().fetchCalendarData();
        
        setTimeout(() => {
          set({ syncStatus: null });
        }, 3000);
        
        return true;
      } else {
        set({ 
          syncStatus: 'Failed to sync data',
          syncing: false 
        });
        return false;
      }
    } catch (error) {
      console.error('Error syncing date range:', error);
      set({ 
        syncStatus: 'Error syncing data',
        syncing: false 
      });
      return false;
    }
  },

  // Fetch worst years data
  fetchWorstYears: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/history/worst-years?limit=10`);
      const data = await response.json();
      
      if (data.success) {
        set({ worstYears: data.worst_years });
      }
    } catch (error) {
      console.error('Error fetching worst years:', error);
    }
  },

  // Initialize calendar (call on mount)
  initialize: async () => {
    await Promise.all([
      get().fetchCalendarData(),
      get().fetchWorstYears(),
    ]);
  },

  // Get events for a specific date
  getEventsForDate: (day) => {
    const { currentDate, calendarData } = get();
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return calendarData.find(d => d.date === dateStr);
  },

  // Reset
  reset: () => set({
    currentDate: new Date(),
    calendarData: [],
    selectedDate: null,
    loading: false,
    worstYears: [],
    error: null,
    syncing: false,
    syncStatus: null,
  }),
}));

export default useCalendarStore;
