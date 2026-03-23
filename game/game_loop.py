# game_loop.py - Pętla gry Air Hockey
# Obsługuje:
# - inicjalizację Pygame
# - obsługę zdarzeń (klawiatura, zamknięcie okna)
# - sterowanie graczem i przeciwnikiem (AI)
# - aktualizację fizyki krążka
# - wykrywanie punktów
# - rysowanie wszystkich elementów gry

import pygame
from game.paddle import Paddle
from game.puck import Puck
from game.player_controller import PlayerController
from game.ai_controller import AIController

class GameLoop:
    def __init__(self, camera):
        """
        Konstruktor głównej pętli gry.
        Inicjalizuje Pygame, ekran, obiekty gry oraz zmienne stanu.
        """
        
        pygame.init()
        
        # Rozdzielczość okna gry
        self.SCREEN_W, self.SCREEN_H = 800, 600
        # Utworzenie okna gry
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pygame.display.set_caption("Eye Hockey")

        #Zegar gry
        self.clock = pygame.time.Clock()
        # Obiekt kamery
        self.camera = camera
        #Licznik punktów
        self.player_score = 0
        self.ai_score = 0
        # Czcionka do wyświetlania wyników
        self.font = pygame.font.SysFont(None, 36)

        # Ustawienie pozycji startowej gracza i ustalenie jego kontrolera
        self.player = Paddle(self.SCREEN_W // 2, self.SCREEN_H - 50)
        self.player_controller = PlayerController()

        # Ustawienie pozycji startowej paletki AI i ustalenie jego kontrolera
        self.ai = Paddle(self.SCREEN_W // 2, 50)
        self.ai_controller = AIController()
        # Ustawienie Krążka na środku ekranu
        self.puck = Puck(self.SCREEN_W // 2, self.SCREEN_H // 2)

    def run(self):
        """
        Główna pętla gry.
        Wykonywana co klatkę aż do zamknięcia aplikacji.
        """
        running = True
        while running:
            # dt to czas jednej klatki w sekundach wykorzystywane przez AI
            dt = self.clock.tick(30) / 1000.0

            # fps = self.clock.get_fps()
            # print(fps)

            # Obsługa zdarzeń klawiatury Zamknięcie gry oraz kalibracja
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.camera.tracker.start_calibration()

            # Pobieranie klatki z kamery i kierunk patrzenia
            frame, gaze = self.camera.get_frame_and_gaze()
            if frame is not None:
                #Wywietlenie obrazu z kamery
                self.camera.show_frame(frame)

            #Aktualizacja pozycji paletki gracza na podstawie kierunku patrzenia
            self.player_controller.update(
                self.player, gaze, self.SCREEN_W
            )
            #Aktualizacja pozycji paletki przeciwnika AI śledzącego krążek
            self.ai_controller.update(
                self.ai, self.puck, self.SCREEN_W, dt
            )
            #Aktualizacja pozycji krążka ruch oraz odbicia
            self.puck.update_position(self.SCREEN_W, self.SCREEN_H)


            # Logika zdobywania punktów, czyli dotknięcie krawędzi górnej lub dolnej to punkt
            if self.puck.y - self.puck.radius <= 0:
                # gracz zdobywa punkt
                self.player_score += 1
                self.puck.reset(self.SCREEN_W, self.SCREEN_H, direction="down")

            elif self.puck.y + self.puck.radius >= self.SCREEN_H:
                # AI zdobywa punkt
                self.ai_score += 1
                self.puck.reset(self.SCREEN_W, self.SCREEN_H, direction="up")

            # Sprawdzanie kolizji między krążkiem i paletką dla gracza i przeciwnika
            self.puck.check_collision(self.player)
            self.puck.check_collision(self.ai)

            # Rysowanie gry
            self.screen.fill((0, 0, 0)) # Czarne tło
            self.draw_scoreboard() # Rysowanie tablicy wyników
            # Rysowanie paletek i krążka
            self.player.draw(self.screen)
            self.ai.draw(self.screen)
            self.puck.draw(self.screen)
            # Wyświetlenie narysowanej klatki
            pygame.display.flip()
            self.clock.tick(30) # Ograniczenie liczby klatek do 30

        # Sprzątanie zasobów po wyjściu z pętli
        self.camera.release()
        pygame.quit()

    def draw_scoreboard(self):
        """
        Rysuje tablicę wyników po prawej stronie ekranu.
        Wyniki są ułożone jeden pod drugim w niebieskiej ramce.
        """
        # Ramka wyniku
        box_width = 80
        box_height = 100
        box_x = self.SCREEN_W - box_width - 20
        box_y = self.SCREEN_H // 2 - box_height // 2

        # tło ramki
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            (box_x, box_y, box_width, box_height)
        )

        # niebieska ramka
        pygame.draw.rect(
            self.screen,
            (0, 0, 255),
            (box_x, box_y, box_width, box_height),
            2
        )

        
        player_text = self.font.render(
            f"P1: {self.player_score}",
            True,
            (255, 255, 255)
        )

        ai_text = self.font.render(
            f"AI: {self.ai_score}",
            True,
            (255, 255, 255)
        )

        # pozycje tekstu (jeden pod drugim)
        player_rect = player_text.get_rect(
            center=(box_x + box_width // 2, box_y + 70)
        )

        ai_rect = ai_text.get_rect(
            center=(box_x + box_width // 2, box_y + 35)
        )
        
        # Rysowanie tekstów na ekranie
        self.screen.blit(player_text, player_rect)
        self.screen.blit(ai_text, ai_rect)