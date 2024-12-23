import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

export default function HomeScreen() {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const scaleAnim = React.useRef(new Animated.Value(0.95)).current;

  React.useEffect(() => {
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

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.content,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
          },
        ]}
      >
        <View style={styles.titleContainer}>
          <Text style={styles.title}>SmartDine</Text>
          <Text style={styles.subtitle}>Find your perfect dining spot</Text>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.startButton}
            onPress={() => navigation.navigate('Selection')}
            activeOpacity={0.7}
          >
            <Text style={styles.startButtonText}>Start Selection</Text>
          </TouchableOpacity>

          <View style={styles.secondaryButtons}>
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => navigation.navigate('Reviews')}
              activeOpacity={0.7}
            >
              <Text style={styles.secondaryButtonText}>Reviews</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => navigation.navigate('Profile')}
              activeOpacity={0.7}
            >
              <Text style={styles.secondaryButtonText}>Profile</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#334027',
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    padding: 20,
  },
  titleContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontFamily: 'Roboto-Bold',
    fontSize: 48,
    color: '#94B06B',
    marginBottom: 12,
    letterSpacing: 1,
  },
  subtitle: {
    fontFamily: 'Roboto',
    fontSize: 18,
    color: '#F4F7EE',
    opacity: 0.9,
    letterSpacing: 0.5,
  },
  buttonContainer: {
    gap: 20,
  },
  startButton: {
    backgroundColor: '#94B06B',
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  startButtonText: {
    fontFamily: 'Roboto-Bold',
    fontSize: 18,
    color: '#192112',
    letterSpacing: 0.5,
  },
  secondaryButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: '#192112',
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
  },
  secondaryButtonText: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#E6EDDA',
    letterSpacing: 0.5,
  },
}); 