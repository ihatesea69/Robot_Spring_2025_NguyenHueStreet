import cv2
import threading
import mediapipe as mp
import time
from utils.logger import Logger

class CameraDetector:
    def __init__(self):
        self.detection_result = {"human_detected_by_cam": False, "waving_hand": False}
        self.detection_lock = threading.Lock()
        self.logger = Logger()
        self.logger.info("Camera detector initialized")
        
    def start_detection(self):
        self.camera_thread = threading.Thread(target=self._camera_detection_thread, daemon=True)
        self.camera_thread.start()
        
    def get_detection_result(self):
        with self.detection_lock:
            return self.detection_result.copy()
            
    def _camera_detection_thread(self):
        mp_drawing_util = mp.solutions.drawing_utils
        mp_hand = mp.solutions.hands
        mp_pose = mp.solutions.pose

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

        cap = cv2.VideoCapture(1)
        prev_time = 0
        fps = 10
        interval = 1 / fps

        try:
            while True:
                current_time = time.time()
                
                if current_time - prev_time >= interval:
                    success, img = cap.read()
                    if not success:
                        print("Failed to read frame from camera.")
                        continue

                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    hand_results = hands.process(img)
                    pose_results = pose.process(img)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                    human_detected = False
                    waving_hand = False

                    if hand_results.multi_hand_landmarks:
                        for hand in hand_results.multi_hand_landmarks:
                            mp_drawing_util.draw_landmarks(img, hand, mp_hand.HAND_CONNECTIONS)
                            landmarks = hand.landmark
                            if landmarks[4].x > landmarks[3].x and landmarks[8].y < landmarks[6].y:
                                waving_hand = True
                    
                    if pose_results.pose_landmarks:
                        mp_drawing_util.draw_landmarks(
                            img, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS
                        )
                        human_detected = True

                    with self.detection_lock:
                        self.detection_result = {
                            "human_detected_by_cam": human_detected,
                            "waving_hand": waving_hand
                        }

                    prev_time = current_time

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"Camera detection error: {e}")
        finally:
            cap.release() 