import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated } from 'react-native';
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

  React.useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);

  const handleSelection = (key: 'cuisine' | 'priceRange' | 'distance', value: any) => {
    updateSelection(key, value);
    
    // If all selections are made, navigate to results
    if (key === 'distance') {
      navigation.navigate('Result', { selections: selectionState });
    }
  };

  const renderCuisineSelection = () => (
    <Animated.View style={[styles.section, { opacity: fadeAnim }]}>
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
    </Animated.View>
  );

  const renderPriceSelection = () => (
    <Animated.View style={[styles.section, { opacity: fadeAnim }]}>
      <Text style={styles.sectionTitle}>What's your budget?</Text>
      <View style={styles.optionsRow}>
        {PRICE_RANGES.map((price) => (
          <TouchableOpacity
            key={price}
            style={[
              styles.priceOption,
              selectionState.priceRange === price && styles.selectedOption,
            ]}
            onPress={() => handleSelection('priceRange', price)}
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
    </Animated.View>
  );

  const renderDistanceSelection = () => (
    <Animated.View style={[styles.section, { opacity: fadeAnim }]}>
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
    </Animated.View>
  );

  return (
    <ScrollView style={styles.container}>
      {renderCuisineSelection()}
      {selectionState.cuisine && renderPriceSelection()}
      {selectionState.priceRange && renderDistanceSelection()}
      
      <TouchableOpacity 
        style={styles.resetButton}
        onPress={resetSelection}
      >
        <Text style={styles.resetButtonText}>Start Over</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  optionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  optionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 10,
  },
  option: {
    width: '48%',
    padding: 15,
    marginBottom: 15,
    borderRadius: 10,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
  },
  priceOption: {
    width: 70,
    height: 70,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 35,
    backgroundColor: '#f5f5f5',
  },
  selectedOption: {
    backgroundColor: '#FF6B6B',
  },
  optionText: {
    fontSize: 16,
    color: '#333',
  },
  selectedOptionText: {
    color: '#fff',
  },
  resetButton: {
    margin: 20,
    padding: 15,
    backgroundColor: '#f0f0f0',
    borderRadius: 10,
    alignItems: 'center',
  },
  resetButtonText: {
    color: '#FF6B6B',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 