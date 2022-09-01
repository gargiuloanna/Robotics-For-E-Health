#!/usr/bin/env python3

import rospy
from nao_nodes.srv import *
#from nao_nodes import text2speech_feedback_node_v2
import numpy as np
import math

from std_msgs.msg import Float32MultiArray, Int16MultiArray
from sensor_msgs.msg import Image

from nao_motion import Motion

import os
from os import listdir
from os.path import isfile, join
dir_path = os.path.dirname(os.path.realpath(__file__))

calls = {"cow": os.path.join(dir_path,'example_sounds',"cow.wav"),
         "train": os.path.join(dir_path,'example_sounds',"train.wav"),
         "car": os.path.join(dir_path,'example_sounds',"car.wav"),
         "sheep": os.path.join(dir_path,'example_sounds',"sheep.wav"),
         "dog": os.path.join(dir_path,'example_sounds',"dog.wav")}

sounds = {"cow": "mouu",
         "train": "ciuff ciuff",
         "car": "bruuum bruuum",
         "sheep": "beeeeheh",
         "dog": "bau bau"}

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
def audio_player(file):
    service = rospy.ServiceProxy('audio_play', AudioPlayer)
    _ = service(file)

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

def hand(open=1,left=False):
    lhand = rospy.Publisher(f'/arm_rotation/hand/left', Float32MultiArray, queue_size=1)
    rhand = rospy.Publisher(f'/arm_rotation/hand/right',Float32MultiArray,queue_size=1)
    msg1 = Float32MultiArray()
    msg1.data = [open]
    if left:
        lhand.publish(msg1)
    else:
        rhand.publish(msg1)

if __name__ == '__main__':
    rospy.init_node('nao_control', anonymous=True)
    
    rospy.wait_for_service('audio_play') # Waiting for at least one Nao service on
    #rospy.wait_for_service('audio_play')
    #for obj,path in calls.items():
        #rospy.loginfo('This is '+ obj +'Repeat: '+ sounds[obj])
        #text_2_speech('This is '+ obj +' \\pau=1000\\ Repeat')
        #if isfile(os.path.join(dir_path,'example_sounds', obj+".wav")):
            #audio_player(path) #raise ServiceExcepition file is not found by AudioPlayer Task created in the loadFile method
            #pass
        #rospy.loginfo("Work with the " + obj + "is done")
        #rospy.sleep(3)
    text_2_speech('The task end now. \\pau=1000\\ Good luck with me.')
    # Services
    audio_player(os.path.join('/home/nao/recordings/audio_recordings',"cow.wav"))
    if False:
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
