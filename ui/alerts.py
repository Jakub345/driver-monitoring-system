"""
Moduł do zarządzania alertami.
"""
import cv2
import numpy as np
import threading
import time
try:
    import winsound  # tylko na Windows
except ImportError:
    print("Moduł winsound nie jest dostępny na tym systemie.")

class AlertSystem:
    def __init__(self):
        """Inicjalizacja systemu alertów."""
        self.current_alert_level = 0
        self.alert_sound_thread = None
        self.is_alerting = False
    
    def update(self, drowsiness_result):
        """Aktualizuje stan alertów na podstawie danych o senności."""
        # Jeśli nie ma danych o senności
        if not drowsiness_result:
            return {'alert_level': 0, 'alert_type': 'none'}
        
        # Pobierz poziom alertu z wyników detekcji senności
        alert_level = drowsiness_result.get('alert_level', 0)
        
        # Określenie typu alertu
        alert_type = 'none'
        if drowsiness_result.get('eyes_closed', False):
            alert_type = 'eyes_closed'
        elif alert_level >= 2:
            alert_type = 'drowsiness'
        elif drowsiness_result.get('head_distracted', False):
            alert_type = 'head_movement'
        
        # Dźwięk alarmu (tylko jeśli poziom alertu się zwiększył)
        if alert_level > self.current_alert_level and alert_level >= 2:
            self._play_alert_sound(alert_level)
        
        # Zapamiętanie bieżącego poziomu alertu
        self.current_alert_level = alert_level
        
        return {
            'alert_level': alert_level,
            'alert_type': alert_type
        }

    def manual_alert(self, alert_type: str, alert_level: int = 3):
        """
        Ręczne wywołanie alarmu, np. z odczytu Arduino.
        :param alert_type: etykieta alarmu, np. "low_pulse"
        :param alert_level: poziom alarmu (2=średni, 3=krytyczny)
        :return: dict w formacie update(), do dalszej obsługi w main.py
        """
        # Jeżeli nowy poziom jest wyższy, zagraj dźwięk
        if alert_level > self.current_alert_level:
            self._play_alert_sound(alert_level)
        # Zaktualizuj stan
        self.current_alert_level = alert_level
        # Zwróć wynik tak, jak update()
        return {
            'alert_level': alert_level,
            'alert_type': alert_type
        }

    
    def _play_alert_sound(self, alert_level):
        """Odtwarza dźwięk alarmu."""
        # Zatrzymanie poprzedniego dźwięku
        self.is_alerting = False
        if self.alert_sound_thread and self.alert_sound_thread.is_alive():
            self.alert_sound_thread.join(0.1)
        
        # Nowy dźwięk
        self.is_alerting = True
        self.alert_sound_thread = threading.Thread(target=self._sound_thread, args=(alert_level,))
        self.alert_sound_thread.daemon = True
        self.alert_sound_thread.start()
    
    def _sound_thread(self, alert_level):
        """Wątek odtwarzający dźwięk alarmu."""
        try:
            if alert_level == 2:
                # Alert - średni dźwięk
                for _ in range(2):
                    if not self.is_alerting:
                        break
                    winsound.Beep(1000, 300)
                    time.sleep(0.2)
            elif alert_level >= 3:
                # Krytyczny - głośny i szybki dźwięk
                for _ in range(3):
                    if not self.is_alerting:
                        break
                    winsound.Beep(1500, 200)
                    time.sleep(0.1)
        except:
            # W przypadku błędu (np. na Linux/Mac)
            print("Dźwięk alertu niedostępny.")