import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
from pushbullet import Pushbullet
import RPi.GPIO as GPIO
import time
from collections import Counter

# GPIO Pins
TRIGGER_PIN = 23
ECHO_PIN = 24

# GPIO Setups
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Insert pushbullet API key here
pb = Pushbullet("KEY_HERE")

# Insert your RPI IP address here
RPI_IP = "IP_HERE"

# Title and message
title = "Motion Detected!"
message = "Pet Surveillance system has detected motion! Check it out at the \
following link if on the same network as the sytem: http://" + RPI_IP + ":8000/"

# Returns the average for lists
def avg(list):
    return sum(list) / len(list) 

# Returns the distance in CM from the UDS.
def distance():
    time.sleep(0.1)
    # Trigger set to high to create bursts.
    GPIO.output(TRIGGER_PIN, True)
    
    # Wait 0.01ms and set Trigger to low.
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)
 
    # Record time of sending bursts.
    while GPIO.input(ECHO_PIN) == 0:
        SentTime = time.time()

    # Record time of bursts returning.
    while GPIO.input(ECHO_PIN) == 1:
        RecieveTime = time.time()

    # Determine time taken to recieve response.
    ResponseTime = RecieveTime - SentTime

    # Determine distance by multiplying with speed of sound
    # divided by 2 as we have the time to and from the target.
    # Returns distance in cm.
    Distance = (ResponseTime * 34300) / 2
    return Distance
        
# Finds threshold number used for filtering insignificant distance changes caused by
# incorrect readings from sensor. Current formula is most common distance divided by 7.5.
def create_threshold(calib_list):
    counter = Counter(calib_list)
    mode_distance = counter.most_common(1)[0][0]
    change_threshold = mode_distance / 7.5
    
    return change_threshold
    
# Looping over functions reading distance and adjusting LED until keyboard interrupt.
try:
    history = []
    avg_list = []
    calib_list = []
    
    # Performs some base line calibrations and determines the change_threshold value.
    print("Sensor calibrating...")
    for x in range(120):
        CurrDist = distance()
        calib_list.append(int(CurrDist))
    
    change_threshold = create_threshold(calib_list)
    print("Sensor calibrated and active \n")
    while 1:
        # Retrieve distance and add to history list
        CurrDist = distance()
        history.append(CurrDist)
        
        # At 100 entries, remove the oldest entry. Also take the average of the history
        # list and add it to our 'avg_list'. 
        if len(history) >= 100:
            history.pop(0)
            history_avg = avg(history)
            avg_list.append(history_avg)
            
            # Repeat the list entry limiting above for 50 entries in our 'avg_list' and
            # if the difference between the max and min value is greater than  
            # the change_threshold, send a notification.
            if len(avg_list) >= 50:
                avg_list.pop(0)
                if (max(avg_list) - min(avg_list)) > change_threshold:
                    print("Object Detected")
                    
                    pb.push_note(title, message)
                    history.clear()
                    avg_list.clear()
                    GPIO.cleanup()
                    print("Sensor deactivated...\n")
                    break
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print("ended")