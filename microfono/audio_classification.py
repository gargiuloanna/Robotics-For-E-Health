#!/usr/bin/env python3
from microfono.msg import SpeechData, ClassifiedData
import rospy
import numpy as np
import os
from classifier import Classifier

dir_path = os.path.dirname(os.path.realpath(__file__))

class AudioClassificationNode:
    __slots__ = "clf", "pub"

    def start(self):
        # Server Initialization
        rospy.init_node('audio_classification_node', anonymous=True)
        rospy.loginfo("clf loading...")
        self.clf = Classifier(os.path.join(dir_path, 'sounds'), os.path.join(dir_path,
                                                                             'weights', 'WavLM-Large.pt'),
                              threshold=0.9)
        rospy.loginfo("clf ok")
        self.pub = rospy.Publisher("/audio_classification", ClassifiedData, queue_size=3)  # TODO: remove if not used

    def listen(self):
        while not rospy.is_shutdown():
            rospy.loginfo("Waiting...")
            try:
                data = rospy.wait_for_message('/speech_detection', SpeechData, timeout=5)
                voice = np.array(data.data)
                sound_label, prob, hypothesis = self.clf.predict(voice)
            except rospy.exceptions.ROSException:
                sound_label = None
                hypothesis = None
                prob = 1.0

            self.pub.publish(sound_label, prob, hypothesis)
        #return sound_label, prob, hypothesis  #TODO remove


if __name__ == "__main__":
    ssr = AudioClassificationNode()
    try:
        ssr.start()
        ssr.listen()
    except rospy.exceptions.ROSInterruptException:
        pass
