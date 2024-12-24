import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Animated } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';

const MOCK_FAVORITES = [
  {
    id: '1',
    name: 'Sushi Paradise',
    cuisine: 'Japanese',
    rating: 4.8,
    priceLevel: '$$',
    distance: '0.8 km',
    image: 'https://via.placeholder.com/300x200',
    tags: ['Sushi', 'Japanese', 'Asian Fusion'],
    lastVisited: '2 days ago',
  },
  {
    id: '2',
    name: 'Pasta Villa',
    cuisine: 'Italian',
    rating: 4.6,
    priceLevel: '$$$',
    distance: '1.2 km',
    image: 'https://via.placeholder.com/300x200',
    tags: ['Pasta', 'Pizza', 'Wine'],
    lastVisited: '1 week ago',
  },
  {
    id: '3',
    name: 'Thai Spice',
    cuisine: 'Thai',
    rating: 4.5,
    priceLevel: '$$',
    distance: '2.0 km',
    image: 'https://via.placeholder.com/300x200',
    tags: ['Spicy', 'Thai', 'Asian'],
    lastVisited: '2 weeks ago',
  },
];

export default function FavoritesScreen() {
  const navigation = useNavigation();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const renderRestaurantCard = (restaurant: typeof MOCK_FAVORITES[0]) => (
    <Animated.View 
      key={restaurant.id}
      style={[styles.card, { opacity: fadeAnim }]}
    >
      <Image source={{ uri: restaurant.image }} style={styles.restaurantImage} />
      <View style={styles.cardContent}>
        <View style={styles.cardHeader}>
          <View>
            <Text style={styles.restaurantName}>{restaurant.name}</Text>
            <Text style={styles.cuisine}>{restaurant.cuisine}</Text>
          </View>
          <TouchableOpacity 
            style={styles.favoriteButton}
            onPress={() => {/* Handle unfavorite */}}
          >
            <Ionicons name="heart" size={24} color="#94B06B" />
          </TouchableOpacity>
        </View>

        <View style={styles.detailsRow}>
          <View style={styles.detail}>
            <Ionicons name="star" size={16} color="#94B06B" />
            <Text style={styles.detailText}>{restaurant.rating}</Text>
          </View>
          <View style={styles.detail}>
            <Ionicons name="wallet-outline" size={16} color="#94B06B" />
            <Text style={styles.detailText}>{restaurant.priceLevel}</Text>
          </View>
          <View style={styles.detail}>
            <Ionicons name="location-outline" size={16} color="#94B06B" />
            <Text style={styles.detailText}>{restaurant.distance}</Text>
          </View>
        </View>

        <View style={styles.tagsContainer}>
          {restaurant.tags.map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.lastVisited}>Last visited: {restaurant.lastVisited}</Text>
      </View>
    </Animated.View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.content}>
        <Text style={styles.title}>Your Favorites</Text>
        <Text style={styles.subtitle}>Restaurants you love</Text>

        <View style={styles.cardsContainer}>
          {MOCK_FAVORITES.map(restaurant => renderRestaurantCard(restaurant))}
        </View>
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
    padding: 16,
  },
  title: {
    fontSize: 28,
    fontFamily: 'Roboto-Bold',
    color: '#94B06B',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    fontFamily: 'Roboto',
    color: '#F4F7EE',
    marginBottom: 24,
    opacity: 0.9,
  },
  cardsContainer: {
    gap: 16,
  },
  card: {
    backgroundColor: '#192112',
    borderRadius: 16,
    overflow: 'hidden',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  restaurantImage: {
    width: '100%',
    height: 160,
  },
  cardContent: {
    padding: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  restaurantName: {
    fontSize: 20,
    fontFamily: 'Roboto-Bold',
    color: '#F4F7EE',
    marginBottom: 4,
  },
  cuisine: {
    fontSize: 14,
    fontFamily: 'Roboto',
    color: '#94B06B',
  },
  favoriteButton: {
    padding: 8,
  },
  detailsRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 12,
  },
  detail: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailText: {
    fontSize: 14,
    fontFamily: 'Roboto',
    color: '#F4F7EE',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  tag: {
    backgroundColor: '#334027',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 12,
  },
  tagText: {
    fontSize: 12,
    fontFamily: 'Roboto',
    color: '#94B06B',
  },
  lastVisited: {
    fontSize: 12,
    fontFamily: 'Roboto',
    color: '#F4F7EE',
    opacity: 0.7,
  },
}); 