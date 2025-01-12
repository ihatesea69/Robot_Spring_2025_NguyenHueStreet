#!/usr/bin/env python3
from utils.screen import init_screen
from modules.camera import CameraDetector
from modules.audio import AudioManager
from modules.display import DisplayManager
from modules.emotions import EmotionManager
from modules.sensor import SensorDetector
import time
import random

def wave_hand():
    print("Waving hand")

def main():
    screen_width, screen_height = init_screen()
    
    camera = CameraDetector()
    sensor = SensorDetector()
    audio = AudioManager()
    display = DisplayManager(screen_width, screen_height, audio)
    emotions = EmotionManager(audio, display)
    
    # Start both detection threads
    camera.start_detection()
    sensor.start_detection()
    
    try:
        while True:
            camera_result = camera.get_detection_result()
            sensor_result = sensor.get_detection_result()
            
            # Human detected by either camera or sensor
            if camera_result["human_detected_by_cam"] or sensor_result["human_detected_by_sensor"]:
                if camera_result["waving_hand"]:
                    wave_hand()
                emotions.show_emotion()
            else:
                if random.choice([True, False]):
                    emotions.one_emotion()
                else:
                    display.scroll_text()
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        exit(0)

if __name__ == '__main__':
    main()
