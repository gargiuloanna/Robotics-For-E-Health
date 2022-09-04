#!/usr/bin/env python3
import rospy
from sound_recognition.msg import SpeechData
from std_msgs.msg import String, Int32
from optparse import OptionParser

from ros_vad import SpeechRecognitionVAD
from speech_recognition import Microphone
from voice_activity_detection import ROSMicrophoneSource

YELLOW = 0x00ffff00

class AudioDetectionNode:

    def __init__(self, test_value=False, timeout=5):
        self.test = test_value
        self.pub = None
        self.timeout = timeout

    def start(self):
        # Node and publisher initialization
        self.pub = rospy.Publisher('audio_detection', SpeechData, queue_size=1)
        rospy.init_node('audio_detection_node')
        self.led_pub = rospy.Publisher('/led/color', Int32, queue_size=1)
        rospy.Subscriber('/listen_start', String, self.listen)
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
            format='int16',
            source=source
        )  

    def listen(self, data):
        rospy.loginfo("Listening...")
        self.led_pub.publish(YELLOW)
        # Get speech data
        self.speechRecognition.calibrate()  # dynamic calibration manages variations in the sound
        speech, timestamps = self.speechRecognition.get_speech_frame(timeout=self.timeout)

        msg = SpeechData()
        # publish nothing
        if speech is None:
            msg.data = [0, 0]
            msg.start_time = rospy.get_time()
            msg.end_time = msg.start_time
        # Message preparing if speech is not none
        else:
            msg.data = speech
            msg.start_time = timestamps[0]
            msg.end_time = timestamps[1]

        # Message publishing
        rospy.loginfo("I'm publishing a record of "+ str(msg.end_time - msg.start_time)+" seconds")
        self.pub.publish(msg)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--test", dest="test", default='0')
    parser.add_option("--timeout", dest="timeout", default=5)
    (options, args) = parser.parse_args()
    test = False if options.test == '0' else True
    speech_detection = AudioDetectionNode(test, int(options.timeout))
    speech_detection.start()
    rospy.spin()

