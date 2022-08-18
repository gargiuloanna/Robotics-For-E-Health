#!/usr/bin/env python3
from optparse import OptionParser
import rospy
import sys
import pyttsx3
from microfono.msg import ClassifiedData


calls = {"cow": "muuu",
         "train": "ciuf ciuf",
         "car": "brum brum",
         "sheep": "beeeee",
         "dog": "bau bau"}

errors = 0

def our_tts(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 125)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)


tts = our_tts


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
    (options, args) = parser.parse_args()
    return [options.ob1.lower(), options.ob2.lower(), options.ob3.lower(), options.ob4.lower(),
            options.ob5.lower()]


if __name__ == "__main__":
    objs = parse_args()
    check(objs)
    rospy.init_node('main_node', anonymous=True)
    rospy.Subscriber("/audio_classification", ClassifiedData)
    while not rospy.is_shutdown():
        for obj in objs:
            say_call(obj, calls[obj])
            rospy.loginfo('waiting...')
            data = rospy.wait_for_message('/audio_classification', ClassifiedData)
            class_label = data.class_label
            rospy.loginfo('predicted class:' + class_label)

            if not class_label == obj:
                errors += 1
                if errors == 3:
                    tts('Retry')
                    sys.exit()
        tts('Very well')
        break


