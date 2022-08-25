#!/usr/bin/env python3
from sound_recognition.msg import SpeechData

from std_msgs.msg import String
import argparse
import json

import rospy

from time import time
import numpy as np
import os
from scipy.io.wavfile import write
from os import listdir
from os.path import isfile, join
dir_path = os.path.dirname(os.path.realpath(__file__))

from classifier import Classifier

class SoundRecognitionNode:

    def start(self):
        # Server Initialization
        rospy.init_node('sound_Recognition_node', anonymous=True)

        rospy.loginfo("clf loading...")
        clf = Classifier(os.path.join(dir_path,'sounds'), os.path.join(dir_path,'weights','WavLM-Large.pt'),threshold=0.9)
        rospy.loginfo("clf ok")
        
        while not rospy.is_shutdown():
            rospy.loginfo("Waiting...")
            data = rospy.wait_for_message('/speech_detection',SpeechData)
            voice = np.array(data.data) #integer 16

            # Se ho altri suoni nel support set
            if len(clf) != 0:
                sound_label, prob, hypothesis = clf.predict(voice)#if the probability is not high enough to overcome the treshold, the 
                #hypothesis allow to identify the class
            else:
                # Default
                sound_label = None
                hypothesis = None
                prob = 1.0

            if sound_label is None: #the sound has not been recognized
                print(
                    f"Suono non riconosciuto. Ipotesi: {hypothesis} ({round(prob*100,2)}%)")
            else:
                print(f"Ho sentito: {sound_label} ({round(prob*100,2)}%)")
            
            c = input("Vuoi inserire il nuovo campione (puoi modificare la label)? (S/N):") #nei file salvati
            if c.lower() == 's':
                name = input("Inserisci il nome del suono:").lower()

                # Storing file
                if not os.path.exists(os.path.join(dir_path,'sounds', name)):
                    os.makedirs(os.path.join(dir_path,'sounds', name))

                onlyfiles = [f for f in listdir(os.path.join(dir_path,'sounds', name)) if isfile(
                    join(os.path.join(dir_path,'sounds', name), f))]

                # Check for other file with the same name
                i = len(onlyfiles) + 1
                while i in onlyfiles:
                    i += 1

                write(os.path.join(dir_path,'sounds', name,
                                    f"{format(i, '04d')}.wav"), 16000, voice.astype(np.int16))

                clf._update_support(voice, name) #update support set of the classifier, voice sample (int 16) and class
                

if __name__ == "__main__":
    ssr = SoundRecognitionNode()
    try:
        ssr.start()
    except rospy.exceptions.ROSInterruptException:
        pass
