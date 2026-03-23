# puck.py - Klasa krążka (puck)
# Klasa Puck reprezentuje krążek w grze
# Odpowiada za:
# - przechowywanie pozycji i prędkości,
# - aktualizację ruchu,
# - obsługę kolizji ze ścianami i paletkami,
# - reset po zdobyciu punktu,
# - rysowanie krążka na ekranie.

import pygame
import random

class Puck:
    def __init__(self, x, y):
        # Aktualna pozycja środka krążka
        self.x = x
        self.y = y

        # Promień krążka (kolizje liczone są względem środka)
        self.radius = 12

        # Kolor krążka (biały)
        self.color = (255, 255, 255)

        # Prędkość początkowa w osi X i Y
        # Losowana, aby każda runda zaczynała się inaczej
        self.speed_x, self.speed_y = self.random_speed()

    def random_speed(self):
        """
        Generuje losową prędkość początkową krążka.

        Zwraca:
            (speed_x, speed_y) – prędkości w osi X i Y
        """
        # Niewielki zakres zapewnia kontrolowalną dynamikę gry
        x = random.randint(2,4)
        y = random.randint(2,4)
        return x,y

    def update_position(self, screen_w, screen_h):
        """
        Aktualizacja pozycji krążka oraz obsługa odbić od ścian.

        screen_w - szerokość ekranu
        screen_h - wysokość ekranu
        """

        # Przesunięcie krążka zgodnie z jego prędkością        
        self.x += self.speed_x
        self.y += self.speed_y

        # Odbicie od lewej/prawej ściany
        if self.x - self.radius <= 0:
            self.speed_x *= -1
        elif self.x + self.radius >= screen_w:
            self.speed_x *= -1

        # Odbicie od górnej/dolnej ściany
        if self.y - self.radius <= 0:
            self.speed_y *= -1
        elif self.y + self.radius >= screen_h:
            self.speed_y *= -1


    def check_collision(self, paddle):
        """
        Sprawdzenie kolizji krążka z paletką.

        paddle - obiekt klasy Paddle
        """

        # Prostokąt kolizyjny paletki
        paddle_rect = pygame.Rect(
            int(paddle.x - paddle.width // 2),
            int(paddle.y - paddle.height // 2),
            paddle.width,
            paddle.height
        )
        # Prostokąt kolizyjny krążka (aproksymacja koła)
        puck_rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2
        )

        # Sprawdzenie przecięcia prostokątów
        if paddle_rect.colliderect(puck_rect):
            # Odbicie w osi Y
            self.speed_y *= -1

            # Dodanie efektu odbicia w osi X (zależne od miejsca uderzenia)
            offset = (self.x - paddle.x) / (paddle.width // 2)
            # Korekta prędkości poziomej zależna od miejsca trafienia
            self.speed_x += offset * 2

            # Ograniczenie prędkości w osi Xa
            if self.speed_x > 8:
                self.speed_x = 8
            if self.speed_x < -8:
                self.speed_x = -8

    def reset(self, screen_w, screen_h, direction):
        """
        Reset krążka po zdobyciu punktu.

        screen_w  - szerokość ekranu
        screen_h  - wysokość ekranu
        direction - kierunek początkowego ruchu ("up" lub "down")
        """        

        # Ustawienie krążka na środku planszy
        self.x = screen_w // 2
        self.y = screen_h // 2

        # Nowa losowa prędkość
        self.speed_x, self.speed_y = self.random_speed()

        # Kierunek po zdobyciu punktu
        if direction == "up":
            self.speed_y = -abs(self.speed_y)
        else:
            self.speed_y = abs(self.speed_y)

    def draw(self, screen):
        #Rysowanie krążka na ekranie.
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)