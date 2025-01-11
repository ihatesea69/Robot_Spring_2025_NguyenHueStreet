import time
from LD2410 import LD2410
import logging

# Turn off logging debug for ld2410
logging.getLogger("LD2410").setLevel(logging.CRITICAL)

#SETUP
portname = "COM5"  # PORT TO CONNECT WITH SENSOR, "COM5" for laptop, "/dev/ttys0" for raspberry
sensor = LD2410(port=portname,baud_rate="0700",timeout=3)
logging.getLogger("logging").setLevel(logging.WARNING)

n = 0
a=350 # MIN DISTANT (cm)
b=450   # MAX DISTANT (cm)
thread1= 80 #THREAD1 FOR STATION AND MOVING ENERGY DETECTED
thread2= 100 #THREAD2 FOR STATION AND MOVING ENERGY DETECTED
def print_meas(state,distant,en_station_fromgate):
    global n,a,b, thread1, thread2
    #mgate4,mgate5,mgate6= en_moving_fromgate
    sgate3,sgate4,sgate5,sgate6= en_station_fromgate
# station, moving_dist, moving_energy, stationary_dist, stationary_energy, detection_dist= data
    if(state!=0):
        #DISTANT CHECKING
        print(f"-" * 30)
        if (a<=distant<=b):
            print(f"DETECTED...|__{distant}__|")
        # CONDITION
        if (thread1 <= sgate6 <=thread2 and thread1<=sgate5<=thread2):
            n += 1
            print(f"{n} time of human detection in the range of 4.5m")
            return True
        elif (thread1 <= sgate5 <=thread2 and thread1<=sgate4<=thread2):
            n += 1
            print(f"{n} time of human detection in the range of 4.5m")
            return True
        elif (thread1 <= sgate4 <=thread2 and thread1<=sgate3<=thread2):
            n += 1
            print(f"{n} time of human detection in the range of 4.5m")
            return True
        # elif (thread1<= mgate6 <=thread2 or thread1<=mgate5<=thread2):
        #     n += 1
        #     print(f"{n} time of moving detection in the range of 4.5m")
        #     return True
        # elif (thread1<= mgate5 <=thread2 or thread1<=mgate4<=thread2):
        #     n += 1
        #     print(f"{n} time of moving detection in the range of 3.75m")
        #     return True
        else:
            print(f"---------STATION:|{sgate4}|{sgate5}|{sgate6}|-------")
            #print(f"MOVEMENT:|{mgate4}|{mgate5}|{mgate6}|-------STATION:|{sgate4}|{sgate5}|{sgate6}|")
            return False
    #NOT IN DETECTION AREA   
    else:
        print(f"NO DETECTION!!!, MOVE CLOSE TO DETECTED AREA {a}-{b}")
        print(f"|__{distant}__|")
        return False
    
    
        
def sensor_read():
    global n
    n = 0  
    sensor.enable_engineering_mode()
    try:
        #time.sleep(3)
        sensor.start()  # Connect to sensor
        while True:
            #Collect data from sensor
            data,_,en_station_fromgate =sensor.get_radar_data()
            #en_moving_fromgate=en_moving_fromgate[4:7]
            en_station_fromgate=en_station_fromgate[3:7]
            state=data[0]
            distant=data[5]
            if data is None or len(data)<6:
                print("invalid data")
                continue  
            # if not en_moving_fromgate:
            #     print("invalid moving en ")
            #     continue
            if en_station_fromgate is None:
                print("invalid station en ")
                continue   
            result=print_meas(state,distant,en_station_fromgate)
            if result and n ==5:
                print("Detection complete")
                n=0
                break
            #delay to educe data processing load
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStop by user")
    finally:
            sensor.disable_engineering_mode()
            sensor.stop()
            print(f"Closed!!! {portname}.")

    return True


if __name__ == "__main__":
    sensor_read()
    
