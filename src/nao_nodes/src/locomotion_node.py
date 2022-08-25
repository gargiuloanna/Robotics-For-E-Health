#!/usr/bin/env python
from naoqi import ALProxy
from optparse import OptionParser
from nao_nodes.srv import *
import rospy

class LocomotionNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.locom = ALProxy("ALMotion", ip, port)
        

    def moveTo(self, msg):
        try:
            self.locom.moveTo(msg.x,msg.y,msg.theta)
        except:
            self.locom = ALProxy("ALMotion", self.ip, self.port)
            self.locom.moveTo(msg.x,msg.y,msg.theta)
        return "ACK"
    
    def start(self):
        rospy.init_node("text2speech_node")
        rospy.Service('locomotion', Locomotion, self.moveTo)

        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        locomotion_node = LocomotionNode(options.ip, int(options.port))
        locomotion_node.start()
    except rospy.ROSInterruptException:
        pass