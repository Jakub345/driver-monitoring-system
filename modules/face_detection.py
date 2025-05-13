"""
Moduł odpowiedzialny za detekcję twarzy i oczu.
"""
import cv2
import numpy as np
from modules.temporal_filter import TemporalFilter

class FaceDetector:
    def __init__(self, face_cascade_path=None, eye_cascade_path=None):
        # Wczytanie klasyfikatorów
        if face_cascade_path:
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
        else:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if eye_cascade_path:
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        else:
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Filtr temporalny dla liczby oczu
        self.eye_count_filter = TemporalFilter(size=5)
    
    def detect(self, image):
        """Wykrywa twarz i oczy na obrazie."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
        
        # Detekcja twarzy
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Jeśli nie wykryto twarzy
        if len(faces) == 0:
            return {
                'face_detected': False,
                'face': None,
                'eyes': [],
                'eye_count': 0,
                'filtered_eye_count': 0
            }
        
        # Wybierz największą twarz
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Region twarzy do wykrywania oczu
        roi_gray = gray[y:y+h, x:x+w]
        
        # Detekcja oczu
        eyes = self.eye_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        # Filtrowanie oczu
        valid_eyes = self._filter_eyes(eyes, h)
        eye_count = len(valid_eyes)
        
        # Filtrowanie temporalne liczby oczu
        filtered_eye_count = self.eye_count_filter.update(eye_count)
        
        return {
            'face_detected': True,
            'face': face,
            'eyes': valid_eyes,
            'eye_count': eye_count,
            'filtered_eye_count': filtered_eye_count
        }
    
    def _filter_eyes(self, eyes, face_height):
        """Filtruje wykryte oczy, wybierając najbardziej wiarygodne."""
        if len(eyes) == 0:
            return []
        
        # Sortowanie według rozmiaru (większe są bardziej wiarygodne)
        eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)
        
        # Wybieranie maksymalnie 2 największych oczu
        eyes = eyes[:2] if len(eyes) > 2 else eyes
        
        # Filtrowanie na podstawie położenia w górnej części twarzy
        upper_eyes = [eye for eye in eyes if eye[1] < face_height/2]
        
        # Jeśli mamy przynajmniej jedno oko w górnej części, używamy tylko ich
        if len(upper_eyes) >= 1:
            return upper_eyes
        
        # W przeciwnym razie używamy wszystkich oczu
        return eyes