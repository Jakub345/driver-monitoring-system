"""
Moduł do śledzenia pozycji głowy.
"""
import numpy as np
from modules.temporal_filter import TemporalFilter

class HeadTracker:
    def __init__(self, movement_threshold=50):
        self.movement_threshold = movement_threshold
        self.face_center_history = []
        self.movement_filter = TemporalFilter(size=3)
    
    def track(self, face_result):
        """Śledzi pozycję głowy i wykrywa znaczne ruchy."""
        if not face_result['face_detected']:
            return {
                'head_distracted': False,
                'movement': 0,
                'filtered_movement': 0
            }
        
        # Pobierz aktualną twarz
        x, y, w, h = face_result['face']
        face_center = (x + w//2, y + h//2)
        
        # Dodaj do historii
        self.face_center_history.append(face_center)
        
        # Ograniczenie długości historii
        if len(self.face_center_history) > 10:
            self.face_center_history.pop(0)
        
        # Jeśli nie mamy wystarczająco dużo historii
        if len(self.face_center_history) <= 1:
            return {
                'head_distracted': False,
                'movement': 0,
                'filtered_movement': 0
            }
        
        # Obliczenie przesunięcia względem pierwszego punktu w historii
        base_center = self.face_center_history[0]
        current_center = self.face_center_history[-1]
        
        dx = current_center[0] - base_center[0]
        dy = current_center[1] - base_center[1]
        
        # Obliczenie wielkości przesunięcia
        movement = np.sqrt(dx**2 + dy**2)
        
        # Filtrowanie ruchu
        filtered_movement = self.movement_filter.update(movement)
        
        # Określenie czy głowa jest odchylona
        head_distracted = filtered_movement > self.movement_threshold
        
        return {
            'head_distracted': head_distracted,
            'movement': movement,
            'filtered_movement': filtered_movement,
            'dx': dx,
            'dy': dy,
            'base_center': base_center,
            'current_center': current_center
        }
    
    def set_movement_threshold(self, threshold):
        """Ustawia próg ruchu głowy."""
        self.movement_threshold = threshold