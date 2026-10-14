import cv2
import numpy as np
import mediapipe as mp
from collections import deque

# AI-Powered Touchless Virtual Drawing System
# Controls:
#   Index finger up + middle finger down: draw
#   Index + middle fingers up: move cursor / select colour buttons
#   Closed fist: erase
#   Press C: clear canvas, Q or ESC: quit

WIDTH, HEIGHT = 1280, 720
BRUSH_SIZE = 8
ERASER_SIZE = 45

COLORS = [
    ("WHITE", (255, 255, 255)),
    ("RED", (0, 0, 255)),
    ("GREEN", (0, 255, 0)),
    ("BLUE", (255, 0, 0)),
    ("YELLOW", (0, 255, 255)),
    ("PURPLE", (255, 0, 255)),
]
selected_color = COLORS[1][1]

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
points = deque(maxlen=2)
prev_x, prev_y = None, None

def finger_up(hand, tip, pip):
    return hand.landmark[tip].y < hand.landmark[pip].y

def draw_ui(frame, mode):
    cv2.rectangle(frame, (0, 0), (WIDTH, 85), (28, 31, 42), -1)
    cv2.putText(frame, "AI TOUCHLESS DRAWING", (22, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
    cv2.putText(frame, f"MODE: {mode}", (22, 63),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (120, 230, 255), 2)
    x = 390
    for name, color in COLORS:
        cv2.rectangle(frame, (x, 17), (x + 62, 62), color, -1)
        border = (255, 255, 255) if color == selected_color else (90, 90, 90)
        cv2.rectangle(frame, (x, 17), (x + 62, 62), border, 3 if color == selected_color else 1)
        cv2.putText(frame, name[:3], (x + 8, 78), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (220, 220, 220), 1)
        x += 72
    cv2.putText(frame, "C: Clear   Q/ESC: Quit", (WIDTH - 280, 78),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220, 220, 220), 1)

def main():
    global canvas, selected_color, prev_x, prev_y
    cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
    if not cap.isOpened():
        print("ERROR: Webcam not found. Connect a camera and try again.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    smooth_x, smooth_y = None, None

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.60
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Could not read from webcam.")
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)
            mode = "SHOW HAND TO START"

            if result.multi_hand_landmarks:
                hand_landmarks = result.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark
                ix, iy = int(lm[8].x * WIDTH), int(lm[8].y * HEIGHT)
                mx, my = int(lm[12].x * WIDTH), int(lm[12].y * HEIGHT)

                # Smooth cursor movement to reduce jitter.
                smooth_x = ix if smooth_x is None else int(0.65 * smooth_x + 0.35 * ix)
                smooth_y = iy if smooth_y is None else int(0.65 * smooth_y + 0.35 * iy)
                index_up = finger_up(hand_landmarks, 8, 6)
                middle_up = finger_up(hand_landmarks, 12, 10)
                ring_up = finger_up(hand_landmarks, 16, 14)
                pinky_up = finger_up(hand_landmarks, 20, 18)

                # Two fingers up: navigation / colour selection.
                if index_up and middle_up:
                    mode = "MOVE / SELECT COLOUR"
                    prev_x, prev_y = None, None
                    if smooth_y < 95:
                        color_x = smooth_x
                        if 390 <= color_x < 390 + 72 * len(COLORS):
                            selected_color = COLORS[min((color_x - 390) // 72, len(COLORS)-1)][1]
                    cv2.circle(frame, (smooth_x, smooth_y), 12, (255, 255, 255), 2)

                # Index finger only: draw.
                elif index_up and not middle_up:
                    mode = "DRAWING"
                    if prev_x is not None and prev_y is not None:
                        cv2.line(canvas, (prev_x, prev_y), (smooth_x, smooth_y), selected_color, BRUSH_SIZE, cv2.LINE_AA)
                    prev_x, prev_y = smooth_x, smooth_y
                    cv2.circle(frame, (smooth_x, smooth_y), BRUSH_SIZE, selected_color, -1)

                # Closed hand: erase.
                elif not index_up and not middle_up and not ring_up and not pinky_up:
                    mode = "ERASER"
                    cv2.circle(canvas, (smooth_x, smooth_y), ERASER_SIZE, (0, 0, 0), -1)
                    prev_x, prev_y = None, None
                    cv2.circle(frame, (smooth_x, smooth_y), ERASER_SIZE, (240, 240, 240), 2)
                else:
                    mode = "PAUSED - TWO FINGERS TO MOVE"
                    prev_x, prev_y = None, None
            else:
                prev_x, prev_y = None, None
                smooth_x, smooth_y = None, None

            # Overlay drawing canvas onto webcam, retaining dark canvas background.
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            inverse = cv2.bitwise_not(mask)
            background = cv2.bitwise_and(frame, frame, mask=inverse)
            drawing = cv2.bitwise_and(canvas, canvas, mask=mask)
            output = cv2.add(background, drawing)
            draw_ui(output, mode)
            cv2.imshow("AI Touchless Virtual Drawing System", output)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("c"):
                canvas[:] = 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
