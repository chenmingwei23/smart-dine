import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import RootNavigator from './src/navigation/RootNavigator';
import { useStore } from './src/store';

export default function App() {
  // Initialize any global state if needed
  const setUser = useStore(state => state.setUser);

  return (
    <NavigationContainer>
      <RootNavigator />
    </NavigationContainer>
  );
}
