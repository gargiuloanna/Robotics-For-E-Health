#!/usr/bin/env python
from naoqi import ALProxy
from optparse import OptionParser
from nao_nodes.srv import *
import rospy

class AudioPlayerNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.audioPlay = ALProxy("ALAudioPlayer", ip, port)
        

    def play(self, msg):
        try:
            fileId = self.audioPlay.loadFile(msg.path)
            self.audioPlay.play(fileId, _async=False)
        except:
            self.audioPlay = ALProxy("ALAudioPlayer", self.ip, self.port)
            fileId = self.audioPlay.loadFile(msg.path)
            self.audioPlay.play(fileId, _async=False)
        return "ACK"
    
    def start(self):
        rospy.init_node("audio_player_node")
        rospy.Service('audio_play', AudioPlayer, self.play)

        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        playnode = AudioPlayerNode(options.ip, int(options.port))
        playnode.start()
    except rospy.ROSInterruptException:
        pass