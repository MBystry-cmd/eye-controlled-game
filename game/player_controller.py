# player_controller.py - Klasa kontrolera gracza
# Kontroler odpowiada za ustawienie prędkości i za ruch gracza

class PlayerController:
    def __init__(self, speed=15):
        # Współczynnik prędkości ruchu paletki gracza
        # Określa, jak silnie sygnał wejściowy (gaze) wpływa na przesunięcie paletki
        # Dzięki temu można łatwo dostosować czułość sterowania
        self.speed = speed

    def update(self, paddle, gaze, screen_w):
        """
        Aktualizacja ruchu paletki gracza.
        Metoda wywoływana co klatkę w pętli gry.

        paddle   - obiekt paletki sterowanej przez gracza
        gaze     - wartość (horizontal, vertical) określająca kierunek patrzenia
        screen_w - szerokość ekranu (do ograniczenia ruchu paletki)
        """
        # Składowa pozioma sygnału sterującego z face trackera
        horizontal, _ = gaze
        # Przeliczenie sygnału wejściowego na przesunięcie paletki gdzie speed pełni rolę wzmocnienia
        paddle.move(horizontal * self.speed, screen_w)
