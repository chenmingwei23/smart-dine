import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated, Easing } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../navigation/types';
import { useStore } from '../store';

type SelectionScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Selection'>;

const CUISINES = ['Italian', 'Japanese', 'Chinese', 'Mexican', 'Indian', 'Thai', 'American', 'Mediterranean'];
const PRICE_RANGES = ['$', '$$', '$$$', '$$$$'];
const MOODS = ['Casual', 'Romantic', 'Family', 'Business'];
const DISTANCES = [1, 3, 5, 10, 15, 20];

export default function SelectionScreen() {
  const navigation = useNavigation<SelectionScreenNavigationProp>();
  const { selectionState, updateSelection, resetSelection } = useStore();
  const fadeAnim = React.useRef(new Animated.Value(0)).current;
  const titleAnim = React.useRef(new Animated.Value(0)).current;
  const scaleAnim = React.useRef(new Animated.Value(0.95)).current;
  const optionsAnim = React.useRef(CUISINES.map(() => new Animated.Value(0))).current;
  const moodsAnim = React.useRef(MOODS.map(() => new Animated.Value(0))).current;
  const pricesAnim = React.useRef(PRICE_RANGES.map(() => new Animated.Value(0))).current;
  const distancesAnim = React.useRef(DISTANCES.map(() => new Animated.Value(0))).current;

  React.useEffect(() => {
    // Sequence animations
    Animated.sequence([
      // First fade in the content
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 500,
          useNativeDriver: true,
        }),
      ]),
      // Then fade in the title
      Animated.timing(titleAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      // Then animate options
      Animated.stagger(50, optionsAnim.map(anim =>
        Animated.spring(anim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        })
      )),
    ]).start();
  }, []);

  React.useEffect(() => {
    if (selectionState.cuisine) {
      Animated.stagger(50, moodsAnim.map(anim =>
        Animated.spring(anim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        })
      )).start();
    }
  }, [selectionState.cuisine]);

  React.useEffect(() => {
    if (selectionState.mood) {
      Animated.stagger(50, pricesAnim.map(anim =>
        Animated.spring(anim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        })
      )).start();
    }
  }, [selectionState.mood]);

  React.useEffect(() => {
    if (selectionState.priceRange) {
      Animated.stagger(50, distancesAnim.map(anim =>
        Animated.spring(anim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        })
      )).start();
    }
  }, [selectionState.priceRange]);

  const handleSelection = (key: 'cuisine' | 'priceRange' | 'mood' | 'distance', value: any) => {
    // Create temporary animated value for selection effect
    const tempScale = new Animated.Value(1);
    Animated.sequence([
      Animated.spring(tempScale, {
        toValue: 1.2,
        tension: 200,
        friction: 2,
        useNativeDriver: true,
      }),
      Animated.spring(tempScale, {
        toValue: 1,
        tension: 200,
        friction: 10,
        useNativeDriver: true,
      }),
    ]).start();

    updateSelection(key, value);
    
    if (key === 'distance') {
      navigation.navigate('Result', { selections: selectionState });
    }
  };

  const renderQuestion = (title: string, isVisible: boolean = true) => (
    <Animated.Text 
      style={[
        styles.sectionTitle,
        {
          opacity: titleAnim,
          transform: [
            { translateY: titleAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [20, 0]
            })}
          ]
        }
      ]}
    >
      {title}
    </Animated.Text>
  );

  const renderOption = (option: string | number, index: number, type: 'cuisine' | 'mood' | 'price' | 'distance') => {
    const isSelected = selectionState[type === 'price' ? 'priceRange' : type] === option;
    const animValue = {
      cuisine: optionsAnim[index],
      mood: moodsAnim[index],
      price: pricesAnim[index],
      distance: distancesAnim[index],
    }[type];

    const optionStyle = {
      cuisine: styles.option,
      mood: styles.moodOption,
      price: styles.priceOption,
      distance: styles.distanceOption,
    }[type];

    return (
      <Animated.View
        key={option}
        style={{
          opacity: animValue,
          transform: [
            { scale: animValue },
            { translateY: animValue.interpolate({
              inputRange: [0, 1],
              outputRange: [50, 0],
            })},
          ],
        }}
      >
        <TouchableOpacity
          style={[
            optionStyle,
            isSelected && styles.selectedOption,
          ]}
          onPress={() => handleSelection(type === 'price' ? 'priceRange' : type, option)}
          activeOpacity={0.7}
        >
          <Text style={[
            styles.optionText,
            isSelected && styles.selectedOptionText,
          ]}>
            {type === 'distance' ? `${option} km` : option}
          </Text>
        </TouchableOpacity>
      </Animated.View>
    );
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
            {renderQuestion("What cuisine are you craving?")}
            <View style={styles.optionsGrid}>
              {CUISINES.map((cuisine, index) => renderOption(cuisine, index, 'cuisine'))}
            </View>
          </View>

          {selectionState.cuisine && (
            <View style={styles.section}>
              {renderQuestion("What's your dining mood?")}
              <View style={styles.moodContainer}>
                {MOODS.map((mood, index) => renderOption(mood, index, 'mood'))}
              </View>
            </View>
          )}

          {selectionState.mood && (
            <View style={styles.section}>
              {renderQuestion("What's your budget?")}
              <View style={styles.priceContainer}>
                {PRICE_RANGES.map((price, index) => renderOption(price, index, 'price'))}
              </View>
            </View>
          )}

          {selectionState.priceRange && (
            <View style={styles.section}>
              {renderQuestion("How far are you willing to travel?")}
              <View style={styles.distanceGrid}>
                {DISTANCES.map((distance, index) => renderOption(distance, index, 'distance'))}
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
    padding: 16,
    flex: 1,
  },
  section: {
    marginBottom: 40,
  },
  sectionTitle: {
    fontFamily: 'Roboto-Bold',
    fontSize: 24,
    color: '#94B06B',
    marginBottom: 24,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  optionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 24,
    paddingHorizontal: 16,
  },
  option: {
    width: 110,
    height: 110,
    backgroundColor: '#192112',
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    margin: 4,
  },
  selectedOption: {
    backgroundColor: '#94B06B',
    transform: [{scale: 1.05}],
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
  },
  optionText: {
    fontFamily: 'Roboto',
    fontSize: 15,
    color: '#E6EDDA',
    letterSpacing: 0.5,
    textAlign: 'center',
  },
  selectedOptionText: {
    fontFamily: 'Roboto-Bold',
    color: '#192112',
  },
  moodContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 24,
    paddingHorizontal: 16,
  },
  moodOption: {
    width: 130,
    height: 130,
    backgroundColor: '#192112',
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    margin: 4,
  },
  priceContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 24,
    paddingHorizontal: 16,
  },
  priceOption: {
    width: 90,
    height: 90,
    backgroundColor: '#192112',
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    margin: 4,
  },
  distanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 24,
    paddingHorizontal: 16,
  },
  distanceOption: {
    width: 110,
    height: 110,
    backgroundColor: '#192112',
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    margin: 4,
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