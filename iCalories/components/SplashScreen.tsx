import React from 'react';
import { View, Image, StyleSheet } from 'react-native';

const SplashScreen = () => (
  <View style={styles.container}>
    <Image
      source={require('../images/splashscreen.png')}
      style={styles.image}
      resizeMode="cover"
    />
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  image: {
    width: '100%',
    height: '100%',
  },
});

export default SplashScreen;
