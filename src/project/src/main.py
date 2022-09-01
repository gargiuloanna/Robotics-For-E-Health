#!/usr/bin/env python3

from optparse import OptionParser
import rospy
import sys
import os
from sound_recognition.msg import ClassifiedData
from nao_nodes.srv import Text2Speech, WakeUp, AudioPlayer
from project.srv import Text2Speech_pyttsx3
from std_msgs.msg import Bool, String, Int32
from nao_motion import Motion


sounds = {"cow": os.path.join('/home/nao/recordings/audio_recordings','cow.wav'),
         "train": os.path.join('/home/nao/recordings/audio_recordings','train.wav'),
         "car": os.path.join('/home/nao/recordings/audio_recordings','car.wav'),
         "sheep": os.path.join('/home/nao/recordings/audio_recordings','sheep.wav'),
         "dog": os.path.join('/home/nao/recordings/audio_recordings','dog.wav')}


yelbow = [-68.6, -88.7, -94.7, 88.7, 68.6]
relbow = [-0.7, -23.5, -17.8, 23.5, 0.7]
pshoulder = [53, 53, 53, 53, 53]
rshoulder = [42.5, 18.1, 2.6, -18.1, -42.5]
left_arm = [True, True, True, False, False]
phead = [5, 5, 5.4, 5, 5]
yhead = [50, 30, 0, -30, -50]
speed = [0.2, 0.15, 0.15, 0.15, 0.2]

def point_to_pos(m, p):
    m.arm_elbow(yelbow[p], relbow[p],speed[p], left_arm[p])
    m.arm_shoulder(pshoulder[p], rshoulder[p], speed[p], left_arm[p])
    m.head(phead[p], yhead[p], speed[p])

def pc_tts(text):
    service = rospy.ServiceProxy('tts_pyttsx3', Text2Speech_pyttsx3)
    _ = service(text)

def text_2_speech(text):
    service = rospy.ServiceProxy('tts', Text2Speech)
    _ = service(text)

def audio_player(file):
    service = rospy.ServiceProxy('audio_play', AudioPlayer)
    _ = service(file)

def say_call(obj):
    tts(sounds[obj])

def check(objects):
    for obj in objects:
        if obj not in sounds.keys():
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
    parser.add_option("--errors", dest="errors", default='3')
    parser.add_option("--patient", dest="patient", default='Salvatore')

    (options, args) = parser.parse_args()
    return [options.ob1.lower(), options.ob2.lower(), options.ob3.lower(), options.ob4.lower(),
            options.ob5.lower()], options.test, int(options.errors), options.patient

def exit_routine():
    global color_pub
    color_pub.publish(0xffffff)
    stand()

def work_with(obj, m, pos):
    rospy.loginfo("We are working with "+obj)
    point_to_pos(m, pos)  
    rospy.sleep(1)
    global color_pub
    color_pub.publish(0xffffff)
    say_call(obj)
    global pub
    pub.publish("done")
    try:
        data = rospy.wait_for_message('/audio_classification', ClassifiedData)
        rospy.loginfo('Predicted class:' + data.hypothesis + ' with ' + str(data.probability) + '% '+ 'of confidence')
        label = data.class_label
    except:
        label = None
        rospy.loginfo("no sound")
    finally:
        stand()
        return label
    
if __name__ == "__main__":
    
    objs , test, max_errors, patient= parse_args()
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
    tts("Hello\\pau=500\\" + patient + "\\pau=1000\\ we're going to do an exercise")
    pub = rospy.Publisher("/listen_start", String, queue_size=3)
    color_pub = rospy.Publisher("/led/color", Int32, queue_size=1)
    rospy.Subscriber("/system_ready", Bool)
    rospy.Subscriber("/audio_classification", ClassifiedData)
    errors = 0
    rospy.wait_for_message("/system_ready", Bool)
    color_pub.publish(0x00ffffff)
    while not rospy.is_shutdown():
        for obj in objs:
            while(work_with(obj, m, objs.index(obj))!=obj):
                print()
                errors += 1
                color_pub.publish(0x00ff0000)
                if errors == max_errors:
                    tts('Retry')
                    exit_routine()
                    sys.exit()
            color_pub.publish(0x0066ff66)
        tts('Very well')
        break

    exit_routine()
