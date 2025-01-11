import time
import cv2
import random
import pygame
import threading
import numpy as np
import mediapipe as mp 
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

pygame.init()  # Khởi tạo Pygame để truy vấn thông tin màn hình
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
print(f"Current Screen : {screen_width} x {screen_height}")
# Số lần lặp của video và audio 
loop_max = 3

# Tạo nền màu đen
black_bg = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

# Tạo cửa sổ và đặt chế độ toàn màn hình
cv2.namedWindow("ALL", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("ALL", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Hiển thị nền đen
cv2.imshow("ALL", black_bg)

# Hàm chạy chữ ngang trên màn hình OpenCV
def scroll_text():
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    textArr = ["HAPPY NEW YEAR", "CUNG CHÚC TÂN XUÂN", "CHÚC MỪNG NĂM MỚI", "XUÂN ẤT TỴ 2025"]
    text = random.choice(textArr)
    #font_path = "./resources/AmericanTypewriter.ttc"  # Đường dẫn đến font hỗ trợ tiếng Việt
    font_path = BASE_DIR / "resources/AmericanTypewriter.ttc"

    
    try:
        # Sử dụng font TrueType hỗ trợ tiếng Việt
        font = ImageFont.truetype(font_path, 300)  # Chọn kích thước font
    except Exception as e:
        print(f"Font Error: {e}")
        return
    
    # Tính toán kích thước chữ
    text_bbox = font.getbbox(text)  # Lấy bounding box của văn bản
    text_width = text_bbox[2] - text_bbox[0]  # Tính chiều rộng của văn bản
    text_height = text_bbox[3] - text_bbox[1]  # Tính chiều cao của văn bản

    # Tạo biến để điều chỉnh vị trí chữ
    global x_pos
    if 'x_pos' not in globals():  # Kiểm tra nếu chưa có biến x_pos
        x_pos = screen_width  # Vị trí bắt đầu của chữ (bên phải màn hình)

    # Vị trí chữ bắt đầu căn giữa
    y_pos = (screen_height + text_height) // 2 - text_height  # Căn giữa theo chiều dọc

    count = 0
    while count < 1:
        # Xóa nền và vẽ chữ vào nền trống
        background[:, :] = 0  # Đặt lại nền đen

        # Tạo đối tượng PIL Image từ frame OpenCV
        pil_img = Image.fromarray(background)
        draw = ImageDraw.Draw(pil_img)

        # Thêm hiệu ứng bóng đổ
        shadow_offset = 10
        shadow_color = (255, 255, 255)  # Màu trắng cho bóng đổ
        draw.text((x_pos + shadow_offset, y_pos + shadow_offset), text, font=font, fill=shadow_color)

        # Vẽ chữ lên nền (màu đỏ cho chữ chính)
        draw.text((x_pos, y_pos), text, font=font, fill=(0, 0, 255))  # Chữ màu xanh

        # Tăng độ sáng của ảnh
        enhancer = ImageEnhance.Brightness(pil_img)  # Tạo enhancer để tăng độ sáng
        pil_img = enhancer.enhance(1.5)  # Tăng độ sáng (1.0 là không thay đổi, >1 sẽ sáng hơn)

        # Chuyển đổi lại sang OpenCV format
        background = np.array(pil_img)

        # Di chuyển chữ từ phải sang trái
        x_pos -= 30
        if x_pos + text_width < 0:  # Nếu chữ đã ra ngoài màn hình, đặt lại vị trí
            x_pos = screen_width
            count += 1

        # Tạo cửa sổ và đặt chế độ toàn màn hình
        cv2.namedWindow("Text", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Text", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # Hiển thị video với nền đen
        cv2.imshow("Text", background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyWindow("Text")

# Hàm khởi tạo pygame mixer trước khi sử dụng
def init_pygame_mixer():
    try:
        pygame.mixer.init()  # Khởi động pygame mixer
        print("Pygame mixer initialized successfully.")
    except Exception as e:
        print("Lỗi khi khởi tạo pygame mixer:", e)

# Hàm hiển thị mắt với âm thanh đồng bộ
def display_eye(video_path):
    # Khởi tạo VideoCapture
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Cannot Open Camera", video_path)
        return
    scale_factor = 0.5
    # Lấy kích thước video gốc
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))*scale_factor
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))*scale_factor

    # Tạo nền đen có kích thước khung hình phù hợp với màn hình
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    loop_count = 0
    while loop_count < loop_max:
        ret, frame = cap.read()  # Đọc từng frame của video
        if not ret:  # Nếu video kết thúc
            loop_count += 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Quay lại frame đầu tiên
            continue

        # Tính toán kích thước khung hình sau khi resize
        aspect_ratio = video_width / video_height
        new_width = min(screen_width, int(aspect_ratio * screen_height))
        new_height = min(screen_height, int(screen_width / aspect_ratio))

        # Resize frame để vừa với không gian màn hình
        resized_frame = cv2.resize(frame, (new_width, new_height))

        # Đặt video vào giữa nền đen
        start_x = (screen_width - new_width) // 2
        start_y = (screen_height - new_height) // 2
        end_x = start_x + new_width
        end_y = start_y + new_height

        # Xóa nền cũ và chèn video vào giữa
        background[:, :] = 0  # Đặt lại nền đen
        background[start_y:end_y, start_x:end_x] = resized_frame

        # Tạo cửa sổ và đặt chế độ toàn màn hình
        cv2.namedWindow("Robot", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Robot", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # Hiển thị video với nền đen
        cv2.imshow("Robot", background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("User has press 'q', exit program!")
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyWindow("Robot")


# Hàm phát âm thanh chúc mừng năm mới
def play_greeting_audio(): 
    greeting_sounds = ['EN', 'CHINA', 'FR', 'JP', 'KR', 'RUS']
    selected_sound = random.choice(greeting_sounds)  # Chọn ngẫu nhiên một âm thanh
    #audio_path = 'resources/sound_greeting/HPNewYear_' + selected_sound + '.mp3'
    audio_path = BASE_DIR / f"resources/sound_greeting/HPNewYear_{selected_sound}.mp3"

    try:
        sound = pygame.mixer.Sound(audio_path)
        sound.play()
        time.sleep(3)  # Thêm thời gian nghỉ giữa các âm thanh
    except Exception as e:
        print("sound error", e)


# Hàm phát âm thanh
def play_audio(audio_path): 
    try:
        sound = pygame.mixer.Sound(audio_path)
        for i in range(0, loop_max):
            sound.play()
            time.sleep(2.5)
    except Exception as e:
        print("sound error", e)

def display_eye_with_audio(video_path, audio_path):
    # Phát âm thanh từ video trong một thread riêng biệt
    audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
    audio_thread.start()

    # Phát video trong khi âm thanh đang phát
    display_eye(video_path)

    # Đợi âm thanh từ video kết thúc
    audio_thread.join()

    # Ngay sau khi audio_thread kết thúc, phát âm thanh chúc mừng
    audio_greating_thread = threading.Thread(target=play_greeting_audio)
    audio_greating_thread.start()

    # Đợi âm thanh chúc mừng kết thúc
    audio_greating_thread.join()

# Hàm chạy chữ ngang trên màn hình OpenCV
def scroll_text():
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    textArr = ["HAPPY NEW YEAR", "CUNG CHÚC TÂN XUÂN", "CHÚC MỪNG NĂM MỚI", "XUÂN ẤT TỴ 2025"]
    text = random.choice(textArr)
    #font_path = "./resources/AmericanTypewriter.ttc"  # Đường dẫn đến font hỗ trợ tiếng Việt
    font_path = BASE_DIR / "resources/AmericanTypewriter.ttc"
    
    try:
        # Sử dụng font TrueType hỗ trợ tiếng Việt
        font = ImageFont.truetype(font_path, 300)  # Chọn kích thước font
    except Exception as e:
        print(f"Font Error {e}")
        return
    
    # Tính toán kích thước chữ
    text_bbox = font.getbbox(text)  # Lấy bounding box của văn bản
    text_width = text_bbox[2] - text_bbox[0]  # Tính chiều rộng của văn bản
    text_height = text_bbox[3] - text_bbox[1]  # Tính chiều cao của văn bản

    # Tạo biến để điều chỉnh vị trí chữ
    global x_pos
    if 'x_pos' not in globals():  # Kiểm tra nếu chưa có biến x_pos
        x_pos = screen_width  # Vị trí bắt đầu của chữ (bên phải màn hình)

    # Vị trí chữ bắt đầu căn giữa
    y_pos = (screen_height + text_height) // 2 - text_height  # Căn giữa theo chiều dọc

    count = 0
    while count < 1:
        # Xóa nền và vẽ chữ vào nền trống
        background[:, :] = 0  # Đặt lại nền đen

        # Tạo đối tượng PIL Image từ frame OpenCV
        pil_img = Image.fromarray(background)
        draw = ImageDraw.Draw(pil_img)

        # Thêm hiệu ứng bóng đổ
        shadow_offset = 10
        shadow_color = (255, 255, 255)  # Màu trắng cho bóng đổ
        draw.text((x_pos + shadow_offset, y_pos + shadow_offset), text, font=font, fill=shadow_color)

        # Vẽ chữ lên nền (màu đỏ cho chữ chính)
        draw.text((x_pos, y_pos), text, font=font, fill=(0, 0, 255))  # Chữ màu xanh

        # Tăng độ sáng của ảnh
        enhancer = ImageEnhance.Brightness(pil_img)  # Tạo enhancer để tăng độ sáng
        pil_img = enhancer.enhance(1.5)  # Tăng độ sáng (1.0 là không thay đổi, >1 sẽ sáng hơn)

        # Chuyển đổi lại sang OpenCV format
        background = np.array(pil_img)

        # Di chuyển chữ từ phải sang trái
        x_pos -= 30
        if x_pos + text_width < 0:  # Nếu chữ đã ra ngoài màn hình, đặt lại vị trí
            x_pos = screen_width
            count += 1

        # Tạo cửa sổ và đặt chế độ toàn màn hình
        cv2.namedWindow("Eye", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Eye", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # Hiển thị video với nền đen
        cv2.imshow('Eye', background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyWindow("Eye")

# Định nghĩa các hàm gesture
def gesture_happy():
    return "Hành động: Vẫy tay vui vẻ!"

def gesture_roll():
    return "Hành động: Xoay tròn mắt!"

def gesture_heart():
    return "Hành động: Tạo hình trái tim bằng tay!"

def gesture_blink():
    return "Hành động: Chớp mắt liên tục!"

# Tạo danh sách trạng thái cảm xúc
def create_emotion_dict(eye, gesture):
    return {
        "eye": eye,
        "gesture": gesture
    }

happy = create_emotion_dict("resources/happy/happy", gesture_happy)
roll = create_emotion_dict("resources/roll/roll", gesture_roll)
heart = create_emotion_dict("resources/heart/heart", gesture_heart)
blink = create_emotion_dict("resources/blink/blink", gesture_blink)

def detect_hello():
    mp_drawing_util = mp.solutions.drawing_utils
    mp_hand = mp.solutions.hands
    mp_pose = mp.solutions.pose

    # Initialize Mediapipe
    hands = mp_hand.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5
    )

    # Frame rate control
    prev_time = 0
    fps = 10
    interval = 1 / fps

    # Timer to limit detection to 3 seconds
    start_time = time.time()
    detection_duration = 5  # seconds

    cap = cv2.VideoCapture(1)  # Use camera index 1, change to 0 if necessary
    while cap.isOpened():
        
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Stop after 3 seconds
        if elapsed_time > detection_duration:
            print("Detection timed out.")
            return False

        if current_time - prev_time >= interval:
            success, img = cap.read()
            if not success:
                print("Failed to read frame from camera.")
                break

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(img)
            pose_results = pose.process(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            hand_detected = False
            waving_hand = False

            # Draw hand landmarks and check waving condition
            if hand_results.multi_hand_landmarks:
                for hand in hand_results.multi_hand_landmarks:
                    mp_drawing_util.draw_landmarks(img, hand, mp_hand.HAND_CONNECTIONS)

                    # Check waving condition (thumb and index finger extended)
                    landmarks = hand.landmark
                    if landmarks[4].x > landmarks[3].x and landmarks[8].y < landmarks[6].y:
                        waving_hand = True
            
            # Draw pose landmarks and check if a person is present
            if pose_results.pose_landmarks:
                mp_drawing_util.draw_landmarks(
                    img, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                )
                hand_detected = True
            

            # Stop if waving hand detected
            if hand_detected and waving_hand:
                print("Hello Friends")
                return True  # Exit the loop when waving hand is detected

            # cv2.imshow("Camera with Overlay", img)
            prev_time = current_time

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exited by user.")
            break

    cap.release()
    # cv2.destroyAllWindows()

def one_emotion(): #Hàm này để chạy show 1 con đảo qua đảo lại
    # Khởi tạo pygame mixer
    init_pygame_mixer()

    emotions = [blink]

    selected_emotion = random.choice(emotions)
    print(selected_emotion)
    
    # Chạy video và âm thanh
    display_eye_with_audio(selected_emotion["eye"] + ".mp4", selected_emotion["eye"] + ".MP3")

def emotion(): #Hàm này để chạy show nhiều emotion
    # Khởi tạo pygame mixer
    init_pygame_mixer()

    emotions = [happy, roll, heart]

    selected_emotion = random.choice(emotions)
    print(selected_emotion)
    
    # Chạy video và âm thanh
    display_eye_with_audio(selected_emotion["eye"] + ".mp4", selected_emotion["eye"] + ".MP3")
def XoayCo(): #Hàm này giả lập việc xoay cổ
    while True:
        print("Xoay Co")
        time.sleep(10)  # Đợi 10 giây
def DoTayChao(): #Hàm này giả lập việc Dơ tay chào
    print("Do tay chao")
    
def continuous_read(): #Hàm main
    global n  # Khai báo biến toàn cục
    n = 0  # Khởi tạo biến đếm
    #Sau 5 phút sau cổ
    hello_thread = threading.Thread(target=XoayCo, daemon=True)
    hello_thread.start()
    try:
        #time.sleep(3)
        while True:
            if (detect_hello()): #Nếu nhận diện người thì show các cảm xúc khác nhưng không có đảo mắt
                DoTayChao()
                emotion()
            else: #Random chỉ mỗi cảm xúc đảo mắt + show chữ
                random.choice([one_emotion, scroll_text])()
           
            

            time.sleep(1)  # Optional delay for readability
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        #ser.close()
        exit(0)

if __name__ == '__main__':
    continuous_read()
