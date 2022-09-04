#!/usr/bin/env python3

from std_msgs.msg import Float32MultiArray
from math import pi
import rospy

def _deg2rad(deg):
    return deg*pi/180

class Motion():

    def __init__(self):
        self.lshoulderroll = rospy.Publisher(f'/arm_rotation/shoulder/left/roll', Float32MultiArray, queue_size=1)
        self.lshoulderpitch = rospy.Publisher(f'/arm_rotation/shoulder/left/pitch', Float32MultiArray, queue_size=1)
        self.rshoulderroll = rospy.Publisher(f'/arm_rotation/shoulder/right/roll', Float32MultiArray, queue_size=1)
        self.rshoulderpitch = rospy.Publisher(f'/arm_rotation/shoulder/right/pitch', Float32MultiArray, queue_size=1)
        self.hpitch = rospy.Publisher('/head_rotation/pitch', Float32MultiArray, queue_size=2)
        self.hyaw = rospy.Publisher('/head_rotation/yaw', Float32MultiArray, queue_size=2)
        self.relbowroll = rospy.Publisher(f'/arm_rotation/elbow/right/roll', Float32MultiArray, queue_size=1)
        self.relbowyaw = rospy.Publisher(f'/arm_rotation/elbow/right/yaw', Float32MultiArray, queue_size=1)
        self.lelbowroll = rospy.Publisher(f'/arm_rotation/elbow/left/roll', Float32MultiArray, queue_size=1)
        self.lelbowyaw = rospy.Publisher(f'/arm_rotation/elbow/left/yaw', Float32MultiArray, queue_size=1)

    def start(self):
        rospy.init_node('motion', anonymous=True)
        rospy.spin()

    def arm_shoulder(self, pitch, roll, speed=1, left=False):
        msg1 = Float32MultiArray()
        msg2 = Float32MultiArray()
        pitch = _deg2rad(pitch)
        roll = _deg2rad(roll)

        msg1.data = [roll, speed]
        msg2.data = [pitch, speed]

        if left:
            self.lshoulderroll.publish(msg1)
            self.lshoulderpitch.publish(msg2)
        else:
            self.rshoulderroll.publish(msg1)
            self.rshoulderpitch.publish(msg2)

    def arm_elbow(self, yaw, roll, speed=1, left=False):
        msg1 = Float32MultiArray()
        msg2 = Float32MultiArray()
        yaw = _deg2rad(yaw)
        roll = _deg2rad(roll)

        msg1.data = [roll, speed]
        msg2.data = [yaw, speed]

        if left:
            self.lelbowroll.publish(msg1)
            self.lelbowyaw.publish(msg2)
        else:
            self.relbowroll.publish(msg1)
            self.relbowyaw.publish(msg2)

    def head(self, pitch, yaw, speed=1):
        msg1 = Float32MultiArray()
        msg2 = Float32MultiArray()

        pitch = _deg2rad(pitch)
        yaw = _deg2rad(yaw)

        msg1.data = [pitch, speed]
        msg2.data = [yaw, speed]

        self.hpitch.publish(msg1)
        self.hyaw.publish(msg2)



