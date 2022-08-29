#!/usr/bin/env python3
from sound_recognition.msg import SpeechData, ClassifiedData
import rospy
import numpy as np
import os
from classifier import Classifier
from std_msgs.msg import String, Bool

from optparse import OptionParser
from scipy.io.wavfile import write
from os import listdir
from os.path import isfile, join
dir_path = os.path.dirname(os.path.realpath(__file__))


class AudioClassificationNode:
    __slots__ = "clf", "pub"

    def start(self, tsh):
        # Server Initialization
        rospy.init_node('audio_classification_node', anonymous=True)
        self.pub = rospy.Publisher("/system_ready", Bool, queue_size=1)
        rospy.loginfo("clf loading...")
        self.pub.publish(False)
        self.clf = Classifier(os.path.join(dir_path, 'sounds'), os.path.join(dir_path,'weights', 'WavLM-Large.pt'),threshold=tsh)
        rospy.loginfo("clf ok")
        self.pub.publish(True)
        self.pub = rospy.Publisher("/audio_classification", ClassifiedData, queue_size=3)
    
        while not rospy.is_shutdown():

            rospy.loginfo("audio classification ready")
            data = rospy.wait_for_message('/audio_detection', SpeechData)
            voice = np.array(data.data)
            if data.start_time == data.end_time:
                sound_label, prob, hyp = None, 1.0, None
            else:
                sound_label, prob, hyp = self.clf.predict(voice)
                
                # Storing file
                onlyfiles = [f for f in listdir(os.path.join(dir_path,'records')) if isfile(
                    join(os.path.join(dir_path,'records'), f))]

                # Check for other file with the same name
                i = len(onlyfiles) + 1

                write(os.path.join(dir_path,'records',
                                    f"{format(i, '04d')}"+hyp+".wav"), 16000, voice.astype(np.int16))
                
            # Message preparing if speech is not none
            msg = ClassifiedData()
            msg.class_label = "None" if sound_label is None else sound_label
            msg.probability = prob
            msg.hypothesis = "None" if hyp is None else hyp
            self.pub.publish(msg)

            rospy.loginfo("audio classification done")


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--threshold", dest="threshold", default='0.75')
    (options, args) = parser.parse_args()
    ssr = AudioClassificationNode()
    try:
        ssr.start(float(options.threshold))
    except rospy.exceptions.ROSInterruptException:
        pass
