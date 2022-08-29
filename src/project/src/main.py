#!/usr/bin/env python3

from optparse import OptionParser
import rospy
import sys
import os
from sound_recognition.msg import ClassifiedData
from nao_nodes.srv import Text2Speech, WakeUp
from project.srv import Text2Speech_pyttsx3
from std_msgs.msg import Bool
from nao_motion import Motion

from os import listdir
from os.path import isfile, join
dir_path = os.path.dirname(os.path.realpath(__file__))

Calls = {"cow": os.path.join(dir_path,'example_sounds',"cow.wav"),
         "train": os.path.join(dir_path,'example_sounds',"train.wav"),
         "car": os.path.join(dir_path,'example_sounds',"car.wav"),
         "sheep": os.path.join(dir_path,'example_sounds',"sheep.wav"),
         "dog": os.path.join(dir_path,'example_sounds',"dog.wav")}

calls = {"cow": "mouu",
         "train": "ciuff ciuff",
         "car": "bruuum bruuum",
         "sheep": "beeeeheh",
         "dog": "bau bau"}

yelbow = [-68.6, -88.7, -94.7, 88.7, 68.6]
relbow = [-0.7, -23.5, -17.8, 23.5, 0.7]
pshoulder = [53, 53, 53, 53, 53]
rshoulder = [42.5, 18.1, 2.6, -18.1, -42.5]
left_arm = [True, True, True, False, False]
phead = [5, 5, 5.4, 5, 5]
yhead = [50, 30, 0, -30, -50]
speed = [0.2, 0.15, 0.15, 0.15, 0.2]

def point_to_pos(m, p):
    m.arm_elbow(yelbow[p], relbow[p],left_arm[p], speed[p])
    m.arm_shoulder(pshoulder[p], rshoulder[p], left_arm[p], speed[p])
    m.head(phead[p], yhead[p], speed[p])

def pc_tts(text):
    service = rospy.ServiceProxy('tts_pyttsx3', Text2Speech_pyttsx3)
    _ = service(text)

def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)

def say_call(obj, call):
    rospy.loginfo("pronounce "+call)
    tts(str("This is " + obj) + str(" repeat" + call))

def check(objects):
    for obj in objects:
        if obj not in calls.keys():
            sys.exit(str("Nao doesn't know " + obj))

def wakeup():
    service = rospy.ServiceProxy('wakeup', WakeUp)
    _ = service()

def no_op():
    pass

def parse_args():
    parser = OptionParser()
    parser.add_option("--1", dest="ob1", default="train")
    parser.add_option("--2", dest="ob2", default="cow")
    parser.add_option("--3", dest="ob3", default="sheep")
    parser.add_option("--4", dest="ob4", default="car")
    parser.add_option("--5", dest="ob5", default='dog')
    parser.add_option("--test", dest="test", default='0')
    parser.add_option("--errors", dest="errors", default=3)
    
    (options, args) = parser.parse_args()
    return [options.ob1.lower(), options.ob2.lower(), options.ob3.lower(), options.ob4.lower(),
            options.ob5.lower()], options.test, options.errors

def work_with(obj, m, pos):
    #point_to_pos(m, pos)   
    say_call(obj, calls[obj])
    try:
        data = rospy.wait_for_message('/audio_classification', ClassifiedData)
        rospy.loginfo('predicted class:' + data.hypothesis + ' with ' + str(data.probability) + '% '+ 'of confidence')
        label = data.class_label
    except:
        label = None
        rospy.loginfo("oh no")
    finally:
        stand()
        return label
    
if __name__ == "__main__":
    if False:
        for obj,path in Calls.items():
            if isfile(os.path.join(dir_path,'example_sounds', obj+".wav")):
                print(path)

    objs , test, max_errors= parse_args()
    check(objs)
    if test == '1':
        tts = pc_tts
        rospy.wait_for_service('tts_pyttsx3')
        stand = no_op
    else:
        tts = text_2_speech
        rospy.wait_for_service('tts')
        stand = wakeup
        rospy.wait_for_service('wakeup')

    m = Motion()
    rospy.init_node('main_node', anonymous=True)
    #tts("Hello" + patient + "\\pau=500\\ we're going to do an exercise")
    rospy.Subscriber("/system_ready", Bool)
    rospy.Subscriber("/audio_classification", ClassifiedData)
    errors = 0
    rospy.wait_for_message("/system_ready", Bool)
    while not rospy.is_shutdown():
        for obj in objs:
            while(work_with(obj, m, objs.index(obj))!=obj):
                print()
                errors += 1
                if errors == max_errors:
                    tts('Retry')
                    sys.exit()
        tts('Very well')
        break
