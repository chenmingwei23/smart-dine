import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, Animated } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';
import { useStore } from '../store';

type ResultScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Result'>;

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

export default function ResultScreen() {
  const navigation = useNavigation<ResultScreenNavigationProp>();
  const { currentRestaurant, setCurrentRestaurant, selectionState } = useStore();
  
  // Animation values
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const slideAnim = React.useRef(new Animated.Value(50)).current;

  useEffect(() => {
    // Fetch restaurant data based on selections
    // For now using mock data
    setCurrentRestaurant({
      name: "Sushi Paradise",
      cuisine: "Japanese",
      rating: 4.5,
      priceLevel: "$$",
      distance: "0.8 km",
      image: "https://via.placeholder.com/300x200",
      tags: ["Popular", "Trending", "Healthy"],
      openNow: true,
    });

    // Start animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(slideAnim, {
        toValue: 0,
        speed: 12,
        bounciness: 8,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  if (!currentRestaurant) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Animated.View style={[styles.header, { opacity: fadeAnim }]}>
        <Text style={styles.title}>Perfect Match!</Text>
        <Text style={styles.subtitle}>Based on your preferences</Text>
      </Animated.View>

      <Animated.View 
        style={[
          styles.resultCard,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          }
        ]}
      >
        <Image
          source={{ uri: currentRestaurant.image }}
          style={styles.restaurantImage}
        />
        <View style={styles.restaurantInfo}>
          <Text style={styles.restaurantName}>{currentRestaurant.name}</Text>
          <Text style={styles.cuisine}>{currentRestaurant.cuisine}</Text>
          
          <View style={styles.detailsRow}>
            <Text style={styles.rating}>★ {currentRestaurant.rating}</Text>
            <Text style={styles.price}>{currentRestaurant.priceLevel}</Text>
            <Text style={styles.distance}>{currentRestaurant.distance}</Text>
          </View>

          <View style={styles.tagsContainer}>
            {currentRestaurant.tags.map((tag: string, index: number) => (
              <View key={index} style={styles.tag}>
                <Text style={styles.tagText}>{tag}</Text>
              </View>
            ))}
          </View>

          <View style={styles.statusContainer}>
            <View style={[styles.statusIndicator, { backgroundColor: currentRestaurant.openNow ? '#4CAF50' : '#F44336' }]} />
            <Text style={styles.statusText}>{currentRestaurant.openNow ? 'Open Now' : 'Closed'}</Text>
          </View>
        </View>
      </Animated.View>

      <Animated.View 
        style={[
          styles.buttonsContainer,
          {
            opacity: fadeAnim,
            transform: [{ translateY: slideAnim }],
          }
        ]}
      >
        <TouchableOpacity 
          style={[styles.button, styles.primaryButton]}
          onPress={() => {/* Add reservation/navigation logic */}}
        >
          <Text style={styles.buttonText}>Let's Go!</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.button, styles.secondaryButton]}
          onPress={() => navigation.navigate('Selection')}
        >
          <Text style={[styles.buttonText, styles.secondaryButtonText]}>Try Again</Text>
        </TouchableOpacity>
      </Animated.View>

      <Animated.View style={{ opacity: fadeAnim }}>
        <TouchableOpacity 
          style={styles.reviewsButton}
          onPress={() => navigation.navigate('Reviews')}
        >
          <Text style={styles.reviewsButtonText}>See All Reviews</Text>
        </TouchableOpacity>
      </Animated.View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  resultCard: {
    margin: 20,
    backgroundColor: '#fff',
    borderRadius: 15,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  restaurantImage: {
    width: '100%',
    height: 200,
    borderTopLeftRadius: 15,
    borderTopRightRadius: 15,
  },
  restaurantInfo: {
    padding: 15,
  },
  restaurantName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  cuisine: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  detailsRow: {
    flexDirection: 'row',
    marginTop: 10,
    alignItems: 'center',
  },
  rating: {
    fontSize: 16,
    color: '#FFC107',
    marginRight: 15,
  },
  price: {
    fontSize: 16,
    color: '#4CAF50',
    marginRight: 15,
  },
  distance: {
    fontSize: 16,
    color: '#666',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 15,
  },
  tag: {
    backgroundColor: '#F5F5F5',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
  },
  tagText: {
    fontSize: 14,
    color: '#666',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 15,
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#666',
  },
  buttonsContainer: {
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 25,
    marginHorizontal: 10,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#FF6B6B',
  },
  secondaryButton: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#FF6B6B',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButtonText: {
    color: '#FF6B6B',
  },
  reviewsButton: {
    padding: 15,
    alignItems: 'center',
    marginBottom: 20,
  },
  reviewsButtonText: {
    color: '#666',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
}); 