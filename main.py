from utils.screen import init_screen
from utils.logger import Logger
from modules.camera import CameraDetector
from modules.audio import AudioManager
from modules.display import DisplayManager
from modules.emotions import EmotionManager
from modules.sensor import SensorDetector
import time
import random

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
        audio = AudioManager()
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
            
            # Check if enough time has passed since last detection
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
            
            time.sleep(0.1)  # Reduced sleep time for more responsive detection
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        logger.info("=== Application Terminated ===")
        exit(0)

if __name__ == '__main__':
    main()
