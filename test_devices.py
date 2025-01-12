import cv2
from LD2410 import LD2410
import time

def test_camera(camera_index=1):
    print(f"\nTesting camera at index {camera_index}...")
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ Cannot open camera at index {camera_index}")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print(f"❌ Cannot read frame from camera at index {camera_index}")
        cap.release()
        return False
        
    print(f"✅ Camera at index {camera_index} is working")
    print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
    cap.release()
    return True

def test_sensor(port="COM5"):
    print(f"\nTesting LD2410 sensor at port {port}...")
    try:
        sensor = LD2410(port=port, baud_rate="0700", timeout=3)
        sensor.enable_engineering_mode()
        sensor.start()
        
        # Try to get data
        data, _, en_station_fromgate = sensor.get_radar_data()
        
        if data is None:
            print(f"❌ Cannot read data from sensor at port {port}")
            return False
            
        print(f"✅ Sensor at port {port} is working")
        print(f"Data received: {data}")
        
        sensor.disable_engineering_mode()
        sensor.stop()
        return True
        
    except Exception as e:
        print(f"❌ Error with sensor at port {port}: {str(e)}")
        return False

def find_working_camera():
    print("\nSearching for available cameras...")
    for i in range(4):  # Test first 4 camera indices
        if test_camera(i):
            print(f"Found working camera at index {i}")
            return i
    print("No working camera found")
    return None

def find_working_sensor():
    print("\nSearching for sensor...")
    ports = ["COM5", "COM4", "COM3", "/dev/ttyUSB0", "/dev/ttyUSB1"]
    for port in ports:
        if test_sensor(port):
            print(f"Found working sensor at port {port}")
            return port
    print("No working sensor found")
    return None

if __name__ == "__main__":
    print("=== Device Testing Utility ===")
    
    # Test current camera
    camera_works = test_camera(1)
    if not camera_works:
        print("\nTrying to find working camera...")
        working_camera = find_working_camera()
        if working_camera is not None:
            print(f"\n💡 Update camera index to {working_camera} in modules/camera.py")
    
    # Test current sensor
    sensor_works = test_sensor("COM5")
    if not sensor_works:
        print("\nTrying to find working sensor...")
        working_port = find_working_sensor()
        if working_port is not None:
            print(f"\n💡 Update sensor port to {working_port} in modules/sensor.py")
    
    if camera_works and sensor_works:
        print("\n✅ All devices are working correctly!")
    else:
        print("\n⚠️ Some devices need configuration!") 