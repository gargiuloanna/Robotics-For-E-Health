#!/usr/bin/env python3
from sound_recognition.msg import SpeechData, ClassifiedData
import rospy
import numpy as np
import os
from classifier import Classifier
from std_msgs.msg import String,Bool

from scipy.io.wavfile import write
from os import listdir
from os.path import isfile, join
dir_path = os.path.dirname(os.path.realpath(__file__))


class AudioClassificationNode:
    __slots__ = "clf", "pub"

    def start(self):
        # Server Initialization
        rospy.init_node('audio_classification_node', anonymous=True)
        rospy.Subscriber("/listen_start", String, self.callback)
        self.pub = rospy.Publisher("/system_ready", Bool, queue_size=1)
        rospy.loginfo("clf loading...")
        self.pub.publish(False)
        self.clf = Classifier(os.path.join(dir_path, 'sounds'), os.path.join(dir_path,'weights', 'WavLM-Large.pt'),threshold=0.85)#TODO threshold to 0.9
        rospy.loginfo("clf ok")
        self.pub.publish(True)
        self.pub = rospy.Publisher("/audio_classification", ClassifiedData, queue_size=3)  # TODO: remove if not used
        rospy.spin()
    
    def callback(self, value):
        rospy.sleep(2)
        rospy.loginfo("Listening...")
        
        try:
            data = rospy.wait_for_message('/speech_detection', SpeechData, timeout=5)
            voice = np.array(data.data)
            sound_label, prob, hypothesis = self.clf.predict(voice)
            # Storing file
            onlyfiles = [f for f in listdir(os.path.join(dir_path,'records')) if isfile(
                join(os.path.join(dir_path,'records'), f))]

            # Check for other file with the same name
            i = len(onlyfiles) + 1

            write(os.path.join(dir_path,'records',
                                f"{format(i, '04d')}"+hypothesis+".wav"), 16000, voice.astype(np.int16))
            
        except rospy.exceptions.ROSException:
            sound_label = None
            hypothesis = None
            prob = 1.0

        self.pub.publish(sound_label, prob, hypothesis)
        rospy.loginfo("listen_done")
    # return sound_label, prob, hypothesis  #TODO remove


if __name__ == "__main__":
    ssr = AudioClassificationNode()
    try:
        ssr.start()
    except rospy.exceptions.ROSInterruptException:
        pass
