export interface SelectionState {
  cuisine: string | null;
  priceRange: string | null;
  mood: string | null;
  distance: number | null;
}

export type RootStackParamList = {
  Home: undefined;
  Selection: undefined;
  Result: { selections: SelectionState };
  Reviews: undefined;
  Profile: undefined;
};

export type BottomTabParamList = {
  SelectionFlow: undefined;
  Reviews: undefined;
  Profile: undefined;
};

export type SelectionKey = keyof SelectionState; 