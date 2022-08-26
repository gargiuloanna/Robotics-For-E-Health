#!/usr/bin/python
from naoqi import ALProxy
from optparse import OptionParser
from std_msgs.msg import Float32MultiArray
import rospy

class ArmMotionNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.motion_proxy = ALProxy("ALMotion", ip, port)

    def lshoulder_roll(self, msg):
        try:
            self.motion_proxy.setAngles(["LShoulderRoll"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["LShoulderRoll"], [msg.data[0]], msg.data[1])

    def lshoulder_pitch(self, msg):
        try:
            self.motion_proxy.setAngles(["LShoulderPitch"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["LShoulderPitch"], [msg.data[0]], msg.data[1])
    
    def rshoulder_roll(self, msg):
        try:
            self.motion_proxy.setAngles(["RShoulderRoll"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["RShoulderRoll"], [msg.data[0]], msg.data[1])

    def rshoulder_pitch(self, msg):
        try:
            self.motion_proxy.setAngles(["RShoulderPitch"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["RShoulderPitch"], [msg.data[0]], msg.data[1])

    def lelbow_roll(self, msg):
        try:
            self.motion_proxy.setAngles(["LELbowRoll"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["LElbowRoll"], [msg.data[0]], msg.data[1])

    def lelbow_yaw(self, msg):
        try:
            self.motion_proxy.setAngles(["LElbowYaw"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["LElbowYaw"], [msg.data[0]], msg.data[1])

        # Right Elbow Movements

    def relbow_roll(self, msg):
        try:
            self.motion_proxy.setAngles(["RElbowRoll"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["RElbowRoll"], [msg.data[0]], msg.data[1])

    def relbow_yaw(self, msg):
        try:
            self.motion_proxy.setAngles(["RElbowYaw"], [msg.data[0]], msg.data[1])
        except:
            self.motion_proxy = ALProxy("ALMotion", self.ip, self.port)
            self.motion_proxy.setAngles(["RElbowYaw"], [msg.data[0]], msg.data[1])

    def start(self):
        rospy.init_node("arm_motion_node", anonymous=True)
        rospy.Subscriber("/arm_rotation/shoulder/left/roll", Float32MultiArray, self.lshoulder_roll)
        rospy.Subscriber("/arm_rotation/shoulder/left/pitch", Float32MultiArray, self.lshoulder_pitch)
        rospy.Subscriber("/arm_rotation/shoulder/right/roll", Float32MultiArray, self.rshoulder_roll)
        rospy.Subscriber("/arm_rotation/shoulder/right/pitch", Float32MultiArray, self.rshoulder_pitch)
        rospy.Subscriber("/arm_rotation/elbow/right/roll", Float32MultiArray, self.relbow_roll)
        rospy.Subscriber("/arm_rotation/elbow/right/yaw", Float32MultiArray, self.relbow_yaw)
        rospy.Subscriber("/arm_rotation/elbow/left/roll", Float32MultiArray, self.lelbow_roll)
        rospy.Subscriber("/arm_rotation/elbow/left/yaw", Float32MultiArray, self.lelbow_yaw)

        rospy.spin()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = ArmMotionNode(options.ip, int(options.port))
        node.start()
    except rospy.ROSInterruptException:
        pass
