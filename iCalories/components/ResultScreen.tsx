import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type ResultScreenProps = {
  carne: string;
  confidence: number;
};

export default function ResultScreen({ carne, confidence }: ResultScreenProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tipo de carne detectada:</Text>
      <Text style={styles.result}>{carne.toUpperCase()}</Text>
      <Text style={styles.confidence}>Confiança: {(confidence * 100).toFixed(1)}%</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#222',
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    color: '#fff',
    marginBottom: 16,
  },
  result: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1e90ff',
    marginBottom: 12,
  },
  confidence: {
    fontSize: 18,
    color: '#fff',
  },
});