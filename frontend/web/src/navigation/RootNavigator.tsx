import React from 'react';
import { TouchableOpacity, StyleSheet, View } from 'react-native';
import { createStackNavigator } from '@react-navigation/stack';
import { Ionicons } from '@expo/vector-icons';
import HomeScreen from '../screens/HomeScreen';
import SelectionScreen from '../screens/SelectionScreen';
import ResultScreen from '../screens/ResultScreen';
import ReviewsScreen from '../screens/ReviewsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import FavoritesScreen from '../screens/FavoritesScreen';
import { RootStackParamList } from './types';
import { useStore } from '../store';

const Stack = createStackNavigator<RootStackParamList>();

export default function RootNavigator() {
  const { resetSelection } = useStore();

  const handleNewSelection = (navigation: any) => {
    resetSelection();
    navigation.navigate('Selection');
  };

  return (
    <Stack.Navigator
      screenOptions={({ navigation, route }) => ({
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
        headerRight: () => (
          <View style={styles.headerButtons}>
            {navigation.canGoBack() && (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => navigation.navigate('Home')}
              >
                <Ionicons name="home-outline" size={24} color="#94B06B" />
              </TouchableOpacity>
            )}
            {route.name !== 'Selection' && route.name !== 'Home' && (
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => handleNewSelection(navigation)}
              >
                <Ionicons name="restaurant-outline" size={24} color="#94B06B" />
              </TouchableOpacity>
            )}
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => navigation.navigate('Favorites')}
            >
              <Ionicons name="heart-outline" size={24} color="#94B06B" />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => navigation.navigate('Profile')}
            >
              <Ionicons name="person-outline" size={24} color="#94B06B" />
            </TouchableOpacity>
          </View>
        ),
      })}
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
        name="Favorites" 
        component={FavoritesScreen}
        options={{ title: 'Your Favorites' }}
      />
      <Stack.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ title: 'Your Profile' }}
      />
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  headerButtons: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerButton: {
    marginLeft: 8,
    marginRight: 8,
    padding: 8,
  },
}); 