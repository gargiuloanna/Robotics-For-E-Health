#!/usr/bin/env python
from naoqi import ALProxy
from optparse import OptionParser
from nao_nodes.srv import Text2Speech
import rospy

class Text2SpeechNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.tts = ALProxy("ALTextToSpeech", ip, port)
        self.tts.setParameter("speed", 100)

    def say(self, msg):
        try:
            self.tts.say('\\rspd=80\\' + '\\vol=100\\' + msg.speech, "English") #rspd is the word/minute rate while vol is the volume
        except:
            self.tts = ALProxy("ALTextToSpeech", self.ip, self.port)
            self.tts.say('\\rspd=80\\' + '\\vol=100\\' + msg.speech, "English") #rspd is the word/minute rate while vol is the volume
        return "ACK"
    
    def start(self):
        rospy.init_node("text2speech_node", anonymous = True)
        rospy.Service('tts', Text2Speech, self.say)

        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        ttsnode = Text2SpeechNode(options.ip, int(options.port))
        ttsnode.start()
    except rospy.ROSInterruptException:
        pass
