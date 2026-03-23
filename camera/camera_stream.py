# camera_stream.py - Obsługa kamery i wyświetlanie obrazu OpenCV
# Przekazuje klatki do face_tracker

import cv2
from camera.face_tracker import FaceTracker

class CameraStream:
    def __init__(self):
        
        # Licznik klatek
        self.frame_count = 0
        
        # Ostatni obliczony kierunek patrzenia
        self.last_gaze = (0.0, 0.0)

        # Inicjalizacja kamery (0 = domyślna kamera systemowa)
        self.cap = cv2.VideoCapture(0)
        # Przechwytywanie błędów
        if not self.cap.isOpened():
            raise RuntimeError("Nie udało się otworzyć kamery")
        # Obiekt odpowiedzialny za analizę twarzy i wzroku
        self.tracker = FaceTracker()


    def get_frame_and_gaze(self):
        """
        Pobiera pojedynczą klatkę z kamery oraz oblicza
        kierunek patrzenia użytkownika.

        Zwraca:
        - frame : aktualna klatka wideo (OpenCV)
        - gaze  : wartość wychylenia (horizontal, vertical)
        """

        ret, frame = self.cap.read()
        if not ret:
            return None, (0, 0)

        self.frame_count += 1
        # Przetwarzanie tylko co drugą klatkę większa płynność gry
        if self.frame_count % 2 == 0:
            gaze = self.tracker.process_frame(frame)
            self.last_gaze = gaze
        else:
            # Użycie poprzedniej wartości kierunku wzroku
            # Jeśli nie jest analizowana klatka
            gaze = self.last_gaze

        return frame, gaze


    def show_frame(self, frame):
        """
        Wyświetla obraz z kamery w osobnym oknie OpenCV.
        Obraz może zawiera naniesione landmarki twarzy,
        co ułatwia debugowanie algorytmu śledzenia.
        """

        cv2.imshow("FaceLandmarker", frame)
        cv2.waitKey(1)

    def release(self):
        """
        Zwalnia zasoby kamery oraz zamyka wszystkie
        okna OpenCV. Powinno być wywołane przy
        zamykaniu aplikacji.
        """
        self.cap.release()
        cv2.destroyAllWindows()