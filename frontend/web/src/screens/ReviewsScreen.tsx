import React from 'react';
import { View, Text, StyleSheet, ScrollView, Image, TouchableOpacity, Animated } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const MOCK_REVIEWS = [
  {
    id: 1,
    userName: 'John D.',
    rating: 4.5,
    date: '2 days ago',
    content: 'Amazing sushi and great atmosphere! The service was excellent and the food came out quickly.',
    userImage: 'https://via.placeholder.com/40',
    helpful: 12,
  },
  {
    id: 2,
    userName: 'Sarah M.',
    rating: 5,
    date: '1 week ago',
    content: 'Best Japanese restaurant in town! The dragon roll was absolutely delicious. Will definitely come back!',
    userImage: 'https://via.placeholder.com/40',
    helpful: 8,
  },
  {
    id: 3,
    userName: 'Mike R.',
    rating: 4,
    date: '2 weeks ago',
    content: 'Good food and nice ambiance. Prices are a bit high but the quality makes up for it.',
    userImage: 'https://via.placeholder.com/40',
    helpful: 5,
  },
];

export default function ReviewsScreen() {
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const navigation = useNavigation();

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      useNativeDriver: true,
    }).start();
  }, []);

  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    return '★'.repeat(fullStars) + (hasHalfStar ? '½' : '');
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        <View style={styles.header}>
          <Text style={styles.title}>Reviews</Text>
          <Text style={styles.subtitle}>See what others are saying</Text>
        </View>

        <View style={styles.reviewsContainer}>
          {MOCK_REVIEWS.map((review) => (
            <View key={review.id} style={styles.reviewCard}>
              <View style={styles.reviewHeader}>
                <Image source={{ uri: review.userImage }} style={styles.userImage} />
                <View style={styles.reviewHeaderText}>
                  <Text style={styles.userName}>{review.userName}</Text>
                  <Text style={styles.reviewDate}>{review.date}</Text>
                </View>
                <Text style={styles.rating}>{renderStars(review.rating)}</Text>
              </View>
              
              <Text style={styles.reviewContent}>{review.content}</Text>
              
              <View style={styles.reviewFooter}>
                <TouchableOpacity style={styles.helpfulButton}>
                  <Text style={styles.helpfulButtonText}>Helpful ({review.helpful})</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </View>

        <TouchableOpacity 
          style={styles.writeReviewButton}
          activeOpacity={0.7}
        >
          <Text style={styles.writeReviewButtonText}>Write a Review</Text>
        </TouchableOpacity>
      </Animated.View>
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
    marginBottom: 24,
  },
  title: {
    fontFamily: 'Roboto-Bold',
    fontSize: 28,
    color: '#94B06B',
    marginBottom: 8,
  },
  subtitle: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#F4F7EE',
    opacity: 0.9,
  },
  reviewsContainer: {
    gap: 16,
  },
  reviewCard: {
    backgroundColor: '#192112',
    borderRadius: 16,
    padding: 16,
    gap: 12,
  },
  reviewHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  userImage: {
    width: 40,
    height: 40,
    borderRadius: 20,
    marginRight: 12,
  },
  reviewHeaderText: {
    flex: 1,
  },
  userName: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#F4F7EE',
  },
  reviewDate: {
    fontFamily: 'Roboto',
    fontSize: 14,
    color: '#E6EDDA',
    opacity: 0.8,
  },
  rating: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#94B06B',
  },
  reviewContent: {
    fontFamily: 'Roboto',
    fontSize: 15,
    color: '#F4F7EE',
    lineHeight: 22,
  },
  reviewFooter: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 8,
  },
  helpfulButton: {
    backgroundColor: '#334027',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 12,
  },
  helpfulButtonText: {
    fontFamily: 'Roboto',
    fontSize: 14,
    color: '#94B06B',
  },
  writeReviewButton: {
    backgroundColor: '#94B06B',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  writeReviewButtonText: {
    fontFamily: 'Roboto-Bold',
    fontSize: 16,
    color: '#192112',
    letterSpacing: 0.5,
  },
}); 