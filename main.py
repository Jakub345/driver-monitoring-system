"""
Główny plik uruchamiający system monitorowania kierowcy.
"""
import cv2
import time
import numpy as np
import os
from modules.face_detection import FaceDetector
from modules.head_tracking import HeadTracker
from modules.drowsiness import DrowsinessDetector, PerclosMonitor
from modules.image_processing import ImageProcessor
from modules.calibration import Calibrator
from ui.config_window import ConfigUI
from ui.visualization import Visualizer
from ui.alerts import AlertSystem
from utils.logger import DataLogger
from utils.reports import ReportGenerator
from config import Config

def main():
    # Inicjalizacja konfiguracji
    config = Config()
    
    # Inicjalizacja modułów
    image_processor = ImageProcessor()
    face_detector = FaceDetector()
    head_tracker = HeadTracker(movement_threshold=config.head_movement_threshold)
    drowsiness_detector = DrowsinessDetector(
        ear_threshold=config.ear_threshold,
        eye_closed_time_threshold=config.eye_closed_time_threshold
    )
    
    # Inicjalizacja UI
    config_ui = ConfigUI("Konfiguracja Systemu")
    visualizer = Visualizer()
    alert_system = AlertSystem()
    
    # Inicjalizacja loggera
    data_logger = DataLogger("data")
    
    # Inicjalizacja kamery
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Błąd: Nie można otworzyć kamery.")
        return
    
    # Kalibracja (opcjonalna)
    calibrator = Calibrator(cap, face_detector)
    if config.perform_calibration:
        calibration_result = calibrator.calibrate()
        if calibration_result:
            config.ear_threshold = calibration_result.get('ear_threshold', config.ear_threshold)
            drowsiness_detector.set_ear_threshold(config.ear_threshold)
    
    print("System monitorowania kierowcy uruchomiony.")
    print("Naciśnij 'Esc' aby zakończyć, 'c' aby skalibrować.")
    
    running = True
    while running and cap.isOpened():
        # Odczyt klatki
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # Odbicie lustrzane
        frame = cv2.flip(frame, 1)
        
        # Przetwarzanie obrazu
        processed_frame = image_processor.process(frame)
        
        # Detekcja twarzy i oczu
        face_result = face_detector.detect(processed_frame)
        
        # Jeśli wykryto twarz
        combined_frame = frame.copy()
        if face_result['face_detected']:
            # Śledzenie pozycji głowy
            head_result = head_tracker.track(face_result)
            
            # Detekcja senności
            drowsiness_result = drowsiness_detector.detect(face_result, head_result)
            
            # Aktualizacja alertów
            alert_result = alert_system.update(drowsiness_result)
            
            # Logowanie danych
            data_logger.log({
                'face': face_result,
                'head': head_result,
                'drowsiness': drowsiness_result,
                'alert': alert_result
            })
            
            # Wizualizacja
            combined_frame = visualizer.draw_face_info(frame, face_result)
            combined_frame = visualizer.draw_head_info(combined_frame, head_result)
            combined_frame = visualizer.draw_drowsiness_info(combined_frame, drowsiness_result)
            combined_frame = visualizer.draw_alert_info(combined_frame, alert_result)
        else:
            # Brak detekcji twarzy
            cv2.putText(combined_frame, "Nie wykryto twarzy", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Dodanie panelu statystyk
        combined_frame = visualizer.add_stats_panel(combined_frame, data_logger.get_recent_data())
        
        # Wyświetlanie obrazu
        cv2.imshow('System Monitorowania Kierowcy', combined_frame)
        
        # Sprawdzenie ustawień z konfiguratora
        config_changes = config_ui.get_changes()
        if config_changes:
            # Aktualizacja konfiguracji
            if 'ear_threshold' in config_changes:
                config.ear_threshold = config_changes['ear_threshold']
                drowsiness_detector.set_ear_threshold(config.ear_threshold)
            if 'head_movement_threshold' in config_changes:
                config.head_movement_threshold = config_changes['head_movement_threshold']
                head_tracker.set_movement_threshold(config.head_movement_threshold)
            # Inne parametry...
        
        # Obsługa klawiszy
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Esc
            running = False
        elif key == ord('c'):  # Kalibracja
            calibration_result = calibrator.calibrate()
            if calibration_result:
                config.ear_threshold = calibration_result.get('ear_threshold', config.ear_threshold)
                drowsiness_detector.set_ear_threshold(config.ear_threshold)
        elif key == ord('s'):  # Zrzut ekranu
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join("data", f"screenshot_{timestamp}.jpg")
            cv2.imwrite(screenshot_path, combined_frame)
            print(f"Zapisano zrzut ekranu: {screenshot_path}")
    
    # Sprzątanie
    cap.release()
    cv2.destroyAllWindows()
    
    # Generowanie raportu
    if config.generate_report:
        report_generator = ReportGenerator()
        report_path = report_generator.generate(data_logger.get_log_path())
        print(f"Wygenerowano raport: {report_path}")
    
    print("System zakończył działanie.")

if __name__ == "__main__":
    main()