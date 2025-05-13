"""
Moduł do detekcji senności kierowcy.
"""
import time
from modules.temporal_filter import TemporalFilter

class DrowsinessDetector:
    def __init__(self, ear_threshold=0.2, eye_closed_time_threshold=2.0):
        self.ear_threshold = ear_threshold
        self.eye_closed_time_threshold = eye_closed_time_threshold
        
        # Stan
        self.eye_closed_start_time = None
        self.eyes_closed = False
        
        # Filtr dla EAR
        self.ear_filter = TemporalFilter(size=5)
        
        # Monitorowanie PERCLOS
        self.perclos_monitor = PerclosMonitor(window_size=60, threshold=self.ear_threshold)
    
    def detect(self, face_result, head_result):
        """Wykrywa senność na podstawie stanu oczu i głowy."""
        # Jeśli nie wykryto twarzy
        if not face_result['face_detected']:
            return {
                'eyes_closed': False,
                'perclos': 0,
                'drowsiness_score': 0,
                'alert_level': 0
            }
        
        # Pobranie liczby oczu
        filtered_eye_count = face_result['filtered_eye_count']
        
        # Symulacja EAR na podstawie liczby oczu
        # W rzeczywistości powinniśmy używać punktów charakterystycznych dlib
        # do dokładnego obliczenia EAR
        estimated_ear = min(0.3, filtered_eye_count * 0.15)
        
        # Filtrowanie EAR
        ear = self.ear_filter.update(estimated_ear)
        
        # Aktualizacja PERCLOS
        current_time = time.time()
        perclos = self.perclos_monitor.update(ear, current_time)
        
        # Określenie czy oczy są zamknięte
        if ear < self.ear_threshold:
            if self.eye_closed_start_time is None:
                self.eye_closed_start_time = current_time
            elif current_time - self.eye_closed_start_time > self.eye_closed_time_threshold:
                self.eyes_closed = True
        else:
            self.eye_closed_start_time = None
            self.eyes_closed = False
        
        # Obliczenie współczynnika senności
        # Kombinacja kilku wskaźników dla dokładniejszego wyniku
        drowsiness_score = 0.4 * perclos + 0.4 * (1.0 if self.eyes_closed else 0.0) + 0.2 * (1.0 if head_result['head_distracted'] else 0.0)
        
        # Określenie poziomu alertu
        alert_level = 0  # Normalny
        if drowsiness_score > 0.7:
            alert_level = 3  # Krytyczny
        elif drowsiness_score > 0.5:
            alert_level = 2  # Alert
        elif drowsiness_score > 0.3:
            alert_level = 1  # Ostrzeżenie
        
        return {
            'ear': ear,
            'eyes_closed': self.eyes_closed,
            'perclos': perclos,
            'drowsiness_score': drowsiness_score,
            'alert_level': alert_level,
            'eye_closed_duration': current_time - self.eye_closed_start_time if self.eye_closed_start_time else 0
        }
    
    def set_ear_threshold(self, threshold):
        """Ustawia próg EAR."""
        self.ear_threshold = threshold
        self.perclos_monitor.set_threshold(threshold)


class PerclosMonitor:
    def __init__(self, window_size=60, threshold=0.2):
        """Monitoruje procent czasu z zamkniętymi oczami w oknie czasowym."""
        self.window_size = window_size  # Okno w sekundach
        self.threshold = threshold      # Próg EAR dla zamkniętych oczu
        self.eye_states = []            # Historia stanów oczu
        self.timestamps = []            # Znaczniki czasu
    
    def update(self, ear, timestamp):
        """Aktualizuje historię i oblicza PERCLOS."""
        # Dodanie nowego stanu oka
        eye_closed = ear < self.threshold
        self.eye_states.append(eye_closed)
        self.timestamps.append(timestamp)
        
        # Usunięcie starych danych spoza okna czasowego
        while self.timestamps and timestamp - self.timestamps[0] > self.window_size:
            self.eye_states.pop(0)
            self.timestamps.pop(0)
        
        # Obliczenie PERCLOS - procent czasu z zamkniętymi oczami
        if self.eye_states:
            perclos = sum(self.eye_states) / len(self.eye_states)
            return perclos
        return 0
    
    def set_threshold(self, threshold):
        """Ustawia próg EAR."""
        self.threshold = threshold