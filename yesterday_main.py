import serial
import time
import cv2
import random
import pygame
import threading
import numpy as np
import mediapipe as mp 
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

pygame.init()  # Khởi tạo Pygame để truy vấn thông tin màn hình
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
print(f"Màn hình hiện tại: {screen_width} x {screen_height}")
# Số lần lặp của video và audio 
loop_max = 3

portname = '/dev/cu.usbserial-0001'
ser = serial.Serial()
ser.port = portname
ser.baudrate = 256000
ser.timeout = 3
serial_status = False

HEADER = bytes([0xfd, 0xfc, 0xfb, 0xfa])
TERMINATOR = bytes([0x04, 0x03, 0x02, 0x01])
NULLDATA = bytes([])
REPORT_HEADER = bytes([0xf4, 0xf3, 0xf2, 0xf1])
REPORT_TERMINATOR = bytes([0xf8, 0xf7, 0xf6, 0xf5])

STATE_NO_TARGET = 0
STATE_MOVING_TARGET = 1
STATE_STATIONARY_TARGET = 2
STATE_COMBINED_TARGET = 3
TARGET_NAME = ["no_target", "moving_target", "stationary_target", "combined_target"]

meas = {
    "state": STATE_NO_TARGET,
    "moving_distance": 0,
    "moving_energy": 0,
    "stationary_distance": 0,
    "stationary_energy": 0,
    "detection_distance": 0,
}

# Biến đếm toàn cục
n = 0

# Hàm chạy chữ ngang trên màn hình OpenCV
def scroll_text():
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    textArr = ["HAPPY NEW YEAR", "CUNG CHÚC TÂN XUÂN", "CHÚC MỪNG NĂM MỚI", "XUÂN ẤT TỴ 2025"]
    text = random.choice(textArr)
    font_path = "./resources/AmericanTypewriter.ttc"  # Đường dẫn đến font hỗ trợ tiếng Việt
    
    try:
        # Sử dụng font TrueType hỗ trợ tiếng Việt
        font = ImageFont.truetype(font_path, 300)  # Chọn kích thước font
    except Exception as e:
        print(f"Lỗi khi tải font: {e}")
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

        # Hiển thị video với nền đen
        cv2.imshow("Text Scroll", background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

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
        print("Không thể mở video:", video_path)
        return

    # Lấy kích thước video gốc
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Tạo nền đen có kích thước khung hình phù hợp với màn hình
    background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # Tạo cửa sổ hiển thị video
    window_name = "ROBOT"

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

        # Hiển thị video với nền đen
        cv2.imshow(window_name, background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Người dùng đã nhấn 'q', thoát chương trình.")
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyWindow("Robot")


# Hàm phát âm thanh chúc mừng năm mới
def play_greeting_audio(): 
    greeting_sounds = ['EN', 'CHINA', 'FR', 'JP', 'KR', 'RUS']
    selected_sound = random.choice(greeting_sounds)  # Chọn ngẫu nhiên một âm thanh
    audio_path = 'resources/sound_greeting/HPNewYear_' + selected_sound + '.mp3'

    try:
        sound = pygame.mixer.Sound(audio_path)
        sound.play()
        time.sleep(3)  # Thêm thời gian nghỉ giữa các âm thanh
    except Exception as e:
        print("Lỗi khi phát âm thanh:", e)


# Hàm phát âm thanh
def play_audio(audio_path): 
    try:
        sound = pygame.mixer.Sound(audio_path)
        for i in range(0, loop_max):
            sound.play()
            time.sleep(2.5)
    except Exception as e:
        print("Lỗi khi phát âm thanh:", e)

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
    font_path = "./resources/AmericanTypewriter.ttc"  # Đường dẫn đến font hỗ trợ tiếng Việt
    
    try:
        # Sử dụng font TrueType hỗ trợ tiếng Việt
        font = ImageFont.truetype(font_path, 300)  # Chọn kích thước font
    except Exception as e:
        print(f"Lỗi khi tải font: {e}")
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

        # Hiển thị video với nền đen
        cv2.imshow("Text Scroll", background)

        # Thoát nếu người dùng nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

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

def detect_persion():

    a = 200
    b = 300
    c = 100
    
    if (a<=meas['detection_distance']<=b or a<=meas['moving_distance']<=b ):
        if meas['moving_energy']>a or meas['stationary_energy']==c:
                # print(f"Phát hiện người ở kc {200}-{250}cm")
                return True
    else:
        print(f"{meas['detection_distance']}, {meas['moving_distance']},{meas['moving_energy'],{meas['stationary_energy']}}")
        return False

def parse_report(data):
    global meas
    if len(data) < 23:
        return
    if data[:4] != REPORT_HEADER:
        return
    if data[4] != 0x0d and data[4] != 0x23:
        return
    if data[7] != 0xaa:
        return

    # Parse data
    meas["state"] = data[8]
    meas["moving_distance"] = data[9] + (data[10] << 8)
    meas["moving_energy"] = data[11]
    meas["stationary_distance"] = data[12] + (data[13] << 8)
    meas["stationary_energy"] = data[14]
    meas["detection_distance"] = data[15] + (data[16] << 8)
    detect_persion()

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
    detection_duration = 3  # seconds

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
                print("Xin Chào Bạn")
                return True  # Exit the loop when waving hand is detected

            # cv2.imshow("Camera with Overlay", img)
            prev_time = current_time

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exited by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

def emotion():
    # Khởi tạo pygame mixer
    init_pygame_mixer()

    emotions = [happy, roll, heart, blink]

    selected_emotion = random.choice(emotions)
    print(selected_emotion)
    
    # Chạy video và âm thanh
    display_eye_with_audio(selected_emotion["eye"] + ".mp4", selected_emotion["eye"] + ".MP3")

def continuous_read():
    global n  # Khai báo biến toàn cục
    n = 0  # Khởi tạo biến đếm
    try:
        # time.sleep(3)
        while True:
            if (detect_hello()):
                emotion()
            ser.open()
            response = ser.read_until(REPORT_TERMINATOR)
            if len(response) not in [23, 45]:
                continue

            parse_report(response)
            
            isTrue = detect_persion()
            ser.close()
            if isTrue:
                emotion()
                # time.sleep(1)
            else:
                scroll_text()

            time.sleep(1)  # Optional delay for readability
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()
        exit(0)

if __name__ == '__main__':
    continuous_read()
