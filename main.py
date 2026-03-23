# main.py - Punkt startowy gry
# Łączy moduły: kamera (OpenCV + MediaPipe) i gra (Pygame)

from camera.camera_stream import CameraStream
from game.game_loop import GameLoop

if __name__ == "__main__":
    # Inicjalizacja strumienia kamery
    camera = CameraStream()

    # Inicjalizacja gry
    game = GameLoop(camera)

    # Uruchomienie pętli gry
    game.run()
