#!/usr/bin/python
from naoqi import ALProxy
from optparse import OptionParser
from std_msgs.msg import Float32MultiArray
import rospy

class HandMotionNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.motion_proxy = ALProxy("ALMotion", ip, port)

    def lhand(self, msg):
        try:
            self.motion_proxy.openHand("LHand")
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.openHand("LHand")
    
    def rhand(self, msg):
        try:
            self.motion_proxy.openHand("RHand")
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.openHand("RHand")
    

    def start(self):
        rospy.init_node("hand_motion_node")
        rospy.Subscriber("/arm_rotation/hand/left", Float32MultiArray, self.lhand)
        rospy.Subscriber("/arm_rotation/hand/right", Float32MultiArray, self.rhand)

        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = HandMotionNode(options.ip, int(options.port))
        node.start()
    except rospy.ROSInterruptException:
        pass
