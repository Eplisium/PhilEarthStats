import { create } from 'zustand';

const useTabStore = create((set) => ({
  activeTab: 'map',
  tabChangeCount: 0, // Increment each time tab changes to trigger animations
  
  setActiveTab: (tab) => set((state) => ({
    activeTab: tab,
    tabChangeCount: state.tabChangeCount + 1
  })),
}));

export default useTabStore;
