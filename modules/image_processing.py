"""
Moduł do przetwarzania obrazu.
"""
import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass
    
    def process(self, image):
        """Przetwarza obraz do detekcji twarzy i oczu."""
        # Konwersja do skali szarości
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) > 2 else image
        
        # Sprawdzenie jasności obrazu
        brightness = np.mean(gray)
        
        # Korekta obrazu w zależności od jasności
        if brightness < 80:  # Ciemny obraz
            # Wyrównanie histogramu dla lepszego kontrastu
            gray = cv2.equalizeHist(gray)
        elif brightness > 200:  # Bardzo jasny obraz
            # Redukcja jasności
            gray = cv2.convertScaleAbs(gray, alpha=0.8, beta=0)
        
        return gray
    
    def enhance_visualization(self, image):
        """Ulepsza obraz do wizualizacji (nie wpływa na detekcję)."""
        # Konwersja do HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Sprawdzenie jasności
        brightness = np.mean(v)
        
        # Korekta jasności dla lepszej wizualizacji
        if brightness < 100:  # Zbyt ciemny
            # Zwiększenie jasności
            v = cv2.add(v, 30)
        elif brightness > 200:  # Zbyt jasny
            # Zmniejszenie jasności
            v = cv2.subtract(v, 30)
        
        # Łączenie kanałów
        hsv = cv2.merge([h, s, v])
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return enhanced