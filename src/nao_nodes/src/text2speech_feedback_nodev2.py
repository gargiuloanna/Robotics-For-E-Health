#!/usr/bin/env python
from naoqi import ALProxy, ALBroker, ALModule
from optparse import OptionParser
import rospy
from std_msgs.msg import Bool

# Global variable to store the TTSEventWatcher module instance
tts_event_watcher = None
memory = None

class TTSEventWatcher(ALModule):
    """ An ALModule to react to the ALTextToSpeech/Status event """

    def __init__(self, ip_robot, port_robot):
        super(TTSEventWatcher, self).__init__("tts_event_watcher")
        self.pub = rospy.Publisher("/listen_start", Bool, queue_size=1)
        global memory
        memory = ALProxy("ALMemory", ip_robot, port_robot)
        self.tts = ALProxy("ALTextToSpeech", ip_robot, port_robot)
        memory.subscribeToEvent("ALTextToSpeech/Status",
                                "tts_event_watcher",  # module instance
                                "on_tts_status")  # callback name

    def on_tts_status(self, key, value, message):
        """ callback for event ALTextToSpeech/Status """
        if value[1] == "done":
            rospy.loginfo("listen_start")  # TODO remove
            self.pub.publish(True)

    def start(self):
        rospy.init_node("text2speech_feed", anonymous=True)
        rospy.spin()
        event_broker.shutdown()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--pip", dest="ip", default="10.0.1.201")
    parser.add_option("--pport", dest="port", default=9559)
    (options, args) = parser.parse_args()

    event_broker = ALBroker("event_broker", "0.0.0.0", 0,
                            options.ip, int(options.port))
    global tts_event_watcher
    tts_event_watcher = TTSEventWatcher(options.ip, int(options.port))
    tts_event_watcher.start()