"""
Konfiguracja parametrów systemu.
"""
import cv2
class Config:
    def __init__(self):
        # Parametry detekcji oczu
        self.ear_threshold = 0.2  # Próg Eye Aspect Ratio (EAR)
        self.eye_closed_time_threshold = 2.0  # Czas w sekundach
        
        # Parametry śledzenia głowy
        self.head_movement_threshold = 50  # Piksele
        
        # Parametry senności
        self.perclos_window = 60  # Okno PERCLOS w sekundach
        self.drowsiness_threshold = 0.4  # Próg senności
        
        # Ustawienia ogólne
        self.perform_calibration = False  # Czy wykonać kalibrację na starcie
        self.generate_report = True  # Czy generować raport po zamknięciu
        
        # Ścieżki do klasyfikatorów
        self.face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'