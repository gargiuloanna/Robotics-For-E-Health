#!/usr/bin/env python3
from queue import Queue
from time import sleep

import numpy as np
import rospy
import soundfile as sf
from sound_recognition.msg import SpeechData
from speech_recognition import Microphone
from std_msgs.msg import Int16MultiArray, String

from ros_vad import SpeechRecognitionVAD

#attaching to the stream coming from the microphone.
#since using the class speechrecognitionvad, the microphone of nao has to be seen as the microphone of the computer

class SpeechDetectionNode:

    def start(self):
        # Node and publisher initialization
        pub = rospy.Publisher('/speech_detection', SpeechData, queue_size=3)
        rospy.init_node('speech_detection_node')            
        rospy.loginfo("SpeechDetection initialized")

        # VAD initialization        
        self.speechRecognition = SpeechRecognitionVAD(
            device_index = None,
            sample_rate = 16000,
            chunk_size = 2720,
            timeout = 0,
            phrase_time_limit = 5,#if put to None, the sounds heard can be of infinite lenght
            calibration_duration = 1, #the method works by using an energy threshold, so to calibrate the threshould the noise energy in
            #the environment has to be known, the calibration factor che used
            format = 'int16',
            source = Microphone( #input stream overidden
                None,
                16000,
                2720
            )
        )


        # Environment calibration
        self.speechRecognition.calibrate()
        self.speechRecognition.get_speech_frame(timeout = 1) #waits till the timeout to go on

        # Loop
        while not rospy.is_shutdown():

            # Get speech data
            #rospy.loginfo("Calibrating...")
            self.speechRecognition.calibrate()#dynamic calibration manages variations in the sound
            #rospy.loginfo("Recording...")
            speech, timestamps = self.speechRecognition.get_speech_frame()
            
            if speech is None:
                continue
            
            # Message preparing if speech is not none
            msg = SpeechData()
            msg.data = speech
            msg.start_time = timestamps[0]
            msg.end_time = timestamps[1]

            # Message publishing
            pub.publish(msg)

            rospy.logdebug('Speech published with timestamps')

if __name__ == '__main__':
    speech_detection = SpeechDetectionNode()
    speech_detection.start()
    