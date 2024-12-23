import create from 'zustand';
import { SelectionState } from '../navigation/types';

interface Restaurant {
  name: string;
  cuisine: string;
  rating: number;
  priceLevel: string;
  distance: string;
  image: string;
  tags: string[];
  openNow: boolean;
}

interface StoreState {
  selectionState: SelectionState;
  currentRestaurant: Restaurant | null;
  updateSelection: (key: keyof SelectionState, value: any) => void;
  resetSelection: () => void;
  setCurrentRestaurant: (restaurant: Restaurant) => void;
}

const initialSelectionState: SelectionState = {
  cuisine: null,
  priceRange: null,
  mood: null,
  distance: null,
};

export const useStore = create<StoreState>((set) => ({
  selectionState: initialSelectionState,
  currentRestaurant: null,
  updateSelection: (key, value) =>
    set((state) => ({
      selectionState: {
        ...state.selectionState,
        [key]: value,
      },
    })),
  resetSelection: () =>
    set(() => ({
      selectionState: initialSelectionState,
    })),
  setCurrentRestaurant: (restaurant) =>
    set(() => ({
      currentRestaurant: restaurant,
    })),
})); 