from LD2410 import LD2410
import logging
import time
import threading
from utils.logger import Logger

class SensorDetector:
    def __init__(self, port="COM5"):
        self.portname = port
        self.detection_result = {"human_detected_by_sensor": False}
        self.detection_lock = threading.Lock()
        self.logger = Logger()
        
        # Disable all logging from LD2410 and other loggers
        logging.getLogger("LD2410").setLevel(logging.CRITICAL)
        logging.getLogger().setLevel(logging.CRITICAL)  # Root logger
        logging.getLogger("logging").setLevel(logging.CRITICAL)
        
        # Only log our application messages
        self.logger.info(f"Initializing sensor on port {port}")
        
        try:
            self.sensor = LD2410(port=self.portname, baud_rate="0700", timeout=3)
        except Exception as e:
            self.logger.error(f"Failed to initialize sensor: {e}")
        
        # Configure sensor parameters
        self.n = 0
        self.a = 350  # MIN DISTANT (cm)
        self.b = 450  # MAX DISTANT (cm)
        self.thread1 = 80  # THREAD1 FOR STATION AND MOVING ENERGY DETECTED
        self.thread2 = 100  # THREAD2 FOR STATION AND MOVING ENERGY DETECTED

    def start_detection(self):
        self.sensor_thread = threading.Thread(target=self._sensor_detection_thread, daemon=True)
        self.sensor_thread.start()

    def get_detection_result(self):
        with self.detection_lock:
            return self.detection_result.copy()

    def _check_detection(self, state, distant, en_station_fromgate):
        sgate3, sgate4, sgate5, sgate6 = en_station_fromgate

        if state != 0:
            if (self.thread1 <= sgate6 <= self.thread2 and self.thread1 <= sgate5 <= self.thread2):
                self.n += 1
                return True
            elif (self.thread1 <= sgate5 <= self.thread2 and self.thread1 <= sgate4 <= self.thread2):
                self.n += 1
                return True
            elif (self.thread1 <= sgate4 <= self.thread2 and self.thread1 <= sgate3 <= self.thread2):
                self.n += 1
                return True
        return False

    def _sensor_detection_thread(self):
        self.sensor.enable_engineering_mode()
        try:
            self.sensor.start()
            while True:
                data, _, en_station_fromgate = self.sensor.get_radar_data()
                en_station_fromgate = en_station_fromgate[3:7]
                
                if data is None or len(data) < 6:
                    continue
                if en_station_fromgate is None:
                    continue

                state = data[0]
                distant = data[5]
                
                detection = self._check_detection(state, distant, en_station_fromgate)
                
                with self.detection_lock:
                    self.detection_result = {
                        "human_detected_by_sensor": detection
                    }
                
                if detection and self.n >= 5:
                    self.n = 0
                
                time.sleep(0.1)

        except Exception as e:
            print(f"Sensor detection error: {e}")
        finally:
            self.sensor.disable_engineering_mode()
            self.sensor.stop() 