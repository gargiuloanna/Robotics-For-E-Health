#!/usr/bin/env python
import qi
from optparse import OptionParser
import rospy
from std_msgs.msg import String

tts_event_watcher = None

class SpeechWatcher(object):
    """ A class to react to the ALTextToSpeech/Status event """

    def __init__(self, app):
        super(SpeechWatcher, self).__init__()
        app.start()
        session = app.session
        self.memory = session.service("ALMemory")
        #self.tts = session.service("ALTextToSpeech")
        self.subscriber = self.memory.subscriber("ALTextToSpeech/TextDone")
        self.subscriber.signal.connect(self.on_tts_status)
        self.pub = rospy.Publisher("/listen_start", String, queue_size =3)
        # keep this variable in memory, else the callback will be disconnected

    def on_tts_status(self, value):
        rospy.loginfo(str(value))
        if value == 1:
            self.pub.publish(str(value)) #TODO



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--pip", dest="ip", default="10.0.1.200")
    parser.add_option("--pport", dest="port", default=9559)
    (options, args) = parser.parse_args()
    rospy.init_node('tts_feed2')
    # Initialize qi framework
    connection_url = "tcp://" + options.ip + ":" + str(options.port)
    rospy.loginfo("=======================================================================")

    rospy.loginfo(connection_url)
    app = qi.Application(["SpeechWatcher", "--qi-url=" + connection_url])
    tts_event_watcher = SpeechWatcher(app)
    rospy.spin()