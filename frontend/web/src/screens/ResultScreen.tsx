import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
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
  const { currentRestaurant, setCurrentRestaurant } = useStore();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const scaleAnim = React.useRef(new Animated.Value(0.95)).current;

  useEffect(() => {
    // Mock data
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

    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  if (!currentRestaurant) {
    return (
      <View style={styles.container}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <Animated.View 
          style={[
            styles.content,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }],
            }
          ]}
        >
          <View style={styles.header}>
            <Text style={styles.title}>Perfect Match!</Text>
            <Text style={styles.subtitle}>Based on your preferences</Text>
          </View>

          <View style={styles.resultCard}>
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
                <View style={[
                  styles.statusIndicator,
                  { backgroundColor: currentRestaurant.openNow ? '#94B06B' : '#FF4444' }
                ]} />
                <Text style={styles.statusText}>
                  {currentRestaurant.openNow ? 'Open Now' : 'Closed'}
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.buttonsContainer}>
            <TouchableOpacity 
              style={styles.mainButton}
              activeOpacity={0.7}
            >
              <Text style={styles.buttonText}>Let's Go!</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.secondaryButton}
              onPress={() => navigation.navigate('Selection')}
              activeOpacity={0.7}
            >
              <Text style={styles.secondaryButtonText}>Try Again</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity 
            style={styles.reviewsButton}
            onPress={() => navigation.navigate('Reviews')}
            activeOpacity={0.7}
          >
            <Text style={styles.reviewsButtonText}>See All Reviews</Text>
          </TouchableOpacity>
        </Animated.View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#334027',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  loadingText: {
    fontFamily: 'Roboto',
    color: '#F4F7EE',
    fontSize: 16,
    textAlign: 'center',
    marginTop: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontFamily: 'Roboto-Bold',
    fontSize: 32,
    color: '#94B06B',
    marginBottom: 8,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  subtitle: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#F4F7EE',
    textAlign: 'center',
    opacity: 0.9,
  },
  resultCard: {
    borderRadius: 20,
    overflow: 'hidden',
    backgroundColor: '#192112',
    marginBottom: 24,
  },
  restaurantImage: {
    width: '100%',
    height: 200,
  },
  restaurantInfo: {
    padding: 20,
  },
  restaurantName: {
    fontFamily: 'Roboto-Bold',
    fontSize: 24,
    color: '#F4F7EE',
    marginBottom: 4,
  },
  cuisine: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#E6EDDA',
    opacity: 0.9,
    marginBottom: 12,
  },
  detailsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  rating: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#94B06B',
    marginRight: 16,
  },
  price: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#F4F7EE',
    marginRight: 16,
  },
  distance: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#E6EDDA',
    opacity: 0.9,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
    gap: 8,
  },
  tag: {
    backgroundColor: '#334027',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  tagText: {
    fontFamily: 'Roboto',
    fontSize: 14,
    color: '#94B06B',
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontFamily: 'Roboto',
    fontSize: 14,
    color: '#E6EDDA',
    opacity: 0.9,
  },
  buttonsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
  },
  mainButton: {
    flex: 1,
    backgroundColor: '#94B06B',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#192112',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  buttonText: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#192112',
    letterSpacing: 0.5,
  },
  secondaryButtonText: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#E6EDDA',
    letterSpacing: 0.5,
  },
  reviewsButton: {
    alignSelf: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  reviewsButtonText: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#94B06B',
    textDecorationLine: 'underline',
  },
}); 