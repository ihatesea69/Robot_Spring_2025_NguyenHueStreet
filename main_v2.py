import time
import cv2
import random
import pygame
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Initialize Pygame
pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
print(f"Current Screen: {screen_width} x {screen_height}")

# Constants
LOOP_MAX = 3
BLACK_BG = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
FONT_PATH = "./resouces/AmericanTypewriter.ttc"
GREETING_SOUNDS = ['EN', 'CHINA', 'FR', 'JP', 'KR', 'RUS']

# Initialize OpenCV window
cv2.namedWindow("ALL", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("ALL", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow("ALL", BLACK_BG)

def scroll_text():
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
    text_options = ["HAPPY NEW YEAR", "CUNG CHÚc TÂN XUÂN", "CHÚc MỬNG NĂM MỞI", "XUÂN ẮT TẬ 2025"]
    text = random.choice(text_options)

    try:
        font = ImageFont.truetype(FONT_PATH, 300)
    except Exception as e:
        print(f"Font Error: {e}")
        return

    text_width, text_height = font.getbbox(text)[2:4]
    x_pos = screen_width if 'x_pos' not in globals() else globals()['x_pos']
    y_pos = (screen_height - text_height) // 2

    while True:
        background.fill(0)
        pil_img = Image.fromarray(background)
        draw = ImageDraw.Draw(pil_img)

        draw.text((x_pos + 10, y_pos + 10), text, font=font, fill=(255, 255, 255))  # Shadow
        draw.text((x_pos, y_pos), text, font=font, fill=(0, 0, 255))

        pil_img = ImageEnhance.Brightness(pil_img).enhance(1.5)
        x_pos -= 30

        if x_pos + text_width < 0:
            x_pos = screen_width
            break

        cv2.imshow("Text", np.array(pil_img))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyWindow("Text")

def init_pygame_mixer():
    try:
        pygame.mixer.init()
        print("Pygame mixer initialized successfully.")
    except Exception as e:
        print(f"Error initializing Pygame mixer: {e}")

def display_eye(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video: {video_path}")
        return

    video_width, video_height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    aspect_ratio = video_width / video_height
    new_width = min(screen_width, int(aspect_ratio * screen_height))
    new_height = min(screen_height, int(screen_width / aspect_ratio))

    loop_count = 0
    while loop_count < LOOP_MAX:
        ret, frame = cap.read()
        if not ret:
            loop_count += 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        resized_frame = cv2.resize(frame, (new_width, new_height))
        background = BLACK_BG.copy()
        start_x, start_y = (screen_width - new_width) // 2, (screen_height - new_height) // 2
        background[start_y:start_y + new_height, start_x:start_x + new_width] = resized_frame

        cv2.imshow("Robot", background)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User pressed 'q', exiting.")
            break

    cap.release()
    cv2.destroyWindow("Robot")

def play_audio(audio_path):
    try:
        sound = pygame.mixer.Sound(audio_path)
        for _ in range(LOOP_MAX):
            sound.play()
            time.sleep(2.5)
    except Exception as e:
        print(f"Audio error: {e}")

def play_greeting_audio():
    selected_sound = random.choice(GREETING_SOUNDS)
    audio_path = f'resouces/sound_greeting/HPNewYear_{selected_sound}.mp3'
    play_audio(audio_path)

def display_eye_with_audio(video_path, audio_path):
    threading.Thread(target=play_audio, args=(audio_path,)).start()
    display_eye(video_path)
    threading.Thread(target=play_greeting_audio).start()

if __name__ == "__main__":
    init_pygame_mixer()
    threading.Thread(target=scroll_text).start()
    display_eye_with_audio("./resouces/video.mp4", "./resouces/audio.mp3")
