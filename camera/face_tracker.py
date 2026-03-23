# face_tracker.py - Obsługa MediaPipe FaceLandmarker
# Moduł odpowiedzialny za:
# - detekcję twarzy przy użyciu MediaPipe FaceLandmarker
# - lokalizację oczu oraz tęczówek
# - obliczanie kierunku patrzenia użytkownika
# - normalizację sygnału do zakresu [-1, 1]
# - wygładzanie, martwą strefę oraz kalibrację
#
# Moduł pełni rolę „wirtualnego joysticka” sterowanego wzrokiem.

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Stałe indeksów landmarków twarzy
# Wydzielone są w osobnym pliku dla czytelności
from utils.constants import (
    LEFT_EYE, LEFT_IRIS, RIGHT_EYE, RIGHT_IRIS,
    LEFT_EYEBROW, RIGHT_EYEBROW,
    LEFT_OUTER_CORNER, LEFT_INNER_CORNER, LEFT_TOP, LEFT_BOTTOM,
    RIGHT_OUTER_CORNER, RIGHT_INNER_CORNER, RIGHT_TOP, RIGHT_BOTTOM
)


class FaceTracker:
    def __init__(self):
        """
            Inicjalizacja śledzenia twarzy i wzroku

            Konfiguruje MediaPipe FaceLandmarker oraz wszystkie
            parametry związane z filtracją i kalibracją sygnału.
        """

        # Skróty nazw klas MediaPipe
        BaseOptions = python.BaseOptions
        FaceLandmarkerOptions = vision.FaceLandmarkerOptions
        RunningMode = vision.RunningMode

        # Konfiguracja FaceLandmarkera
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='face_landmarker.task'), # Model ML zapisany na dysku
            running_mode=RunningMode.IMAGE,      #Tryb analizy opcja pojedynczego obrazu
            num_faces=1,                         #Liczby twarzy do wykrywania
            min_face_detection_confidence=0.5,   #Minimalne zaufanie detekcji twarzy
            min_face_presence_confidence=0.5,    #Minimalne zaufanie obecności twarzy
            output_face_blendshapes=False,       #Służy do detekcji zmiany kształtu twarzy np.emocje W moim przypadku nie potrzebne
            output_facial_transformation_matrixes=True,  #na wyjściu macierz transformacji twarzy
        )

        # Utworzenie obiektu FaceLandmarker
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)
        # Alias klasy obrazu MediaPipe
        self.mp_image = mp.Image
        
        # Flaga informująca o kalibracji
        self.is_calibrating = False


        # Parametry wygładzania joysticka i martwa strefa
        
        # Poprzednie wartości kierunku patrzenia użyte do filtracji
        self.prev_horizontal = 0.0
        self.prev_vertical   = 0.0
        
        # Współczynnik wygładania
        # Im bliżej 1.0 tym ruch bardziej stabilny i wygładzony, ale wolniejszy
        self.alpha = 0.7
        # Martwa strefa czyli ignorowanie drobnych ruchów oczu
        self.dead_zone = 0.10
        
        # Skalowanie joysticka (wzmocnienie, bo realny ruch źrenicy jest mały)
        self.scale_x = 4.0
        self.scale_y = 2.5

        # Korekta kalibracji
        self.bias_x = 0.0
        self.bias_y = 0.0

    @staticmethod
    def _mean_xy(landmarks, indices):
        """
            Oblicza współrzędne środek ciężkości z wybranych punktów
            Głównie używane do wyznaczania środka tęczówki

            Zwraca punkt reprezentujący środek tęczówki
        """
        xs = [landmarks[i].x for i in indices]
        ys = [landmarks[i].y for i in indices]
        return (float(sum(xs) / len(xs)), float(sum(ys) / len(ys)))

    def start_calibration(self):
        """
            Funkcja rozpoczynająca kalibracje - zbieranie punktów przy patrzeniu w środek ekranu

            Użytkownik powinien patrzeć się w środek ekranu
        """
        self.calibration_samples = []
        self.is_calibrating = True
        print("Kalibracja rozpoczęta – patrz na środek ekranu...")

    def add_calibration_sample(self, horizontal, vertical):
        """
            Dodaje próbki do kalibracji i wyciąga średnią z 50 próbek jako korektę kalibracji

            Po zebraniu próbek i obliczeniu średniej staje się ona nowym środkiem (0,0)
        """
        if self.is_calibrating:
            self.calibration_samples.append((horizontal, vertical))
            if len(self.calibration_samples) >= 50:
                avg_x = sum(x for x, _ in self.calibration_samples) / len(self.calibration_samples)
                avg_y = sum(y for _, y in self.calibration_samples) / len(self.calibration_samples)
                self.bias_x = avg_x
                self.bias_y = avg_y
                self.is_calibrating = False
                print(f"Kalibracja zakończona! bias_x={self.bias_x:.2f}, bias_y={self.bias_y:.2f}")


    def _normalized_eye_offset(self, lm, iris_idx, outer_corner_idx, inner_corner_idx, top_idx, bottom_idx):
        """
        Oblicza znormalizowaną pozycję źrenicy względem oka

        Zwraca:

        - nx [-1,1] - wychylenie poziome
        - ny [-1,1] - wychylenie pionowe

        Metoda jest dzięki temu odporna na ruchy głowy,
        ponieważ bazuje na geometrii oka
        """

        # Środek tęczówki
        iris_x, iris_y = self._mean_xy(lm, iris_idx)

        # Geometria oka
        outer = lm[outer_corner_idx]
        inner = lm[inner_corner_idx]
        top   = lm[top_idx]
        bottom= lm[bottom_idx]

        # Środek oka
        eye_mid_x = (outer.x + inner.x) / 2.0
        eye_mid_y = (top.y + bottom.y) / 2.0

        # Rozmiar oka (oraz zabezpieczenie przed dzieleniem przez 0 dodając 1e-6 czyli bardzo małą liczbę)
        eye_w = abs(inner.x - outer.x) + 1e-6   # szerokość oka
        eye_h = abs(bottom.y - top.y) + 1e-6    # wysokość oka

        # Znormalizowane przesunięcie źrenicy względem środka oka
        nx = (iris_x - eye_mid_x) / eye_w
        ny = (iris_y - eye_mid_y) / eye_h

        # Współrzędna y w obrazie rośnie w dół, więc trzeba obrócić, czyli zmiana znaku na '-'
        ny = -ny

        return nx, ny

    def process_frame(self, frame):
        """
            Analiza klatek obrazu z kamery i zwraca 
            uśredniony kierunek patrzenia w zakresie [-1,1]
        """

        # Konwersja z BGR do RGB dla MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Utworzenie obiektu obrazu MediaPipe
        mp_img = self.mp_image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Wykrywanie landmarków twarzy
        result = self.face_landmarker.detect(mp_img)

        # Jeśli brak twarzy to punkt neutralny [0,0]
        if not result.face_landmarks:
            return (0.0, 0.0)

        # Pierwsza wykryta twarz
        lm = result.face_landmarks[0]
        h, w, _ = frame.shape

        # Obliczenie wychylenia dla obu oczu
        left_nx, left_ny = self._normalized_eye_offset(
            lm, LEFT_IRIS, LEFT_OUTER_CORNER, LEFT_INNER_CORNER, LEFT_TOP, LEFT_BOTTOM
        )
        right_nx, right_ny = self._normalized_eye_offset(
            lm, RIGHT_IRIS, RIGHT_OUTER_CORNER, RIGHT_INNER_CORNER, RIGHT_TOP, RIGHT_BOTTOM
        )

        # Średnia obu oczu
        horizontal = (left_nx + right_nx) / 2.0
        vertical   = (left_ny + right_ny) / 2.0

        # Wzmocnienie (naturalny zakres jest niewielki)
        horizontal *= self.scale_x
        vertical   *= self.scale_y

        # Ograniczenie do [-1,1]
        horizontal = max(-1.0, min(1.0, horizontal))
        vertical   = max(-1.0, min(1.0, vertical))

        # Martwa strefa — drobne ruchy oczu ignorujemy
        if abs(horizontal) < self.dead_zone:
            horizontal = 0.0
        if abs(vertical) < self.dead_zone:
            vertical = 0.0

        # Wygładzanie ruchu
        horizontal = self.alpha * horizontal + (1 - self.alpha) * self.prev_horizontal
        vertical   = self.alpha * vertical   + (1 - self.alpha) * self.prev_vertical
        self.prev_horizontal = horizontal
        self.prev_vertical   = vertical

        # Korekta z kalibracji
        horizontal -= self.bias_x
        vertical   -= self.bias_y

        #Dodawanie próbek do kalibracji, jeśli odbywa się kalibracja
        self.add_calibration_sample(horizontal, vertical)

        # Rysowanie landmarków na obrazie OpenCV dla debugu
        # oko + brew + tęczówki
        for face_landmarks in result.face_landmarks:
            # Lewa brew + oko
            for idx in (LEFT_EYE + LEFT_EYEBROW):
                lm_i = face_landmarks[idx]
                x, y = int(lm_i.x * w), int(lm_i.y * h)
                cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

            # Prawa brew + oko
            for idx in (RIGHT_EYE + RIGHT_EYEBROW):
                lm_i = face_landmarks[idx]
                x, y = int(lm_i.x * w), int(lm_i.y * h)
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

            # Tęczówki
            for idx in (RIGHT_IRIS + LEFT_IRIS):
                lm_i = face_landmarks[idx]
                x, y = int(lm_i.x * w), int(lm_i.y * h)
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
        # Zwracam (-horizontal), (vertical) jako wartości wychylenia joysticka
        # Przed horizontal jest '-' bo kamera zwraca obraz w odbiciu lustrzanym
        return ((-horizontal), (vertical))