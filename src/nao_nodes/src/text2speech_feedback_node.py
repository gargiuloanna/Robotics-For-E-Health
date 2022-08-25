#!/usr/bin/env python

import sys
import time
import rospy
from std_msgs.msg import Bool

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

# Global variable to store the speech module instance
Speech = None # deve essere inserito come secondo parametro nella subscribe to event
memory = None

class SpeechModule(ALModule):

    def __init__(self, name, pip, pport):
        ALModule.__init__(self, name)
        # Create a proxy to ALTextToSpeech for later use
        # self.memory = ALProxy("ALMemory", ip, port)
        self.pub = rospy.Publisher("/listen_start", Bool, queue_size=1)
        global memory
        memory = ALProxy("ALMemory", pip, pport)
        # Subscribe to the FaceDetected event:
        memory.subscribeToEvent("ALTextToSpeech/Status", "Speech", "onStatusDone")

    
    def start(self):
        rospy.init_node("text2speech_feed", anonymous=True)
        rospy.spin()
        myBroker.shutdown()

    def onStatusDone(self, name, value):
        if value[1] == "done":
            global memory
            memory.unsubscribeToEvent("ALTextToSpeech/Status", "Speech")
            rospy.loginfo("listen_start") #TODO remove
            self.pub.publish(True)
            memory.subscribeToEvent("ALTextToSpeech/Status", "Speech", "onStatusDone")


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--pip", dest="pip", default="10.0.1.201")
    parser.add_option("--pport", dest="pport", default=9559)
    (options, args) = parser.parse_args()
    pip = options.pip
    pport = int(options.pport)
    myBroker = ALBroker("myBroker", "0.0.0.0", 0, pip, pport)
    # print("QUIII: " + options.ip) #TODO provare
    try:
        Speech = SpeechModule("Speech", pip, pport)
        Speech.start()
    except rospy.ROSInterruptException:
        pass
