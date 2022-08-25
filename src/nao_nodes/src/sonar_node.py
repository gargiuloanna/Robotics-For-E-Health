#!/usr/bin/env python
import argparse
import sys
from naoqi import ALProxy
import numpy as np
from optparse import OptionParser
import rospy
from std_msgs.msg import Float32MultiArray


class SonarNode:
    def __init__(self,ip,port):
        self.ip = ip 
        self.port = port
        self.memory_proxy = ALProxy("ALMemory", ip, port)
        self.sonar_proxy = ALProxy("ALSonar", ip, port)


    def start(self):
        # Node and publisher initialization
        self.pub = rospy.Publisher('sonar_data', Float32MultiArray, queue_size=3)
        rospy.init_node('sonar_node')

        self.sonar_proxy.subscribe("myApplication")

        r = rospy.Rate(2) # 2hz
        while not rospy.is_shutdown():
            try:
                # Get sonar left first echo (distance in meters to the first obstacle).
                sl = self.memory_proxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")

                # Same thing for right.
                sr = self.memory_proxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")

                # Message preparation
                msg = Float32MultiArray()
                msg.data = [sl, sr]

                # Message publishing
                self.pub.publish(msg)
                r.sleep()
            except:
                self.memory_proxy = ALProxy("ALMemory", ip, port)   
                self.sonar_proxy = ALProxy("ALSonar", ip, port)
                #self.sonar_proxy.subscribe("myApplication") 
            
        self.sonar_proxy.unsubscribe("myApplication")

        

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        sonar_node = SonarNode(options.ip, int(options.port))
        sonar_node.start()
    except rospy.ROSInterruptException:
        pass