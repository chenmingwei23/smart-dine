import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const MOCK_USER = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  preferences: {
    favoriteCuisines: ['Japanese', 'Italian', 'Thai'],
    usualBudget: '$$',
    preferredDistance: '5km',
  },
  stats: {
    restaurantsVisited: 24,
    reviewsWritten: 15,
    favoritePlaces: 8,
  }
};

export default function ProfileScreen() {
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.content}>
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Image
              source={{ uri: 'https://via.placeholder.com/100' }}
              style={styles.avatar}
            />
          </View>
          <Text style={styles.name}>{MOCK_USER.name}</Text>
          <Text style={styles.email}>{MOCK_USER.email}</Text>
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{MOCK_USER.stats.restaurantsVisited}</Text>
            <Text style={styles.statLabel}>Visited</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{MOCK_USER.stats.reviewsWritten}</Text>
            <Text style={styles.statLabel}>Reviews</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statNumber}>{MOCK_USER.stats.favoritePlaces}</Text>
            <Text style={styles.statLabel}>Favorites</Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          <View style={styles.preferenceItem}>
            <Ionicons name="restaurant-outline" size={20} color="#94B06B" />
            <Text style={styles.preferenceLabel}>Favorite Cuisines:</Text>
            <Text style={styles.preferenceValue}>
              {MOCK_USER.preferences.favoriteCuisines.join(', ')}
            </Text>
          </View>
          <View style={styles.preferenceItem}>
            <Ionicons name="wallet-outline" size={20} color="#94B06B" />
            <Text style={styles.preferenceLabel}>Usual Budget:</Text>
            <Text style={styles.preferenceValue}>{MOCK_USER.preferences.usualBudget}</Text>
          </View>
          <View style={styles.preferenceItem}>
            <Ionicons name="location-outline" size={20} color="#94B06B" />
            <Text style={styles.preferenceLabel}>Preferred Distance:</Text>
            <Text style={styles.preferenceValue}>{MOCK_USER.preferences.preferredDistance}</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.editButton}>
          <Text style={styles.editButtonText}>Edit Profile</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#334027',
  },
  content: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#192112',
    marginBottom: 16,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    overflow: 'hidden',
  },
  avatar: {
    width: '100%',
    height: '100%',
  },
  name: {
    fontFamily: 'Roboto-Bold',
    fontSize: 24,
    color: '#F4F7EE',
    marginBottom: 4,
  },
  email: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#94B06B',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#192112',
    borderRadius: 16,
    padding: 20,
    marginBottom: 30,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontFamily: 'Roboto-Bold',
    fontSize: 24,
    color: '#94B06B',
    marginBottom: 4,
  },
  statLabel: {
    fontFamily: 'Roboto',
    fontSize: 14,
    color: '#E6EDDA',
  },
  section: {
    backgroundColor: '#192112',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontFamily: 'Roboto-Bold',
    fontSize: 20,
    color: '#94B06B',
    marginBottom: 16,
  },
  preferenceItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  preferenceLabel: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#E6EDDA',
    marginRight: 8,
  },
  preferenceValue: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#F4F7EE',
    flex: 1,
  },
  editButton: {
    backgroundColor: '#94B06B',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  editButtonText: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#192112',
    letterSpacing: 0.5,
  },
}); 