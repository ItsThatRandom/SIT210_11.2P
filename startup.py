import subprocess
import time

try:
    while True:
        SensorProcess = subprocess.Popen(["python3", "UDSdetection.py"])
        SensorProcess.wait()
        print("Stream activated")
        StreamProcess = subprocess.Popen(["python3", "WebStreaming.py"])
        time.sleep(300)
        StreamProcess.kill()
        print("Stream ended")
    
except KeyboardInterrupt:
    print("Sensor Ended")
    SensorProcess.kill()
    
    try:
        StreamProcess.kill()
        print("Stream Ended")
    except:
        print("Stream Not Started")
    print("All Ended")
