#!/usr/bin/env python3
import rospy
import pyttsx3
from project.srv import Text2Speech_pyttsx3


class Text2SpeechNode_Pyttsx3:

    def __init__(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 150)
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[0].id)
        

    def say(self, msg):
        self.tts.say(msg.speech)
        self.tts.runAndWait()

        return "ACK"
    
    def start(self):
        rospy.init_node("text2speech_pyttsx3_node", anonymous=True)
        rospy.Service('tts_pyttsx3', Text2Speech_pyttsx3, self.say)

        rospy.spin()

if __name__ == "__main__":

    try:
        ttsnode = Text2SpeechNode_Pyttsx3()
        ttsnode.start()
    except rospy.ROSInterruptException:
        pass
