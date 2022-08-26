#!/usr/bin/env python3

import rospy
from nao_nodes.srv import *
import numpy as np
import math

from std_msgs.msg import Float32MultiArray, Int16MultiArray
from sensor_msgs.msg import Image

from nao_motion import Motion

lroll = rospy.Publisher(f'/arm_rotation/shoulder/left/roll', Float32MultiArray, queue_size=1)
lpitch = rospy.Publisher(f'/arm_rotation/shoulder/left/pitch', Float32MultiArray, queue_size=1)
rroll = rospy.Publisher(f'/arm_rotation/shoulder/right/roll', Float32MultiArray, queue_size=1)
rpitch = rospy.Publisher(f'/arm_rotation/shoulder/right/pitch', Float32MultiArray, queue_size=1)

hpitch = rospy.Publisher('/head_rotation/pitch', Float32MultiArray, queue_size=2)
hyaw = rospy.Publisher('/head_rotation/yaw', Float32MultiArray, queue_size=2)


# Publishers
def sonar():
    data = rospy.wait_for_message('sonar_data',Float32MultiArray)
    rospy.loginfo(data.data)

def camera():
    data = rospy.wait_for_message('in_rgb',Image)
    img = np.frombuffer(data.data, dtype=np.uint8).reshape(data.height, data.width, -1)
    
    rospy.loginfo(img[:5,:5,0])

def mic():
    data = rospy.wait_for_message('nao_mic_data',Int16MultiArray)
    rospy.loginfo(data.data[:5])

# Services

def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)

def wakeup():
    service = rospy.ServiceProxy('wakeup', WakeUp)
    _ = service()

def rest():
    service = rospy.ServiceProxy('rest', WakeUp)
    _ = service()

def locomotion(x,y,theta):
    service = rospy.ServiceProxy('locomotion', Locomotion)
    _ = service(x,y,theta)

def move_to_first():
    locomotion(0.0,0.0,-math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.4,0.0,0.0)
    rospy.sleep(1)
    #wakeup()
    locomotion(0.0,0.0,math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.4,0.0,0.0)
    text_2_speech('Macchina')

def move_to_next(text):
    locomotion(0.0,0.0,math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.2,0.0,0.0)
    rospy.sleep(1)
    #wakeup()
    locomotion(0.0,0.0,-math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.2,0.0,0.0)
    rospy.sleep(1)
    #wakeup()
    locomotion(0.0,0.0,-math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.2,0.0,0.0)
    text_2_speech(text)

def move_to_rest():
    locomotion(0.0,0.0,-math.pi)
    #wakeup()
    locomotion(0.4,0.0,0.0)
    rospy.sleep(1)
    #wakeup()
    locomotion(0.0,0.0,math.pi/2)
    #wakeup()
    rospy.sleep(1)
    locomotion(0.4,0.0,0.0)
    #wakeup()
    locomotion(0.0,0.0,math.pi/2)
    text_2_speech('Finito')
    rospy.sleep(1)
    rest()

if __name__ == '__main__':
    rospy.init_node('nao_control', anonymous=True)
    if False:
        rospy.wait_for_service('tts') # Waiting for at least one Nao service on
        text_2_speech('Start')
    # Services

    #rest()
    wakeup()
    # locomotion(1,1,0.5)
    # Subscribers
    m = Motion()
    m.arm_elbow(-68.6, -0.7, left = True)
    m.arm_shoulder(53, 42.5, left = True)
    m.head(5, 50, speed = 0.3)

    rospy.sleep(2)
    wakeup()
    rospy.sleep(2)

    m.arm_elbow(-88.7, -23.5, left = True)
    m.arm_shoulder(53, 18.1, left = True)
    m.head(5, 30, speed = 0.3)

    rospy.sleep(2)
    wakeup()
    rospy.sleep(2)

    m.arm_elbow(-94.7, -17.8, left = True)
    m.arm_shoulder(53, 2.6, left = True)
    m.arm_elbow(94.7, 17.8)
    m.arm_shoulder(53, 2.6)
    m.head(5.4, 0, speed = 0.3)

    rospy.sleep(2)
    wakeup()
    rospy.sleep(2)

    m.arm_elbow(88.7, 23.5)
    m.arm_shoulder(53, -18.1)
    m.head(5, -30, speed = 0.3)

    rospy.sleep(2)
    wakeup()
    rospy.sleep(2)
    
    m.arm_elbow(68.6, 0.7)
    m.arm_shoulder(53, -42.5)
    m.head(5, -50, speed = 0.3)
    





    rospy.spin()
    #rest()
    wakeup()    


    # head(0.2,-0.2, 0.2)
    # arm_shoulder(0.2,-0.2,0.2)
    # rospy.sleep(5)
    # wakeup()
    # rospy.spin()

    # Publishers

    # sonar()
    # camera()
    # mic()
    
    #head(0.2,-0.2, 0.2)
    #text_2_speech('Hey you')
    #rospy.sleep(1)
    #arm_shoulder(0.5,-0.,0.5)
    #arm_shoulder(0.5,-0.,0.5)
    #rospy.sleep(5)
    #wakeup()
    #rospy.spin()
    if False:
        move_to_first()
        rospy.sleep(5)
        move_to_next('Pecora')
        rospy.sleep(5)
        move_to_next('Mucca')
        rospy.sleep(5)
        move_to_next('Cane')
        rospy.sleep(5)
        move_to_next('Treno')
        rospy.sleep(5)
        move_to_rest()


