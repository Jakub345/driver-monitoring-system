"""
Moduł implementujący filtry temporalne.
"""
import numpy as np

class TemporalFilter:
    def __init__(self, size=5, alpha=0.3):
        """
        Filtr do wygładzania danych w czasie.
        
        Args:
            size: Rozmiar bufora historii
            alpha: Współczynnik dla filtra EWMA (Exponentially Weighted Moving Average)
        """
        self.buffer = []
        self.size = size
        self.alpha = alpha
    
    def update(self, value):
        """
        Aktualizuje filtr nową wartością.
        
        Args:
            value: Nowa wartość do filtrowania
            
        Returns:
            float: Filtrowana wartość
        """
        # Dodanie nowej wartości do bufora
        self.buffer.append(value)
        
        # Ograniczenie rozmiaru bufora
        if len(self.buffer) > self.size:
            self.buffer.pop(0)
        
        # Średnia z bufora
        avg_value = sum(self.buffer) / len(self.buffer)
        
        # Możemy również zaimplementować filtr EWMA (Exponentially Weighted Moving Average)
        # jeśli potrzebujemy bardziej responsywnego filtrowania
        if len(self.buffer) > 1:
            ewma = self.alpha * value + (1 - self.alpha) * self.buffer[-2]
            # Możemy użyć ewma zamiast avg_value
        
        return avg_value