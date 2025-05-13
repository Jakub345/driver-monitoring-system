"""
Moduł do logowania danych.
"""
import os
import csv
import time
import json

class DataLogger:
    def __init__(self, log_dir="data"):
        """Inicjalizacja loggera danych."""
        # Utworzenie katalogu na logi jeśli nie istnieje
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Nazwa pliku z logami
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.log_path = os.path.join(log_dir, f"driver_monitoring_{timestamp}.csv")
        
        # Inicjalizacja pliku CSV
        with open(self.log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "EAR", "Eyes_Closed", "Head_Movement",
                "Head_Distracted", "PERCLOS", "Drowsiness_Score",
                "Alert_Level", "Alert_Type", "Brightness"
            ])
        
        # Historia danych
        self.data_history = []
        self.max_history_size = 100
    
    def log(self, data):
        """Zapisuje dane do pliku CSV."""
        # Flatten danych z różnych modułów
        flat_data = {}
        
        if 'face' in data:
            face_data = data['face']
            flat_data['eye_count'] = face_data.get('eye_count', 0)
            flat_data['filtered_eye_count'] = face_data.get('filtered_eye_count', 0)
        
        if 'head' in data:
            head_data = data['head']
            flat_data['head_movement'] = head_data.get('filtered_movement', 0)
            flat_data['head_distracted'] = head_data.get('head_distracted', False)
        
        if 'drowsiness' in data:
            drowsiness_data = data['drowsiness']
            flat_data['ear'] = drowsiness_data.get('ear', 0)
            flat_data['eyes_closed'] = drowsiness_data.get('eyes_closed', False)
            flat_data['perclos'] = drowsiness_data.get('perclos', 0)
            flat_data['drowsiness_score'] = drowsiness_data.get('drowsiness_score', 0)
        
        if 'alert' in data:
            alert_data = data['alert']
            flat_data['alert_level'] = alert_data.get('alert_level', 0)
            flat_data['alert_type'] = alert_data.get('alert_type', 'none')
        
        # Dodanie do historii
        self.data_history.append(flat_data)
        if len(self.data_history) > self.max_history_size:
            self.data_history.pop(0)
        
        # Zapisanie do pliku CSV
        with open(self.log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                flat_data.get('ear', 0),
                int(flat_data.get('eyes_closed', False)),
                flat_data.get('head_movement', 0),
                int(flat_data.get('head_distracted', False)),
                flat_data.get('perclos', 0),
                flat_data.get('drowsiness_score', 0),
                flat_data.get('alert_level', 0),
                flat_data.get('alert_type', 'none'),
                flat_data.get('brightness', 0)
            ])
    
    def get_recent_data(self):
        """Zwraca najnowsze dane."""
        return self.data_history
    
    def get_log_path(self):
        """Zwraca ścieżkę do pliku z logami."""
        return self.log_path