#!/usr/bin/env python3
from optparse import OptionParser
import rospy
import sys
from nao_nodes.srv import *

calls = {"cow": "muuu",
         "train": "ciuf ciuf",
         "car": "brum brum",
         "sheep": "beeeee",
         "dog": "bau bau"}

errors = 0


def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)


def say_call(obj, call):
    text_2_speech('This is ' + str(obj))
    rospy.sleep(2)
    text_2_speech('repeat:' + call)


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
    rospy.init_node('main_node')
    rospy.loginfo("===============================================")
    rospy.loginfo("===============================================")
    rospy.loginfo(objs)
    rospy.loginfo("===============================================")
    rospy.loginfo("===============================================")
    #while(errors < 3):
     #   moveToObj(num)
      #  sayCall(obj, call)
       # listen()

