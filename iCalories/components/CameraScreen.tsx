import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View, Image, Alert } from 'react-native';
import * as MediaLibrary from 'expo-media-library';
import * as FileSystem from 'expo-file-system';

export default function CameraScreen() {
  const [facing, setFacing] = useState<CameraType>('back');
  const [permission, requestPermission] = useCameraPermissions();
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [takePhoto, setTakePhoto] = useState(false);

  if (!permission) {
    return <View style={styles.container}><Text style={styles.message}>Carregando permissões...</Text></View>;
  }
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>Precisamos da sua permissão para mostrar a câmera</Text>
        <Button onPress={requestPermission} title="Conceder permissão" />
      </View>
    );
  }

  async function sendPhotoToBackend(photoUri: string) {
    const API_URL = 'http://192.168.1.30:8000/predict'; // Troque pelo IP do seu backend
    const formData = new FormData();
    formData.append('file', {
      uri: photoUri,
      name: 'photo.jpg',
      type: 'image/jpeg',
    } as any);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      const result = await response.json();
      Alert.alert('Resultado', `Classe: ${result.class}\nConfiança: ${result.confidence}`);
    } catch (e) {
      Alert.alert('Erro', 'Não foi possível enviar a imagem.');
    }
  }

  function handlePhotoCaptured(photo: { uri: string }) {
    setPhotoUri(photo.uri);
    MediaLibrary.createAssetAsync(photo.uri);
    sendPhotoToBackend(photo.uri);
    Alert.alert('Foto salva!', 'A foto foi salva na galeria.');
  }

  function handleTakePhoto() {
    setTakePhoto(true);
    setTimeout(() => setTakePhoto(false), 100); // Reset flag
  }

  function toggleCameraFacing() {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

  return (
    <View style={styles.container}>
      {!photoUri ? (
        <>
          <CameraView
            style={styles.camera}
            facing={facing}
            photo={takePhoto}
            onPhotoCaptured={handlePhotoCaptured}
          />
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={[styles.button, styles.flipButton]} onPress={toggleCameraFacing}>
              <Text style={styles.buttonText}>Flip</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.button, styles.captureButton]} onPress={handleTakePhoto}>
              <Text style={styles.buttonText}>Tirar foto</Text>
            </TouchableOpacity>
          </View>
        </>
      ) : (
        <>
          <Image source={{ uri: photoUri }} style={styles.preview} />
          <Text style={{ color: 'white', margin: 20 }}>Foto salva na galeria!</Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    backgroundColor: '#000',
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
    color: 'white',
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    position: 'absolute',
    bottom: 64,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    width: '100%',
    paddingHorizontal: 64,
  },
  button: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 10,
    paddingVertical: 16,
    borderRadius: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  flipButton: {
    backgroundColor: '#222',
  },
  captureButton: {
    backgroundColor: '#1e90ff',
  },
  buttonText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    letterSpacing: 1,
  },
  preview: {
    flex: 1,
    width: '100%',
    resizeMode: 'contain',
  },
});