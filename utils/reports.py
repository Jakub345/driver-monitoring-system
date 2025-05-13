"""
Moduł do generowania raportów.
"""
import os
import time
import pandas as pd
import matplotlib.pyplot as plt

class ReportGenerator:
    def __init__(self, output_dir="reports"):
        """Inicjalizacja generatora raportów."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, log_path):
        """Generuje raport HTML na podstawie pliku CSV z logami."""
        try:
            # Wczytanie danych
            data = pd.read_csv(log_path)
            
            # Obliczenie statystyk
            total_time = (data['Timestamp'].max() - data['Timestamp'].min()) / 60.0  # w minutach
            eyes_closed_ratio = data['Eyes_Closed'].mean() if 'Eyes_Closed' in data else 0
            head_distracted_ratio = data['Head_Distracted'].mean() if 'Head_Distracted' in data else 0
            avg_drowsiness = data['Drowsiness_Score'].mean() if 'Drowsiness_Score' in data else 0
            
            # Generowanie wykresów
            self._generate_ear_plot(data)
            self._generate_drowsiness_plot(data)
            
            # Nazwa pliku raportu
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            report_path = os.path.join(self.output_dir, f"report_{timestamp}.html")
            
            # Generowanie HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Raport z monitorowania kierowcy</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .stat {{ margin-bottom: 10px; }}
                    .chart {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Raport z monitorowania kierowcy</h1>
                    <p>Data: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                    
                    <h2>Statystyki sesji</h2>
                    <div class="stat">Całkowity czas: {total_time:.2f} minut</div>
                    <div class="stat">Procent czasu z zamkniętymi oczami: {eyes_closed_ratio*100:.2f}%</div>
                    <div class="stat">Procent czasu z odchyloną głową: {head_distracted_ratio*100:.2f}%</div>
                    <div class="stat">Średni poziom senności: {avg_drowsiness:.2f}</div>
                    
                    <h2>Wykresy</h2>
                    <div class="chart">
                        <h3>Eye Aspect Ratio (EAR)</h3>
                        <img src="ear_plot.png" width="100%">
                    </div>
                    <div class="chart">
                        <h3>Poziom senności</h3>
                        <img src="drowsiness_plot.png" width="100%">
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Zapisanie HTML
            with open(report_path, 'w') as f:
                f.write(html_content)
            
            return report_path
            
        except Exception as e:
            print(f"Błąd generowania raportu: {e}")
            return None
    
    def _generate_ear_plot(self, data):
        """Generuje wykres EAR."""
        plt.figure(figsize=(10, 6))
        plt.plot(data['Timestamp'] - data['Timestamp'].min(), data['EAR'])
        plt.axhline(y=0.2, color='r', linestyle='--')  # Linia progu EAR
        plt.title('Eye Aspect Ratio (EAR) podczas sesji')
        plt.xlabel('Czas (s)')
        plt.ylabel('EAR')
        plt.grid(True, alpha=0.3)
        plt.savefig(os.path.join(self.output_dir, 'ear_plot.png'))
        plt.close()
    
    def _generate_drowsiness_plot(self, data):
        """Generuje wykres poziomu senności."""
        if 'Drowsiness_Score' in data.columns:
            plt.figure(figsize=(10, 6))
            plt.plot(data['Timestamp'] - data['Timestamp'].min(), data['Drowsiness_Score'])
            plt.axhline(y=0.3, color='y', linestyle='--')  # Ostrzeżenie
            plt.axhline(y=0.7, color='r', linestyle='--')  # Krytyczny
            plt.title('Poziom senności podczas sesji')
            plt.xlabel('Czas (s)')
            plt.ylabel('Współczynnik senności')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(self.output_dir, 'drowsiness_plot.png'))
            plt.close()