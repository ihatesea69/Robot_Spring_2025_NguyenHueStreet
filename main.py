import os
import sys
import pygame
import time
import random
from utils.screen import init_screen
from utils.logger import Logger
from modules.camera import CameraDetector
from modules.audio import AudioManager
from modules.display import DisplayManager
from modules.emotions import EmotionManager
from modules.sensor import SensorDetector

# Try different audio drivers based on platform
if sys.platform.startswith('linux'):
    try:
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
    except pygame.error:
        try:
            os.environ['SDL_AUDIODRIVER'] = 'pulse'
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
        except pygame.error:
            try:
                os.environ['SDL_AUDIODRIVER'] = 'dummy'
                pygame.mixer.pre_init(44100, -16, 2, 2048)
                pygame.mixer.init()
            except pygame.error as e:
                print(f"Could not initialize audio: {e}")
else:
    # For Windows and other platforms
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()

pygame.mixer.set_num_channels(8)

logger = Logger()

def wave_hand():
    logger.info("Wave hand gesture detected")
    print("Waving hand")

def main():
    try:
        logger.info("Initializing screen...")
        screen_width, screen_height = init_screen()
        
        logger.info("Initializing components...")
        camera = CameraDetector()
        sensor = SensorDetector()
        audio = AudioManager(init_mixer=False)  # Don't initialize mixer again
        display = DisplayManager(screen_width, screen_height, audio)
        emotions = EmotionManager(audio, display)
        
        logger.info("Starting detection threads...")
        camera.start_detection()
        sensor.start_detection()
        
        logger.info("Application ready")
        last_detection_time = 0
        detection_cooldown = 5  # seconds
        
        while True:
            camera_result = camera.get_detection_result()
            sensor_result = sensor.get_detection_result()
            current_time = time.time()
            
            if current_time - last_detection_time >= detection_cooldown:
                if camera_result["human_detected_by_cam"] or sensor_result["human_detected_by_sensor"]:
                    logger.info(f"Human detected - Camera: {camera_result['human_detected_by_cam']}, Sensor: {sensor_result['human_detected_by_sensor']}")
                    
                    if camera_result["waving_hand"]:
                        wave_hand()
                    logger.info("Showing emotion response")
                    emotions.show_emotion()
                    last_detection_time = current_time
                else:
                    if random.choice([True, False]):
                        logger.info("Playing one emotion")
                        emotions.one_emotion()
                    else:
                        logger.info("Displaying scroll text")
                        display.scroll_text()
                    last_detection_time = current_time
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        logger.info("=== Application Terminated ===")
        pygame.mixer.quit()
        exit(0)

if __name__ == '__main__':
    main()
