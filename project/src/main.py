#!/usr/bin/env python3
from concurrent.futures import thread
from optparse import OptionParser
import rospy
import sys
import pyttsx3
from sound_recognition.msg import ClassifiedData
from nao_nodes.srv import Text2Speech
from std_msgs.msg import Bool

calls = {"cow": "mouu",
         "train": "ciuff ciuff",
         "car": "bruuum bruuum",
         "sheep": "beeeeheh",
         "dog": "bau bau"}

def our_tts(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(text)
    engine.runAndWait()

def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)


def say_call(obj, call):
    tts(str("This is " + obj))
    rospy.sleep(2)
    tts(str("repeat" + call))


def check(objects):
    for obj in objects:
        if obj not in calls.keys():
            sys.exit(str("Nao doesn't know " + obj))


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

def work_with(obj):
    global pub
    say_call(obj, calls[obj])
    #rospy.sleep(x)
    pub.publish(True)
    data = rospy.wait_for_message('/audio_classification', ClassifiedData)
    rospy.loginfo('predicted class:' + data.hypothesis)
    return data.class_label


if __name__ == "__main__":
    objs , test= parse_args()
    check(objs)
    if test == '1':
        tts = our_tts
    else:
        #tts = text_2_speech #TODO see if it works with nao
        tts = rospy.loginfo


    rospy.init_node('main_node', anonymous=True)
    pub = rospy.Publisher("/listen_start",Bool, queue_size=1)
    rospy.Subscriber("/system_ready", Bool)
    rospy.Subscriber("/audio_classification", ClassifiedData)
    errors = 0
    while not rospy.wait_for_message("/system_ready", Bool):
        pass
    while not rospy.is_shutdown():
        for obj in objs:
            while(work_with(obj)!=obj):
                errors += 1
                if errors == 3:
                    tts('Retry')
                    sys.exit()
        tts('Very well')
        break




