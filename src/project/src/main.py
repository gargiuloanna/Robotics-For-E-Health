#!/usr/bin/env python3

from optparse import OptionParser
import rospy
import sys
from sound_recognition.msg import ClassifiedData
from nao_nodes.srv import Text2Speech, WakeUp
from project.srv import Text2Speech_pyttsx3
from std_msgs.msg import Bool
from nao_motion import Motion

calls = {"cow": "mouu",
         "train": "ciuff ciuff",
         "car": "bruuum bruuum",
         "sheep": "beeeeheh",
         "dog": "bau bau"}

def our_tts(text):
    service = rospy.ServiceProxy('tts_pyttsx3', Text2Speech_pyttsx3)
    _ = service(text)


def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)


def say_call(obj, call):
    tts(str("This is " + obj) + str(" repeat" + call))


def check(objects):
    for obj in objects:
        if obj not in calls.keys():
            sys.exit(str("Nao doesn't know " + obj))

def wakeup():
    service = rospy.ServiceProxy('wakeup', WakeUp)
    _ = service()

def parse_args():
    parser = OptionParser()
    parser.add_option("--1", dest="ob1", default="train")
    parser.add_option("--2", dest="ob2", default="cow")
    parser.add_option("--3", dest="ob3", default="sheep")
    parser.add_option("--4", dest="ob4", default="car")
    parser.add_option("--5", dest="ob5", default='dog')
    parser.add_option("--test", dest="test", default='0')
    (options, args) = parser.parse_args()
    return [options.ob1.lower(), options.ob2.lower(), options.ob3.lower(), options.ob4.lower(),
            options.ob5.lower()], options.test

def work_with(obj, m, pos):
    #global pub
    if pos == 0:
        m.arm_elbow(-68.6, -0.7, left = True, speed = 0.3)
        m.arm_shoulder(53, 42.5, left = True, speed = 0.3)
        m.head(5, 50, speed = 0.3)
    elif pos == 1:
        m.arm_elbow(-88.7, -23.5, left = True, speed = 0.3)
        m.arm_shoulder(53, 18.1, left = True, speed = 0.3)
        m.head(5, 30, speed = 0.3)
    elif pos == 2:
        m.arm_elbow(-94.7, -17.8, left = True, speed = 0.3)
        m.arm_shoulder(53, 2.6, left = True, speed = 0.3)
        m.arm_elbow(94.7, 17.8, speed = 0.3)
        m.arm_shoulder(53, 2.6, speed = 0.3)
        m.head(5.4, 0, speed = 0.3)
    elif pos == 3:
        m.arm_elbow(88.7, 23.5, speed = 0.3)
        m.arm_shoulder(53, -18.1, speed = 0.3)
        m.head(5, -30, speed = 0.3)
    elif pos == 4:
        m.arm_elbow(68.6, 0.7, speed = 0.3)
        m.arm_shoulder(53, -42.5, speed = 0.3)
        m.head(5, -50, speed = 0.3)
    
    say_call(obj, calls[obj])
    data = rospy.wait_for_message('/audio_classification', ClassifiedData)
    print('predicted class:' + data.hypothesis + ' with ' + str(data.probability) + '% '+ 'of confidence')# TODO remove
    wakeup()
    return data.hypothesis


if __name__ == "__main__":
    objs , test= parse_args()
    check(objs)
    if test == '1':
        tts = our_tts
    else:
        tts = text_2_speech #TODO see if it works with nao
        #tts = rospy.loginfo

    m = Motion()
    rospy.init_node('main_node', anonymous=True)
    # pub = rospy.Publisher("/listen_start",Bool, queue_size=1)
    rospy.Subscriber("/system_ready", Bool)
    rospy.Subscriber("/audio_classification", ClassifiedData)
    errors = 0
    rospy.wait_for_message("/system_ready", Bool)
    while not rospy.is_shutdown():
        for obj in objs:
            while(work_with(obj, m, objs.index(obj))!=obj):
                print("entro nel while del main")
                errors += 1
                if errors == 3:
                    tts('Retry')
                    sys.exit()
        tts('Very well')
        break




