#!/usr/bin/python

from naoqi import ALProxy
from optparse import OptionParser
from std_msgs.msg import Int32
import rospy

class LedsNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.led_proxy = ALProxy("ALLeds", ip, port)

    def eye(self, color):
        try:
            self.led_proxy.fadeRGB("FaceLeds", color, 0)
        except:
            self.led_proxy = ALProxy("ALLeds", self.ip, self.port)
            self.led_proxy.fadeRGB("FaceLeds", color, 0)

    def ear(self, color):
        try:
            self.led_proxy.fadeRGB("EarLeds", color, 0)
        except:
            self.led_proxy = ALProxy("ALLeds", self.ip, self.port)
            self.led_proxy.fadeRGB("EarLeds", color, 0)
    
    def reset(self, name):
        try:
            self.led_proxy.reset(name)
        except:
            self.led_proxy = ALProxy("ALLeds", self.ip, self.port)
            self.led_proxy.reset(name)

    def set_color(self, msg):
        self.reset("EarLeds")
        self.reset("FaceLeds")
        self.ear(msg.data)
        self.eye(msg.data)

    def start(self):
        rospy.init_node("led_node", anonymous=True)
        rospy.Subscriber("/led/color", Int32, self.set_color)
        rospy.spin()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.200")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = LedsNode(options.ip, int(options.port))
        node.start()
        node.reset("FaceLeds") 
        node.reset("EarLeds")   
    except rospy.ROSInterruptException:
        pass
