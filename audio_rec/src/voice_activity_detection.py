#!/usr/bin/env python3
import rospy
from audio_rec.msg import SpeechData
from std_msgs.msg import Int16MultiArray, String
from optparse import OptionParser

from ros_vad import SpeechRecognitionVAD
from speech_recognition import AudioSource
from speech_recognition import Microphone


import numpy as np
from time import sleep
import soundfile as sf
from queue import Queue


class ROSMicrophoneSource(AudioSource):

    def __init__(self, device_index=None, sample_rate=None, chunk_size=2720):
        self.device_index = device_index
        self.format = 8  # 16-bit int sampling
        self.SAMPLE_WIDTH = 2  # size in bytes of each sample (2 = 16 bit -> int16)
        self.SAMPLE_RATE = sample_rate  # sampling rate in Hertz
        self.CHUNK = chunk_size  # number of frames stored in each buffer, window size

        self.audio = None
        self.stream = None

    def __enter__(self):
        self.stream = self.ROSAudioStream()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    class ROSAudioStream:
        def __init__(self):
            self.buffer = None
            rospy.Subscriber('nao_mic_data', Int16MultiArray, self.store)

        def store(self, audio):
            if self.buffer is not None:
                self.buffer.put(np.array(audio.data, dtype='int16').tobytes())

        def read(self, chunk):
            self.buffer = Queue() if self.buffer is None else self.buffer
            return self.buffer.get()


class SpeechDetectionNode:

    def __init__(self, test_value=False):
        self.test = test_value

    def start(self):
        # Node and publisher initialization
        pub = rospy.Publisher('speech_detection', SpeechData, queue_size=3)
        rospy.init_node('speech_detection_node')
        if self.test:
            source = Microphone(None, 16000, 2720)
        else:
            source = ROSMicrophoneSource(None, 16000, 2720)
        # VAD initialization        
        self.speechRecognition = SpeechRecognitionVAD(
            device_index=None,
            sample_rate=16000,
            chunk_size=2720,
            timeout=0,
            phrase_time_limit=5,  # if put to None, the sounds heard can be of infinite lenght
            calibration_duration=1,
            # the method works by using an energy threshold, so to calibrate the threshould the noise energy in
            # the environment has to be known, the calibration factor che used
            format='int16',
            source=source
        )

        # Environment calibration
        self.speechRecognition.calibrate()
        self.speechRecognition.get_speech_frame(timeout=1)  # waits till the timeout to go on

        # Loop
        while not rospy.is_shutdown():

            # Get speech data
            # rospy.loginfo("Calibrating...")
            self.speechRecognition.calibrate()  # dynamic calibration manages variations in the sound
            # rospy.loginfo("Recording...")
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
    parser = OptionParser()
    parser.add_option("--test", dest="test", default='0')
    (options, args) = parser.parse_args()
    test = True if options.test == '1' else False
    speech_detection = SpeechDetectionNode(test)
    speech_detection.start()

