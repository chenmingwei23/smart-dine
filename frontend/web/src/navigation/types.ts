export interface SelectionState {
  cuisine?: string;
  priceRange?: string;
  distance?: number;
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