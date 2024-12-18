import create from 'zustand';

interface UserPreferences {
  vegetarian: boolean;
  notifications: boolean;
  darkMode: boolean;
  maxDistance: number;
}

interface UserStats {
  reviewsCount: number;
  favoritesCount: number;
  visitsCount: number;
}

interface User {
  name: string;
  email: string;
  avatar: string;
  preferences: UserPreferences;
  stats: UserStats;
}

interface SelectionState {
  cuisine: string | null;
  priceRange: string | null;
  distance: number | null;
}

interface AppState {
  // User state
  user: User | null;
  setUser: (user: User | null) => void;
  
  // Selection state
  selectionState: SelectionState;
  updateSelection: (key: keyof SelectionState, value: any) => void;
  resetSelection: () => void;
  
  // Restaurant state
  currentRestaurant: any | null;
  setCurrentRestaurant: (restaurant: any) => void;
}

const initialSelectionState: SelectionState = {
  cuisine: null,
  priceRange: null,
  distance: null,
};

export const useStore = create<AppState>((set) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),
  
  // Selection state
  selectionState: initialSelectionState,
  updateSelection: (key, value) => 
    set((state) => ({
      selectionState: {
        ...state.selectionState,
        [key]: value,
      },
    })),
  resetSelection: () => 
    set({ selectionState: initialSelectionState }),
  
  // Restaurant state
  currentRestaurant: null,
  setCurrentRestaurant: (restaurant) => 
    set({ currentRestaurant: restaurant }),
})); 