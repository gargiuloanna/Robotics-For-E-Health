import sys
import time
import rospy
from std_msgs.msg import Bool

from naoqi import ALProxy
from naoqi import ALModule


from optparse import OptionParser

# Global variable to store the speech module instance
Speech = None


class SpeechModule(ALModule):

    def __init__(self,ip, port, name):
        ALModule.__init__(self, name)
        self.ip = ip
        self.port = port
        # Create a proxy to ALTextToSpeech for later use
        self.memory = ALProxy("ALMemory", ip, port)
        self.pub = rospy.Publisher("/listen_start", Bool, queue_size = 1)
        # Subscribe to the FaceDetected event:
        self.memory.subscribeToEvent("ALTextToSpeech/TextDone",
            "Speech",
            "onTextDone")

    def onTextDone(self, *_args):
        self.pub.publish(True)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()
    # print("QUIII: " + options.ip) #TODO provare

    try:
        SpeechModule(options.ip, int(options.port),"Speech")
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

