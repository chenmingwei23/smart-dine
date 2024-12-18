import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, Image, TouchableOpacity, TextInput } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';

type ReviewsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Reviews'>;

// Mock data - replace with API call
const MOCK_REVIEWS = Array(10).fill(null).map((_, index) => ({
  id: index.toString(),
  restaurantName: "Restaurant " + (index + 1),
  rating: (Math.random() * 2 + 3).toFixed(1), // Random rating between 3-5
  reviewCount: Math.floor(Math.random() * 500),
  image: `https://picsum.photos/300/200?random=${index}`,
  cuisine: ['Japanese', 'Chinese', 'Thai', 'Italian', 'Indian'][Math.floor(Math.random() * 5)],
  priceLevel: ['$', '$$', '$$$'][Math.floor(Math.random() * 3)],
}));

export default function ReviewsScreen() {
  const navigation = useNavigation<ReviewsScreenNavigationProp>();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState<string | null>(null);

  const cuisineTypes = ['All', 'Japanese', 'Chinese', 'Thai', 'Italian', 'Indian'];

  const filteredReviews = MOCK_REVIEWS.filter(review => {
    const matchesSearch = review.restaurantName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCuisine = !selectedCuisine || selectedCuisine === 'All' || review.cuisine === selectedCuisine;
    return matchesSearch && matchesCuisine;
  });

  const renderReviewCard = ({ item }: { item: typeof MOCK_REVIEWS[0] }) => (
    <TouchableOpacity style={styles.card}>
      <Image source={{ uri: item.image }} style={styles.cardImage} />
      <View style={styles.cardContent}>
        <Text style={styles.restaurantName}>{item.restaurantName}</Text>
        <View style={styles.ratingContainer}>
          <Text style={styles.rating}>★ {item.rating}</Text>
          <Text style={styles.reviewCount}>({item.reviewCount})</Text>
        </View>
        <View style={styles.detailsRow}>
          <Text style={styles.cuisine}>{item.cuisine}</Text>
          <Text style={styles.price}>{item.priceLevel}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search restaurants..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <View style={styles.cuisineFilter}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={cuisineTypes}
          keyExtractor={(item) => item}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.cuisineButton,
                selectedCuisine === item && styles.selectedCuisine
              ]}
              onPress={() => setSelectedCuisine(item)}
            >
              <Text style={[
                styles.cuisineButtonText,
                selectedCuisine === item && styles.selectedCuisineText
              ]}>
                {item}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      <FlatList
        data={filteredReviews}
        renderItem={renderReviewCard}
        keyExtractor={item => item.id}
        numColumns={2}
        columnWrapperStyle={styles.columnWrapper}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 10,
  },
  searchContainer: {
    padding: 10,
  },
  searchInput: {
    backgroundColor: '#f5f5f5',
    padding: 10,
    borderRadius: 20,
    fontSize: 16,
  },
  cuisineFilter: {
    marginVertical: 10,
    height: 50,
  },
  cuisineButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    marginHorizontal: 5,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
  },
  selectedCuisine: {
    backgroundColor: '#FF6B6B',
  },
  cuisineButtonText: {
    color: '#666',
    fontSize: 14,
  },
  selectedCuisineText: {
    color: '#fff',
  },
  columnWrapper: {
    justifyContent: 'space-between',
  },
  card: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  cardImage: {
    width: '100%',
    height: 120,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
  },
  cardContent: {
    padding: 10,
  },
  restaurantName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  rating: {
    color: '#FFC107',
    marginRight: 5,
  },
  reviewCount: {
    color: '#666',
    fontSize: 12,
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cuisine: {
    color: '#666',
    fontSize: 12,
  },
  price: {
    color: '#4CAF50',
    fontSize: 12,
  },
}); 