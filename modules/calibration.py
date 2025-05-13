"""
Moduł do kalibracji systemu.
"""
import cv2
import time
import numpy as np

class Calibrator:
    def __init__(self, cap, face_detector, duration=5):
        self.cap = cap
        self.face_detector = face_detector
        self.duration = duration
    
    def calibrate(self):
        """Kalibruje system dla aktualnego użytkownika."""
        print("Rozpoczynam kalibrację. Proszę patrzeć prosto w kamerę przez 5 sekund...")
        
        eye_counts = []
        face_centers = []
        
        start_time = time.time()
        while time.time() - start_time < self.duration:
            # Odczyt klatki
            success, frame = self.cap.read()
            if not success:
                continue
            
            # Odbicie lustrzane
            frame = cv2.flip(frame, 1)
            
            # Detekcja twarzy i oczu
            result = self.face_detector.detect(frame)
            
            if result['face_detected']:
                # Zapisanie liczby oczu
                eye_counts.append(result['eye_count'])
                
                # Zapisanie pozycji twarzy
                x, y, w, h = result['face']
                face_centers.append((x + w//2, y + h//2))
            
            # Wyświetlanie pozostałego czasu
            remaining = int(self.duration - (time.time() - start_time))
            cv2.putText(frame, f"Kalibracja: {remaining}s", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Wyświetlanie obrazu
            cv2.imshow('Kalibracja systemu', frame)
            cv2.waitKey(1)
        
        # Obliczenie nowych progów
        if len(eye_counts) > 0:
            # Średnia liczba oczu
            avg_eye_count = sum(eye_counts) / len(eye_counts)
            
            # Ustalamy próg EAR na podstawie liczby oczu
            # Prosta heurystyka: jeśli średnio wykryto 2 oczy, EAR = 0.25
            # Jeśli wykryto mniej, proporcjonalnie mniej
            ear_threshold = min(0.25, avg_eye_count * 0.125)
            
            # Ustalamy pozycję odniesienia dla głowy
            base_face_center = None
            if len(face_centers) > 0:
                base_face_center = face_centers[-1]  # Ostatnia pozycja jako referencyjna
            
            print(f"Kalibracja zakończona. Nowy próg EAR: {ear_threshold:.3f}")
            
            return {
                'ear_threshold': ear_threshold,
                'base_face_center': base_face_center
            }
        else:
            print("Kalibracja nie powiodła się. Używanie domyślnych wartości.")
            return None