# Gra sterowana ruchem oczu / Eye Controlled Game

# Opis

Projekt przedstawia grę komputerową typu Pong, w której sterowanie odbywa się przy użyciu ruchu oczu zamiast tradycyjnych urządzeń wejścia.

Aplikacja łączy przetwarzanie obrazu w czasie rzeczywistym z pętlą gry, umożliwiając sterowanie paletką na podstawie kierunku spojrzenia wykrywanego przez kamerę internetową.

---

## Funkcjonalności

- Sterowanie grą za pomocą ruchu oczu
- Detekcja punktów twarzy w czasie rzeczywistym
- Integracja przetwarzania obrazu (OpenCV, MediaPipe) z pętlą gry (PyGame)
- Sterowanie analogiczne do joysticka (wychylenie)
- Przeciwnik sterowany przez sztuczną inteligencję

---

## Technologie

- Python 3.12
- PyGame
- OpenCV
- MediaPipe (Face Landmark Detection)

---

## Jak to działa

### Estymacja kierunku spojrzenia

Sterowanie opiera się na prostej analizie geometrii oka, a nie bezwzględnej pozycji w obrazie.

Wykorzystywane są punkty:
- kąciki oka (wewnętrzny i zewnętrzny)
- górna i dolna powieka
- środek tęczówki

Na ich podstawie obliczany jest środek oka oraz jego rozmiar, a następnie znormalizowane przesunięcie źrenicy:

- `nx ∈ [-1, 1]` – ruch poziomy
- `ny ∈ [-1, 1]` – ruch pionowy

### Mapowanie na sterowanie

Ruch oka działa analogicznie do joysticka:

- środek oka → brak ruchu  
- wychylenie → proporcjonalna prędkość paletki  

Zastosowano dodatkowe mechanizmy poprawiające stabilność sterowania:

- **dead zone** – niewielkie ruchy oka są ignorowane, co zapobiega przypadkowym drganiom
- **wygładzanie sygnału** – aktualna wartość jest uśredniana z poprzednią, co ogranicza nagłe zmiany sterowania

Dzięki temu sterowanie jest płynniejsze i bardziej przewidywalne.

## AI przeciwnika

Przeciwnik nie jest idealny – jego zachowanie zostało celowo ograniczone, aby mechanika sterowania była wyzwaniem dla gracza.

Zastosowano mechanizmy:

- czas reakcji (AI nie reaguje natychmiast)
- dynamiczny cel (śledzenie krążka tylko gdy leci w stronę AI)
- losowy błąd (odchylenie pozycji celu)
- ograniczona prędkość ruchu

---

## Wymagania

- Kamera
- Python 3.12

---

## Instalacja
1. **Utworzenie wirtualnego środowiska w katalogu projektu**
```bash
python3.12 -m venv venv
```
2. **Aktywacja środowiska**

Windows
```bash
venv\Scripts\activate
```
Linux
```bash
source venv/bin/activate
```
3. **Instalacja zależności**
```bash
pip install -r requirements.txt
```
4. **Uruchomienie gry**
```bash
python3.12 main.py
```

### Wideo

Demo z działania gry pokazuje działanie gry z widokiem okna gry oraz podglądem na obraz kamery z nałożonymi punktami charakterystycznymi. Migotanie punktów jest spowodowane przetwarzaniem obrazu co drugą klatke co ma za zadanie zmniejszyć obciążenie procesora.

[[Link do Demo]](https://drive.google.com/file/d/1eM_K0tPHoTuxMq27wjAdPOY5bcNdmXzl/view?usp=sharing)
