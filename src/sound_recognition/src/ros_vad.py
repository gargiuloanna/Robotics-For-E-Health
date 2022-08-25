import speech_recognition as sr
from speech_recognition import Recognizer, AudioData, AudioSource, WaitTimeoutError

import math
import collections
import audioop
import time
import numpy as np
import os 

class TimedRecognizer(Recognizer):
    
    def listen_timestamp(self, source, timeout=None, phrase_time_limit=None, snowboy_configuration=None, vad=None):
        """
        Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.
        This is done by waiting until the audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking), and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input. The ending silence is not included.
        The ``timeout`` parameter is the maximum number of seconds that this will wait for a phrase to start before giving up and throwing an ``speech_recognition.WaitTimeoutError`` exception. If ``timeout`` is ``None``, there will be no wait timeout.
        The ``phrase_time_limit`` parameter is the maximum number of seconds that this will allow a phrase to continue before stopping and returning the part of the phrase processed before the time limit was reached. The resulting audio will be the phrase cut off at the time limit. If ``phrase_timeout`` is ``None``, there will be no phrase time limit.
        The ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__, an offline, high-accuracy, power-efficient hotword recognition engine. When used, this function will pause until Snowboy detects a hotword, after which it will unpause. This parameter should either be ``None`` to turn off Snowboy support, or a tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``, where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory, and ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).
        This operation will always complete within ``timeout + phrase_timeout`` seconds if both are numbers, either by returning the audio data, or by raising a ``speech_recognition.WaitTimeoutError`` exception.
        """

        self.phrase_threshold = 0.2

        assert isinstance(source, AudioSource), "Source must be an audio source"
        assert source.stream is not None, "Audio source must be entered before listening, see documentation for ``AudioSource``; are you using ``source`` outside of a ``with`` statement?"
        assert self.pause_threshold >= self.non_speaking_duration >= 0
        if snowboy_configuration is not None:
            assert os.path.isfile(os.path.join(snowboy_configuration[0], "snowboydetect.py")), "``snowboy_configuration[0]`` must be a Snowboy root directory containing ``snowboydetect.py``"
            for hot_word_file in snowboy_configuration[1]:
                assert os.path.isfile(hot_word_file), "``snowboy_configuration[1]`` must be a list of Snowboy hot word configuration files"

        seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer))  # number of buffers of non-speaking audio during a phrase, before the phrase should be considered complete
        phrase_buffer_count = int(math.ceil(self.phrase_threshold / seconds_per_buffer))  # minimum number of buffers of speaking audio before we consider the speaking audio a phrase
        non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / seconds_per_buffer))  # maximum number of buffers of non-speaking audio to retain before and after a phrase

        # read audio input for phrases until there is a phrase that is long enough
        elapsed_time = 0  # number of seconds of audio read
        buffer = b""  # an empty buffer means that the stream has ended and there is no data left to read
        while True:
            frames = collections.deque()

            if snowboy_configuration is None:
                # store audio input until the phrase starts
                while True:
                    # handle waiting too long for phrase by raising an exception
                    elapsed_time += seconds_per_buffer
                    if timeout and elapsed_time > timeout:
                        raise WaitTimeoutError("listening timed out while waiting for phrase to start")

                    buffer = source.stream.read(source.CHUNK)
                    
                    if len(buffer) == 0: break  # reached end of the stream
                    frames.append(buffer)
                    if len(frames) > non_speaking_buffer_count:  # ensure we only keep the needed amount of non-speaking buffers
                        frames.popleft()

                    if vad is None:
                        # detect whether speaking has started on audio input
                        energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
                        is_speech = energy > self.energy_threshold
                    else:
                        is_speech = vad.is_speech(buffer)

                    if is_speech: break

                    # dynamically adjust the energy threshold using asymmetric weighted average
                    if self.dynamic_energy_threshold and vad is None:
                        damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
                        target_energy = energy * self.dynamic_energy_ratio
                        self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
            else:
                # read audio input until the hotword is said
                snowboy_location, snowboy_hot_word_files = snowboy_configuration
                buffer, delta_time = self.snowboy_wait_for_hot_word(snowboy_location, snowboy_hot_word_files, source, timeout)
                elapsed_time += delta_time
                if len(buffer) == 0: break  # reached end of the stream
                frames.append(buffer)

            # read audio input until the phrase ends
            pause_count, phrase_count = 0, 0
            phrase_start_time = elapsed_time

            ret_end_time = time.time()
            while True:
                # handle phrase being too long by cutting off the audio
                elapsed_time += seconds_per_buffer
                if phrase_time_limit and elapsed_time - phrase_start_time > phrase_time_limit:
                    break

                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break  # reached end of the stream
                frames.append(buffer)
                phrase_count += 1

                # check if speaking has stopped for longer than the pause threshold on the audio input
                if vad is None:
                    # detect whether speaking has started on audio input
                    energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # unit energy of the audio signal within the buffer
                    is_speech = energy > self.energy_threshold
                else:
                    is_speech = vad.is_speech(buffer)

                if is_speech:
                    pause_count = 0
                    ret_end_time = time.time()
                else:
                    pause_count += 1
                if pause_count > pause_buffer_count:  # end of the phrase
                    break

            # check how long the detected phrase is, and retry listening if the phrase is too short
            phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
            if phrase_count >= phrase_buffer_count or len(buffer) == 0: break  # phrase is long enough or we've reached the end of the stream, so stop listening


        # obtain frame data
        for i in range(pause_count - non_speaking_buffer_count): frames.pop()  # remove extra non-speaking frames at the end
        frame_data = b"".join(frames)

        final_data = AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
        
        ret_start_time = ret_end_time - np.frombuffer(final_data.get_raw_data(), dtype=np.int16).shape[0]/source.SAMPLE_RATE
        return final_data, (ret_start_time, ret_end_time)


class SpeechSource:
    '''Class defining the interface of a SpeechSource object.
    The methods to implement are:
    
    - **\_\_init\_\_(self)**: constructor that takes as input the source settings (sr, timeout , ... )
    - **get_speech_frame(self)**: returns a numpy audio frame related to a voice activity and a tuple (start,end) indicating the timestamps of the voice activity
    - **calibrate(self) **: calibrate the Voice Activity Detection wrt environmental noise
    - **stop(self)**: this function close open streams
    Utils method (already implemented) are:
    - **pcm2float(self, sig, dtype='float32')**
    - **float2pcm(self, sig, dtype='int16')**
    '''
    def __init__(self):
        pass

    def get_speech_frame(self):
        raise NotImplementedError
    
    def pcm2float(self, sig, dtype='float32'):
        """Convert PCM signal to floating point with a range from -1 to 1.
        Use dtype='float32' for single precision.
        Parameters
        ----------
        sig : array_like
            Input array, must have integral type.
        dtype : data type, optional
            Desired (floating point) data type.
        Returns
        -------
        numpy.ndarray
            Normalized floating point data.
        See Also
        --------
        float2pcm, dtype
        """
        sig = np.asarray(sig)
        if sig.dtype.kind not in 'iu':
            raise TypeError("'sig' must be an array of integers")
        dtype = np.dtype(dtype)
        if dtype.kind != 'f':
            raise TypeError("'dtype' must be a floating point type")

        i = np.iinfo(sig.dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (sig.astype(dtype) - offset) / abs_max


    def float2pcm(self, sig, dtype='int16'):
        """Convert floating point signal with a range from -1 to 1 to PCM.
        Any signal values outside the interval [-1.0, 1.0) are clipped.
        No dithering is used.
        Note that there are different possibilities for scaling floating
        point numbers to PCM numbers, this function implements just one of
        them.  For an overview of alternatives see
        http://blog.bjornroche.com/2009/12/int-float-int-its-jungle-out-there.html
        Parameters
        ----------
        sig : array_like
            Input array, must have floating point type.
        dtype : data type, optional
            Desired (integer) data type.
        Returns
        -------
        numpy.ndarray
            Integer data, scaled and clipped to the range of the given
            *dtype*.
        See Also
        --------
        pcm2float, dtype
        """
        sig = np.asarray(sig)
        if sig.dtype.kind != 'f':
            raise TypeError("'sig' must be a float array")
        dtype = np.dtype(dtype)
        if dtype.kind not in 'iu':
            raise TypeError("'dtype' must be an integer type")

        i = np.iinfo(dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (sig * abs_max + offset).clip(i.min, i.max).astype(dtype)

    def calibrate(self):
        raise NotImplementedError
    
    def stop(self):
        raise 

class SpeechRecognitionVAD(SpeechSource):
    '''SpeechRecognitionVAD implements SpeechSource through the use of the SpeechRecognition and PyAudio libraries.
    Extracts audio chunks that contain speech.
    # Arguments
        device_index: int
            Microphone index: index in the list speech_recognition.Microphone.list_microphone_names()
        sample_rate: float 
            Sampling rate - `default None`
        chunk_size: int
            Chunk size (in samples) - `default 1024`
        timeout: float
            Timeout for an input phrase - `default None`
        phrase_time_limit: float
            Input phrase limit - `default None`
        calibration_duration: float
            Time needed to perform the vad calibration - `default 1`
        format: str
            Audio array dtype: 'int16' or 'float32' - `default 'int16'`
        source: speech_recognition.AudioSource
            Audio source: None to use speech_recognition.Microphone. 
        
    For more details refer to the SpeechRecognition and PyAudio libraries docs.
    '''
    def __init__(self, device_index=None, sample_rate=None, chunk_size=1024, timeout=None, phrase_time_limit=None, calibration_duration=1, format='int16', source=None, vad=None):
        self.sr = TimedRecognizer()
        if source is None:
            self.mic = sr.Microphone(device_index, sample_rate, chunk_size)
        else:
            self.mic = source 
            
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.calibration_duration = calibration_duration
        self.format = format
        self.vad = vad

    def get_speech_frame(self, timeout=None):
        # wait for a phrase
        try :
            with self.mic as s:
                speech_data,timestamps = self.sr.listen_timestamp(source=s,timeout=self.timeout if timeout is None else timeout, phrase_time_limit=self.phrase_time_limit, vad=self.vad) 
        except sr.WaitTimeoutError:
            return None, (None,None)

        # bytes to samples
        speech_data = np.frombuffer(speech_data.get_raw_data(), dtype=np.int16)

        # conversion if needed
        if self.format == 'float32':
            speech_data = self.pcm2float(speech_data)
        
        return speech_data, timestamps

    def calibrate(self):
        with self.mic as source:
            self.sr.adjust_for_ambient_noise(source, self.calibration_duration)  

    def stop(self):
        pass
