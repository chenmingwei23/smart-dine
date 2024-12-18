import React from 'react';
import { createStackNavigator, CardStyleInterpolators } from '@react-navigation/stack';
import { StyleSheet } from 'react-native';
import HomeScreen from '../screens/HomeScreen';
import SelectionScreen from '../screens/SelectionScreen';
import ResultScreen from '../screens/ResultScreen';
import ReviewsScreen from '../screens/ReviewsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import { RootStackParamList } from './types';

const Stack = createStackNavigator<RootStackParamList>();

const screenOptions = {
  headerStyle: {
    backgroundColor: '#FF6B6B',
  },
  headerTintColor: '#fff',
  headerTitleStyle: {
    fontWeight: '700' as const,
  },
  cardStyleInterpolator: CardStyleInterpolators.forHorizontalIOS,
  gestureEnabled: true,
  gestureDirection: 'horizontal' as const,
};

export default function RootNavigator() {
  return (
    <Stack.Navigator
      initialRouteName="Home"
      screenOptions={screenOptions}
    >
      <Stack.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'SmartDine',
          cardStyleInterpolator: CardStyleInterpolators.forFadeFromBottomAndroid,
        }}
      />
      <Stack.Screen 
        name="Selection" 
        component={SelectionScreen}
        options={{
          title: 'Find Your Meal',
          cardStyleInterpolator: CardStyleInterpolators.forHorizontalIOS,
        }}
      />
      <Stack.Screen 
        name="Result" 
        component={ResultScreen}
        options={{
          title: 'Perfect Match',
          cardStyleInterpolator: CardStyleInterpolators.forModalPresentationIOS,
        }}
      />
      <Stack.Screen 
        name="Reviews" 
        component={ReviewsScreen}
        options={{
          title: 'Reviews',
          cardStyleInterpolator: CardStyleInterpolators.forVerticalIOS,
        }}
      />
      <Stack.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'My Profile',
          cardStyleInterpolator: CardStyleInterpolators.forHorizontalIOS,
        }}
      />
    </Stack.Navigator>
  );
} 