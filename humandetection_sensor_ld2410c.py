import serial
import time
portname = 'COM5'
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

"""
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
"""
"""
            ser.open()
            response = ser.read_until(REPORT_TERMINATOR)
            if len(response) not in [23, 45]:
                continue

            parse_report(response)
            
            
            isTrue = detect_persion()
            ser.close()
            
            if isTrue:
                emotion()
"""