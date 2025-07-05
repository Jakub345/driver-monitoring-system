"""
Moduł do wizualizacji danych i rysowania na obrazie.
"""
import cv2
import numpy as np

class Visualizer:
    def __init__(self):
        """Inicjalizacja wizualizatora."""
        # Historia danych do wykresów
        self.ear_history = []
        self.drowsiness_history = []
        self.max_history = 100
    
    def draw_face_info(self, image, face_result):
        """Rysuje informacje o twarzy i oczach na obrazie."""
        if not face_result['face_detected']:
            return image
        
        result_image = image.copy()
        
        # Pobierz dane twarzy
        x, y, w, h = face_result['face']
        
        # Rysowanie prostokąta wokół twarzy
        cv2.rectangle(result_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Rysowanie oczu
        for (ex, ey, ew, eh) in face_result['eyes']:
            cv2.rectangle(result_image, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
        
        # Wyświetlanie liczby oczu
        cv2.putText(result_image, f"Oczy: {face_result['filtered_eye_count']:.1f}/{face_result['eye_count']}", 
                   (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return result_image
    
    def draw_head_info(self, image, head_result):
        """Rysuje informacje o ruchu głowy na obrazie."""
        result_image = image.copy()
        
        # Jeśli śledzenie głowy jest aktywne
        if 'base_center' in head_result and 'current_center' in head_result:
            # Rysowanie linii ruchu głowy
            if head_result['head_distracted']:
                cv2.line(result_image, 
                        head_result['base_center'], 
                        head_result['current_center'], 
                        (0, 0, 255), 2)
            
            # Wyświetlanie informacji o ruchu
            movement_text = f"Ruch: {head_result['filtered_movement']:.1f}"
            cv2.putText(result_image, movement_text, (30, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Alert o odchyleniu głowy
            if head_result['head_distracted']:
                cv2.putText(result_image, "UWAGA: RUCH GLOWY!", (30, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        return result_image
    
    def draw_drowsiness_info(self, image, drowsiness_result):
        """Rysuje informacje o senności na obrazie."""
        result_image = image.copy()
        
        # Wyświetlanie EAR
        if 'ear' in drowsiness_result:
            ear_text = f"EAR: {drowsiness_result['ear']:.2f}"
            cv2.putText(result_image, ear_text, (30, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Dodaj do historii
            self.ear_history.append(drowsiness_result['ear'])
            if len(self.ear_history) > self.max_history:
                self.ear_history.pop(0)
        
        # Wyświetlanie PERCLOS
        if 'perclos' in drowsiness_result:
            perclos_text = f"PERCLOS: {drowsiness_result['perclos']:.2f}"
            cv2.putText(result_image, perclos_text, (200, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Alert o zamkniętych oczach
        if drowsiness_result.get('eyes_closed', False):
            cv2.putText(result_image, "UWAGA: ZAMKNIETE OCZY!", (30, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        # Współczynnik senności
        if 'drowsiness_score' in drowsiness_result:
            drowsiness_score = drowsiness_result['drowsiness_score']
            
            # Dodaj do historii
            self.drowsiness_history.append(drowsiness_score)
            if len(self.drowsiness_history) > self.max_history:
                self.drowsiness_history.pop(0)
            
            # Kolor w zależności od poziomu senności
            if drowsiness_score > 0.7:
                color = (0, 0, 255)  # Czerwony
            elif drowsiness_score > 0.4:
                color = (0, 165, 255)  # Pomarańczowy
            else:
                color = (0, 255, 0)  # Zielony
            
            drowsiness_text = f"Sennosc: {drowsiness_score:.2f}"
            cv2.putText(result_image, drowsiness_text, (30, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return result_image
    
    def draw_alert_info(self, image, alert_result):
        """Rysuje informacje o alertach na obrazie."""
        result_image = image.copy()
        
        if 'alert_level' in alert_result:
            alert_level = alert_result['alert_level']
            
            # Teksty alertów
            alert_texts = ["Normalny", "Ostrzeżenie", "Alert", "Krytyczny"]
            alert_colors = [(0, 255, 0), (0, 165, 255), (0, 0, 255), (0, 0, 255)]
            
            if alert_level < len(alert_texts):
                alert_text = f"Alert: {alert_texts[alert_level]}"
                cv2.putText(result_image, alert_text, (30, 210),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, alert_colors[alert_level], 2)
        
        return result_image
    
    def add_stats_panel(self, image, recent_data=None):
        """Dodaje panel statystyk pod głównym obrazem."""
        # Wysokość panelu statystyk
        stats_height = 100
        
        # Utwórz czarny panel
        stats_panel = np.zeros((stats_height, image.shape[1], 3), dtype=np.uint8)
        
        # Rysowanie wykresu EAR
        if self.ear_history:
            max_ear = max(0.4, max(self.ear_history))
            points = []
            
            for i, ear in enumerate(self.ear_history):
                x = int(i * stats_panel.shape[1] / len(self.ear_history))
                y = int((1 - ear / max_ear) * (stats_height - 20)) + 10
                points.append((x, y))
            
            # Rysowanie wykresu
            for i in range(1, len(points)):
                cv2.line(stats_panel, points[i-1], points[i], (0, 255, 0), 1)
            
            # Rysowanie linii progu
            threshold_y = int((1 - 0.2 / max_ear) * (stats_height - 20)) + 10
            cv2.line(stats_panel, (0, threshold_y), (stats_panel.shape[1], threshold_y), 
                    (0, 0, 255), 1)
        
        # Pasek senności
        if self.drowsiness_history:
            drowsiness_score = self.drowsiness_history[-1]
            
            bar_width = 100
            bar_height = 20
            x = stats_panel.shape[1] - bar_width - 10
            y = 40
            
            # Tło paska
            cv2.rectangle(stats_panel, (x, y), (x + bar_width, y + bar_height),
                         (100, 100, 100), -1)
            
            # Wypełnienie paska
            fill_width = int(bar_width * drowsiness_score)
            
            # Kolor w zależności od poziomu senności
            if drowsiness_score > 0.7:
                color = (0, 0, 255)  # Czerwony
            elif drowsiness_score > 0.4:
                color = (0, 165, 255)  # Pomarańczowy
            else:
                color = (0, 255, 0)  # Zielony
            
            cv2.rectangle(stats_panel, (x, y), (x + fill_width, y + bar_height),
                         color, -1)
            
            # Etykieta
            cv2.putText(stats_panel, "Poziom senności", (x, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Połączenie obrazu głównego z panelem statystyk
        combined_image = np.vstack((image, stats_panel))
        
        return combined_image