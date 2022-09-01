#!/usr/bin/python
from naoqi import ALProxy
from optparse import OptionParser
from std_msgs.msg import Int16
import rospy

class LedsNode:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.led_proxy = ALProxy("ALLeds", ip, port)

    def eye(self, color):
        try:
            self.led_proxy.fadeRGB("FaceLeds", color, 5) #TODO passare timeout
        except:
            self.led_proxy = ALProxy("ALLeds", self.ip, self.port)
            self.led_proxy.fadeRGB("FaceLeds", color, 5)

    def ear(self, color):
        try:
            self.led_proxy.fadeRGB("EarLeds", color, 5)  # TODO passare timeout
        except:
            self.led_proxy = ALProxy("ALLeds", self.ip, self.port)
            self.led_proxy.fadeRGB("EarLeds", color, 5)

    def violet(self, msg):
        self.ear(0x004b0082)
        self.eye(0x004b0082)

    def white(self, msg):
        self.ear(0x00ffffff)
        self.eye(0x00ffffff)

    def set_color(self, msg):
        self.ear(msg.data)
        self.eye(msg.data)

    def start(self):
        rospy.init_node("led_node", anonymous=True)
        rospy.Subscriber("/led/violet", Int16, self.violet)
        rospy.Subscriber("/led/white", Int16, self.white)
        rospy.Subscriber("/led/color", Int16, self.set_color)
        rospy.spin()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.200")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        node = LedsNode(options.ip, int(options.port))
        node.start()
    except rospy.ROSInterruptException:
        pass
