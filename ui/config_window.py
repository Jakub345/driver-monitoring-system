"""
Moduł do konfiguracji parametrów systemu w czasie rzeczywistym.
"""
import cv2

class ConfigUI:
    def __init__(self, window_name="Konfiguracja"):
        """Inicjalizacja interfejsu konfiguracyjnego."""
        self.window_name = window_name
        
        # Utworzenie okna
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 400, 200)
        
        # Utworzenie suwaków
        cv2.createTrackbar("EAR Próg x100", self.window_name, 20, 50, lambda x: None)
        cv2.createTrackbar("Czas oczu (0.1s)", self.window_name, 20, 50, lambda x: None)
        cv2.createTrackbar("Ruch głowy", self.window_name, 50, 100, lambda x: None)
        
        # Przyciski (symulowane przez suwaki 0-1)
        cv2.createTrackbar("Kalibracja", self.window_name, 0, 1, lambda x: None)
        cv2.createTrackbar("Zapisz", self.window_name, 0, 1, lambda x: None)
        
        # Ostatnio odczytane wartości
        self.last_values = {
            'ear_threshold': 0.2,
            'eye_closed_time': 2.0,
            'head_movement_threshold': 50,
            'calibrate': False,
            'save': False
        }
    
    def get_changes(self):
        """Sprawdza czy nastąpiły zmiany w konfiguracji."""
        # Odczyt aktualnych wartości
        ear_threshold = cv2.getTrackbarPos("EAR Próg x100", self.window_name) / 100.0
        eye_closed_time = cv2.getTrackbarPos("Czas oczu (0.1s)", self.window_name) / 10.0
        head_movement_threshold = cv2.getTrackbarPos("Ruch głowy", self.window_name)
        calibrate = cv2.getTrackbarPos("Kalibracja", self.window_name) == 1
        save = cv2.getTrackbarPos("Zapisz", self.window_name) == 1
        
        # Sprawdzenie zmian
        changes = {}
        if ear_threshold != self.last_values['ear_threshold']:
            changes['ear_threshold'] = ear_threshold
            self.last_values['ear_threshold'] = ear_threshold

        if eye_closed_time != self.last_values['eye_closed_time']:
           changes['eye_closed_time'] = eye_closed_time
           self.last_values['eye_closed_time'] = eye_closed_time
           
        if head_movement_threshold != self.last_values['head_movement_threshold']:
            changes['head_movement_threshold'] = head_movement_threshold
            self.last_values['head_movement_threshold'] = head_movement_threshold
        
        # Obsługa przycisków
        if calibrate:
            changes['calibrate'] = True
            cv2.setTrackbarPos("Kalibracja", self.window_name, 0)
            
        if save:
            changes['save'] = True
            cv2.setTrackbarPos("Zapisz", self.window_name, 0)
        
        return changes if changes else None
    
    def close(self):
        """Zamyka okno konfiguracji."""
        cv2.destroyWindow(self.window_name)