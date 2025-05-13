# System Monitorowania Skupienia Kierowcy

System monitorujący stan skupienia kierowcy przy użyciu kamery internetowej. Wykrywa zamknięte oczy i odchylenie głowy w celu identyfikacji zmęczenia i nieuwagi.

## Funkcje

- Detekcja twarzy i oczu przy użyciu OpenCV
- Śledzenie pozycji głowy
- Wykrywanie zamkniętych oczu
- Obliczanie współczynnika senności
- System alertów wizualnych i dźwiękowych
- Możliwość kalibracji do konkretnego użytkownika
- Logowanie danych i generowanie raportów

## Wymagania

- Python 3.7+
- OpenCV
- NumPy
- Pandas (do generowania raportów)
- Matplotlib (do generowania wykresów)

## Instalacja

```bash
# Klonowanie repozytorium
git clone https://github.com/[twój-użytkownik]/driver-monitoring-system.git
cd driver-monitoring-system

# Instalacja zależności
pip install -r requirements.txt


Użycie
python main.py