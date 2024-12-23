import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from '../screens/HomeScreen';
import SelectionScreen from '../screens/SelectionScreen';
import ResultScreen from '../screens/ResultScreen';
import ReviewsScreen from '../screens/ReviewsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import { RootStackParamList } from './types';

const Stack = createStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#192112',
          elevation: 0,
          shadowOpacity: 0,
        },
        headerTintColor: '#F4F7EE',
        headerTitleStyle: {
          fontFamily: 'Roboto-Bold',
          fontSize: 20,
          color: '#94B06B',
        },
        cardStyle: {
          backgroundColor: '#334027',
        },
      }}
    >
      <Stack.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="Selection" 
        component={SelectionScreen}
        options={{ title: 'Make Your Selection' }}
      />
      <Stack.Screen 
        name="Result" 
        component={ResultScreen}
        options={{ title: 'Your Match' }}
      />
      <Stack.Screen 
        name="Reviews" 
        component={ReviewsScreen}
        options={{ title: 'Restaurant Reviews' }}
      />
      <Stack.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Your Profile' }}
      />
    </Stack.Navigator>
  );
} 