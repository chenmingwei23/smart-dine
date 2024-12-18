import create from 'zustand';
import { SelectionState } from '../navigation/types';

interface StoreState {
  selectionState: SelectionState;
  currentRestaurant: any;
  updateSelection: (key: keyof SelectionState, value: string | number) => void;
  resetSelection: () => void;
  setCurrentRestaurant: (restaurant: any) => void;
}

export const useStore = create<StoreState>((set) => ({
  selectionState: {
    cuisine: undefined,
    priceRange: undefined,
    distance: undefined,
  },
  currentRestaurant: null,
  updateSelection: (key, value) => 
    set((state) => ({
      selectionState: { ...state.selectionState, [key]: value }
    })),
  resetSelection: () => 
    set({ selectionState: { cuisine: undefined, priceRange: undefined, distance: undefined } }),
  setCurrentRestaurant: (restaurant) => 
    set({ currentRestaurant: restaurant }),
})); 