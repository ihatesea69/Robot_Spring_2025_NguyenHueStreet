import cv2
import threading
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random

class DisplayManager:
    def __init__(self, screen_width, screen_height, audio_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.audio_manager = audio_manager
        self.loop_max = 3
        
    def display_eye(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Cannot open video: {video_path}")
            return

        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        background = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)

        loop_count = 0
        while loop_count < self.loop_max:
            ret, frame = cap.read()
            if not ret:
                loop_count += 1
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            aspect_ratio = video_width / video_height
            new_width = min(self.screen_width, int(aspect_ratio * self.screen_height))
            new_height = min(self.screen_height, int(self.screen_width / aspect_ratio))

            resized_frame = cv2.resize(frame, (new_width, new_height))
            start_x = (self.screen_width - new_width) // 2
            start_y = (self.screen_height - new_height) // 2
            
            background[:, :] = 0
            background[start_y:start_y+new_height, start_x:start_x+new_width] = resized_frame

            cv2.namedWindow("Robot", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Robot", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Robot", background)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyWindow("Robot")

    def display_eye_with_audio(self, video_path, audio_path):
        audio_thread = threading.Thread(target=self.audio_manager.play_audio, args=(audio_path,))
        audio_thread.start()
        self.display_eye(video_path)
        audio_thread.join()
        
        greeting_thread = threading.Thread(target=self.audio_manager.play_greeting)
        greeting_thread.start()
        self.display_eye(video_path)
        greeting_thread.join()

    def display_eye_with_audio_no_greeting(self, video_path, audio_path):
        audio_thread = threading.Thread(target=self.audio_manager.play_audio, args=(audio_path,))
        audio_thread.start()
        self.display_eye(video_path)
        audio_thread.join() 

    def scroll_text(self):
        background = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        textArr = ["HAPPY NEW YEAR", "CUNG CHÚC TÂN XUÂN", "CHÚC MỪNG NĂM MỚI", "XUÂN ẤT TỴ 2025"]
        text = random.choice(textArr)
        font_path = "./resources/AmericanTypewriter.ttc"
        
        try:
            font = ImageFont.truetype(font_path, 300)
        except Exception as e:
            print(f"Font Error {e}")
            return
        
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x_pos = self.screen_width
        y_pos = (self.screen_height + text_height) // 2 - text_height

        count = 0
        while count < 1:
            background[:, :] = 0
            pil_img = Image.fromarray(background)
            draw = ImageDraw.Draw(pil_img)

            shadow_offset = 10
            shadow_color = (255, 255, 255)
            draw.text((x_pos + shadow_offset, y_pos + shadow_offset), text, font=font, fill=shadow_color)
            draw.text((x_pos, y_pos), text, font=font, fill=(0, 0, 255))

            enhancer = ImageEnhance.Brightness(pil_img)
            pil_img = enhancer.enhance(1.5)
            background = np.array(pil_img)

            x_pos -= 30
            if x_pos + text_width < 0:
                x_pos = self.screen_width
                count += 1

            cv2.namedWindow("Eye", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("Eye", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('Eye', background)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyWindow("Eye") 