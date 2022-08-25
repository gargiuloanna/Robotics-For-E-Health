#!/usr/bin/env python
import qi
import argparse
import sys
import time
import numpy as np
from optparse import OptionParser
import rospy
from std_msgs.msg import Int16MultiArray




class SoundProcessingModule(object):
    """
    A simple get signal from the front microphone of Nao & calculate its rms power.
    It requires numpy.
    """

    def __init__(self, app, callback):
        """
        Initialise services and variables.
        """
        super(SoundProcessingModule, self).__init__()
        app.start()
        session = app.session

        # Get the service ALAudioDevice.
        self.audio_service = session.service("ALAudioDevice")
        self.module_name = "SoundProcessingModule"
        self.callback = callback

    def startProcessing(self, sr = 16000, mic_id = 3, deinterleaved=0):
        """
        Start processing
        """
        # ask for the front microphone signal sampled at 16kHz
        # if you want the 4 channels call setClientPreferences(self.module_name, 48000, 0, 0)
        self.audio_service.setClientPreferences(self.module_name, sr, mic_id, deinterleaved)
        self.audio_service.subscribe(self.module_name)        
    
    def stopProcessing(self):
        self.audio_service.unsubscribe(self.module_name)

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        # convert inputBuffer to signed integer as it is interpreted as a string by python
        self.callback(self.convertStr2SignedInt(inputBuffer))

    def convertStr2SignedInt(self, data) :
        """
        This function takes a string containing 16 bits little endian sound
        samples as input and returns a vector containing the 16 bits sound
        samples values converted between -1 and 1.
        """

        dt = np.dtype(np.int16)
        dt = dt.newbyteorder('<')
        data = np.frombuffer(data, dtype=dt) 

        return data



class PepperAudioSource():
    '''Class defining the interface of a AsyncAudioSource object.
    The methods to implement are:
    
    - **\_\_init\_\_(self, callback)**: constructor that takes as input the callback function and the source settings (sr, frame_len , ...)
    - **start(self)**: this function open the stream
    - **stop(self)**: this function close the open stream
    
    Utils method (already implemented) are:
    - **pcm2float(self, sig, dtype='float32')**
    - **float2pcm(self, sig, dtype='int16')**
    '''
    def __init__(self, callback, pepper_ip, pepper_port, sr = 16000, mic_id = 0, deinterleaved=0):
        self.callback = callback

        try:
            # Initialize qi framework.
            connection_url = "tcp://" + pepper_ip + ":" + str(pepper_port)
            self.app = qi.Application(["SoundProcessingModule", "--qi-url=" + connection_url])

        except RuntimeError as e:
            print(e.message)
            print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\nPlease check your script arguments. Run with -h option for help.")
            sys.exit(1)
        

    def start(self):
        self.sound_processing = SoundProcessingModule(self.app, self.callback)
        self.app.session.registerService("SoundProcessingModule", self.sound_processing)
        self.sound_processing.startProcessing()    
    
    def stop(self):
        self.sound_processing.stopProcessing()



class PepperMicrophoneNode:
    def __init__(self,ip,port):
        self.ip = ip 
        self.port = port
    

    def callback(self, audio_data):
        # Message preparation
        msg = Int16MultiArray()
        msg.data = audio_data.tolist()

        # Message publishing
        self.pub.publish(msg)


    def start(self):
        # Node and publisher initialization
        self.pub = rospy.Publisher('nao_mic_data', Int16MultiArray, queue_size=3)
        rospy.init_node('nao_microphone_node', anonymous=True)#TODO INVERT

        # Stream initialization
        audio_stream = PepperAudioSource(
            self.callback,
            self.ip,
            self.port
        )

        # Open the stream
        audio_stream.start()

        # Wait for closure
        rospy.spin()            
            
        # Close the stream
        audio_stream.stop() 

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--ip", dest="ip", default="10.0.1.207")
    parser.add_option("--port", dest="port", default=9559)
    (options, args) = parser.parse_args()

    try:
        micnode = PepperMicrophoneNode(options.ip, int(options.port))
        micnode.start()
    except rospy.ROSInterruptException:
        pass