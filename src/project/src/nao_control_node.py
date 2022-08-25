#!/usr/bin/env python3

import rospy
from nao_nodes.srv import *
import numpy as np
import math

from std_msgs.msg import Float32MultiArray, Int16MultiArray
from sensor_msgs.msg import Image

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

# Subscribers

def arm_shoulder(pitch, roll, speed =1, left = False):
    msg1 = Float32MultiArray()
    msg2 = Float32MultiArray()

    msg1.data = [roll,speed]
    msg2.data = [pitch,speed]
    
    if left:
        lroll.publish(msg1)
        lpitch.publish(msg2)
    else:
        rroll.publish(msg1)
        rpitch.publish(msg2)

def head(pitch, yaw, speed =1):

    msg1 = Float32MultiArray()
    msg2 = Float32MultiArray()

    msg1.data = [pitch,speed]
    msg2.data = [yaw,speed]
    
    hpitch.publish(msg1)
    hyaw.publish(msg2)


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
    rospy.wait_for_service('tts') # Waiting for at least one Nao service on

    # Services

    # rest()
    # wakeup()
    # locomotion(1,1,0.5)
    text_2_speech('Start')

    # Subscribers

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
