import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';
import { useStore } from '../store';

type SelectionScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Selection'>;

const CUISINES = ['Italian', 'Japanese', 'Chinese', 'Mexican', 'Indian', 'Thai', 'American', 'Mediterranean'];
const PRICE_RANGES = ['$', '$$', '$$$', '$$$$'];
const DISTANCES = [1, 3, 5, 10, 15, 20];

export default function SelectionScreen() {
  const navigation = useNavigation<SelectionScreenNavigationProp>();
  const { selectionState, updateSelection, resetSelection } = useStore();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const scaleAnim = React.useRef(new Animated.Value(0.95)).current;

  React.useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const handleSelection = (key: 'cuisine' | 'priceRange' | 'distance', value: any) => {
    updateSelection(key, value);
    
    if (key === 'distance') {
      navigation.navigate('Result', { selections: selectionState });
    }
  };

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
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>What cuisine are you craving?</Text>
            <View style={styles.optionsGrid}>
              {CUISINES.map((cuisine) => (
                <TouchableOpacity
                  key={cuisine}
                  style={[
                    styles.option,
                    selectionState.cuisine === cuisine && styles.selectedOption,
                  ]}
                  onPress={() => handleSelection('cuisine', cuisine)}
                  activeOpacity={0.7}
                >
                  <Text style={[
                    styles.optionText,
                    selectionState.cuisine === cuisine && styles.selectedOptionText,
                  ]}>
                    {cuisine}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {selectionState.cuisine && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>What's your budget?</Text>
              <View style={styles.priceContainer}>
                {PRICE_RANGES.map((price) => (
                  <TouchableOpacity
                    key={price}
                    style={[
                      styles.priceOption,
                      selectionState.priceRange === price && styles.selectedOption,
                    ]}
                    onPress={() => handleSelection('priceRange', price)}
                    activeOpacity={0.7}
                  >
                    <Text style={[
                      styles.optionText,
                      selectionState.priceRange === price && styles.selectedOptionText,
                    ]}>
                      {price}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}

          {selectionState.priceRange && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>How far are you willing to travel?</Text>
              <View style={styles.optionsGrid}>
                {DISTANCES.map((distance) => (
                  <TouchableOpacity
                    key={distance}
                    style={[
                      styles.option,
                      selectionState.distance === distance && styles.selectedOption,
                    ]}
                    onPress={() => handleSelection('distance', distance)}
                    activeOpacity={0.7}
                  >
                    <Text style={[
                      styles.optionText,
                      selectionState.distance === distance && styles.selectedOptionText,
                    ]}>
                      {distance} km
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}
        </Animated.View>

        <TouchableOpacity 
          style={styles.resetButton}
          onPress={resetSelection}
          activeOpacity={0.7}
        >
          <Text style={styles.resetButtonText}>Start Over</Text>
        </TouchableOpacity>
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
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontFamily: 'Roboto-Bold',
    fontSize: 24,
    color: '#94B06B',
    marginBottom: 20,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  optionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: 12,
  },
  option: {
    width: '48%',
    backgroundColor: '#192112',
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
  },
  selectedOption: {
    backgroundColor: '#94B06B',
  },
  optionText: {
    fontFamily: 'Roboto',
    fontSize: 16,
    color: '#E6EDDA',
    letterSpacing: 0.5,
  },
  selectedOptionText: {
    fontFamily: 'Roboto-Bold',
    color: '#192112',
  },
  priceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    gap: 12,
  },
  priceOption: {
    width: 70,
    height: 70,
    backgroundColor: '#192112',
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  resetButton: {
    alignSelf: 'center',
    paddingVertical: 12,
    paddingHorizontal: 24,
    marginVertical: 20,
  },
  resetButtonText: {
    fontFamily: 'Roboto',
    color: '#94B06B',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
}); 