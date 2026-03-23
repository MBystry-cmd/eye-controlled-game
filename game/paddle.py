# paddle.py - Klasa paletki (gracza lub AI)
# Odpowiada wyłącznie za:
# - przechowywanie pozycji i rozmiaru paletki
# - ograniczenie ruchu do obszaru ekranu
# - rysowanie paletki

import pygame

class Paddle:
    def __init__(self, x, y):
        """
        Konstruktor paletki.

        Parametry:
        x, y – początkowa pozycja środka paletki w układzie współrzędnych ekranu.

        Paletka jest opisywana przez punkt środkowy,
        co upraszcza obliczenia kolizji i ruchu.
        """
        self.x = x                  # Pozycja pozioma środka paletki
        self.y = y                  # Pozycja pionowa środka paletki

        self.width = 100            # Szerokość paletki w pikselach
        self.height = 20            # Wysokość paletki w pikselach

        self.color = (0, 255, 0)    # Kolor paletki (zielony RGB)

    def move(self, dx, screen_w):
        """
        Przesuwa paletkę w poziomie.

        Parametry:
        dx        – zmiana pozycji w osi X (dodatnia: w prawo, ujemna: w lewo)
        screen_w – szerokość ekranu (do ograniczenia ruchu)

        Wartość parametru dx:
        - dla gracza: dx wynika z kierunku patrzenia
        - dla AI: dx wynika z logiki przeciwnika
        """
        # Aktualizacja pozycji w osi X
        self.x += dx
        # Ograniczenie ruchu do granic ekranu:
        # paletka nie może wyjść poza lewą ani prawą krawędź
        self.x = max(self.width // 2, min(screen_w - self.width // 2, self.x))

    def draw(self, screen):
        """
        Rysuje paletkę na ekranie.

        Paletka jest reprezentowana jako prostokąt Pygame,
        którego pozycja jest liczona na podstawie środka (x, y),
        a nie lewego górnego rogu.
        """        
        rect = pygame.Rect(
            int(self.x - self.width // 2), #lewy górny róg X
            int(self.y - self.height // 2), #lewy górny róg Y
            self.width,
            self.height
        )
        # Rysowanie prostokąta na ekranie
        pygame.draw.rect(screen, self.color, rect)
