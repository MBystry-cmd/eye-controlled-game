# ai_controller.py - Klasa kontrolera sztucznej inteligencji
# Odpowiada wyłącznie za:
#  - podejmowanie decyzji (gdzie AI chce się przesunąć),
#  - ograniczanie prędkości i czasu reakcji,
#  - wprowadzanie błędu, aby AI nie było idealne.

import random

class AIController:
    def __init__(self):
        # Maksymalna prędkość ruchu paletki AI (piksele na sekundę)
        self.max_speed = 400
        
        # Maksymalny losowy błąd w położeniu celu (w pikselach)
        # Im większa wartość, tym mniej precyzyjna sztuczna inteligencja
        self.error = 50

        # Czas reakcji AI w sekundach
        # AI aktualizuje cel dopiero po upływie tego czasu,
        # co symuluje opóźnienie reakcji człowieka
        self.reaction = 0.25
        
        # Licznik czasu od ostatniej decyzji
        self.timer = 0

        # Aktualny cel w osi X, do którego AI próbuje się przesunąć
        # None oznacza brak celu na starcie gry
        self.target_x = None

    def update(self, paddle, puck, screen_w, dt):
        """
        Metoda aktualizująca zachowanie AI.
        Wywoływana co klatkę z pętlą gry.

        paddle   - obiekt paletki sterowanej przez AI
        puck     - obiekt krążka
        screen_w - szerokość ekranu
        dt       - czas od ostatniej klatki (delta time)
        """

        # Zliczanie czasu od ostatniej decyzji AI
        self.timer += dt
        
        # Podejmowanie nowej decyzji po upływie czasu reakcji
        if self.timer >= self.reaction:
            self.timer = 0

            # Jeżeli krążek porusza się w stronę AI ustala aktualny cel
            if puck.speed_y < 0:
                # AI celuje w pozycję krążka z dodanym losowym błędem
                self.target_x = puck.x + random.uniform(-self.error, self.error)
            else:
                # Jeżeli krążek oddala się od AI, paletka wraca do środka ekranu
                self.target_x = screen_w // 2

        # Jeżeli AI nie ma jeszcze ustalonego celu to nic nie robi
        if self.target_x is None:
            return

        # Różnica pomiędzy aktualną pozycją paletki a celem        
        dx = self.target_x - paddle.x
        # Maksymalny możliwy ruch w tej klatce zależny od dt
        max_move = self.max_speed * dt

        # Wykonanie ruchu z ograniczoną prędkością
        paddle.move(
            max(-max_move, min(max_move, dx)),
            screen_w
        )
