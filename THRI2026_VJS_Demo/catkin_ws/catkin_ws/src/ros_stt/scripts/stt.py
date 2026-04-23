#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import queue
import time
import vosk
import sounddevice as sd

import rospy
import rospkg
from ros_stt.msg import speech_recognition
from std_msgs.msg import String, Bool, Int32

import stt_ros_model_downloader as downloader

class vosk_sr():
    def __init__(self):
        model_name = rospy.get_param('stt/model', "vosk-model-small-en-us-0.15")

        rospack = rospkg.RosPack()
        package_path = rospack.get_path('ros_stt')

        models_dir = os.path.join(package_path, 'models')
        model_path = os.path.join(models_dir, model_name)

        if not os.path.exists(model_path):
            rospy.logwarn(f"model '{model_name}' not found in '{models_dir}', launching downloader...")
            model_downloader = downloader.model_downloader()
            model_downloader.execute()
            model_name = model_downloader.model_to_download

        if not rospy.has_param('stt/model'):
            rospy.set_param('stt/model', model_name)

        # --- State flags ---
        self.tts_status = False
        self.mic_enabled = bool(rospy.get_param('stt/mic_enabled', 0))
        self.accept_audio = True  # gate in callback; set False when stopped
        self.pausing = False      # soft-stop in progress
        self.stop_grace_ms = int(rospy.get_param('~stop_grace_ms', 600))  # how long to finish buffered audio

        # --- Publishers ---
        self.pub_vosk = rospy.Publisher('speech_recognition/vosk_result', speech_recognition, queue_size=10)
        self.pub_final = rospy.Publisher('speech_recognition/final_result', String, queue_size=10)
        self.pub_partial = rospy.Publisher('speech_recognition/partial_result', String, queue_size=10)

        rospy.on_shutdown(self.cleanup)

        self.msg = speech_recognition()
        self.q = queue.Queue()

        # --- Audio device ---
        self.input_dev_num = sd.query_hostapis()[0]['default_input_device']
        if self.input_dev_num == -1:
            rospy.logfatal('No input device found')
            raise ValueError('No input device found, device number == -1')

        device_info = sd.query_devices(self.input_dev_num, 'input')
        self.samplerate = int(device_info['default_samplerate'])
        rospy.set_param('stt/sample_rate', self.samplerate)

        # --- Model ---
        self.model = vosk.Model(model_path)

        # --- Subscribers (once) ---
        rospy.Subscriber('/tts/status', Bool, self.tts_get_status, queue_size=1)
        rospy.Subscriber('speech_recognition/mic_enable', Int32, self.mic_enable_cb, queue_size=1)

    def cleanup(self):
        rospy.logwarn("Shutting down VOSK speech recognition node...")

    def stream_callback(self, indata, frames, time_info, status):
        # Called in audio thread
        if status:
            print(status, file=sys.stderr)
        # Drop audio if not accepting (paused/stopped or TTS speaking)
        if self.accept_audio:
            self.q.put(bytes(indata))

    def tts_get_status(self, msg):
        self.tts_status = msg.data
        # If TTS starts speaking, stop accepting new audio immediately
        if self.tts_status:
            self.accept_audio = False

    def mic_enable_cb(self, msg):
        want_enable = (int(msg.data) != 0)
        if want_enable and not self.mic_enabled:
            # Resume
            self.mic_enabled = True
            self.accept_audio = True
            self.pausing = False
            rospy.loginfo("Mic ENABLED")
        elif (not want_enable) and self.mic_enabled:
            # Request a graceful stop
            self.mic_enabled = False
            self.pausing = True
            # keep accepting audio during pausing so queued frames can be processed
            self.accept_audio = True
            rospy.loginfo("Mic DISABLE requested (graceful pause)")

    def _drain_queue_nowait(self):
        """Empty queue without blocking."""
        drained = 0
        try:
            while True:
                self.q.get_nowait()
                drained += 1
        except queue.Empty:
            pass
        return drained

    def speech_recognize(self):
        try:
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=16000,
                device=self.input_dev_num,
                dtype='int16',
                channels=1,
                callback=self.stream_callback
            ):
                rospy.loginfo('Audio stream started')
                rec = vosk.KaldiRecognizer(self.model, self.samplerate)
                print("Vosk is ready to listen!")

                # loop vars
                have_partial = False
                partial_text = "unk"

                rate = rospy.Rate(200)
                while not rospy.is_shutdown():

                    # --- If TTS is speaking: ignore everything, reset recognizer, drop queue ---
                    if self.tts_status:
                        self.accept_audio = False
                        self._drain_queue_nowait()
                        rec.Reset()
                        rate.sleep()
                        continue

                    # --- Graceful stop (pausing): finish buffered audio, then finalize & stop ---
                    if self.pausing:
                        deadline = time.monotonic() + (self.stop_grace_ms / 1000.0)
                        # Process whatever is still in the queue until grace time expires
                        while time.monotonic() < deadline:
                            try:
                                data = self.q.get_nowait()
                            except queue.Empty:
                                # small sleep to allow last frames to arrive
                                time.sleep(0.01)
                                continue

                            if rec.AcceptWaveform(data):
                                # Final chunk recognized during pause; publish final
                                result_text = json.loads(rec.FinalResult()).get("text", "")
                                if len(result_text) > 2:
                                    self.msg.isSpeech_recognized = True
                                    self.msg.time_recognized = rospy.Time.now()
                                    self.msg.final_result = result_text
                                    self.msg.partial_result = "unk"
                                    self.pub_vosk.publish(self.msg)
                                    self.pub_final.publish(result_text)
                                rec.Reset()

                        # After grace window, ask Vosk to flush internal buffers
                        final_flush = json.loads(rec.FinalResult()).get("text", "")
                        if len(final_flush) > 2:
                            self.msg.isSpeech_recognized = True
                            self.msg.time_recognized = rospy.Time.now()
                            self.msg.final_result = final_flush
                            self.msg.partial_result = "unk"
                            self.pub_vosk.publish(self.msg)
                            self.pub_final.publish(final_flush)

                        # Now fully stop: stop accepting, clear queue, reset recognizer
                        self.accept_audio = False
                        self._drain_queue_nowait()
                        rec.Reset()
                        self.pausing = False
                        rate.sleep()
                        continue

                    # --- If mic disabled (and not pausing): just idle ---
                    if not self.mic_enabled:
                        self.accept_audio = False
                        self._drain_queue_nowait()
                        rec.Reset()
                        rate.sleep()
                        continue

                    # --- Normal operation (mic enabled) ---
                    self.accept_audio = True
                    try:
                        data = self.q.get(timeout=0.05)
                    except queue.Empty:
                        rate.sleep()
                        continue

                    if rec.AcceptWaveform(data):
                        # Final result
                        result_text = json.loads(rec.FinalResult()).get("text", "")
                        if len(result_text) > 2:
                            self.msg.isSpeech_recognized = True
                            self.msg.time_recognized = rospy.Time.now()
                            self.msg.final_result = result_text
                            self.msg.partial_result = "unk"
                            self.pub_vosk.publish(self.msg)
                            self.pub_final.publish(result_text)
                        rec.Reset()
                        have_partial = False
                        partial_text = "unk"
                    else:
                        # Partial result (only publish if non-empty)
                        ptxt = json.loads(rec.PartialResult()).get("partial", "")
                        if ptxt:
                            have_partial = True
                            partial_text = ptxt
                            self.msg.isSpeech_recognized = False
                            self.msg.time_recognized = rospy.Time.now()
                            self.msg.final_result = "unk"
                            self.msg.partial_result = partial_text
                            self.pub_vosk.publish(self.msg)
                            self.pub_partial.publish(partial_text)

                    rate.sleep()

        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
        except KeyboardInterrupt:
            rospy.loginfo("Stopping the VOSK speech recognition node...")
            rospy.sleep(1)
            print("node terminated")

if __name__ == '__main__':
    try:
        rospy.init_node('vosk', anonymous=False)
        rec = vosk_sr()
        rec.speech_recognize()
    except (KeyboardInterrupt, rospy.ROSInterruptException):
        rospy.logfatal("Error occurred! Stopping the vosk speech recognition node...")
        rospy.sleep(1)
        print("node terminated")


###!/usr/bin/env python3
### -*- coding: utf-8 -*-
##
##import os
##import sys
##import json
##import queue
##import time
##import vosk
##import sounddevice as sd
##
##import rospy
##import rospkg
##from ros_stt.msg import speech_recognition
##from std_msgs.msg import String, Bool, Int32
##
##import stt_ros_model_downloader as downloader
##
##class vosk_sr():
##    def __init__(self):
##        model_name = rospy.get_param('vosk/model', "vosk-model-small-en-us-0.15")
##
##        rospack = rospkg.RosPack()
##        package_path = rospack.get_path('ros_stt')
##
##        models_dir = os.path.join(package_path, 'models')
##        model_path = os.path.join(models_dir, model_name)
##
##        if not os.path.exists(model_path):
##            rospy.logwarn(f"model '{model_name}' not found in '{models_dir}', launching downloader...")
##            model_downloader = downloader.model_downloader()
##            model_downloader.execute()
##            model_name = model_downloader.model_to_download
##
##        if not rospy.has_param('vosk/model'):
##            rospy.set_param('vosk/model', model_name)
##
##        # --- State flags ---
##        self.tts_status = False
##        self.mic_enabled = bool(rospy.get_param('vosk/mic_enabled', 1))
##        self.accept_audio = True  # gate in callback; set False when stopped
##        self.pausing = False      # soft-stop in progress
##        self.stop_grace_ms = int(rospy.get_param('~stop_grace_ms', 500))  # how long to finish buffered audio
##
##        # --- Publishers ---
##        self.pub_vosk = rospy.Publisher('speech_recognition/vosk_result', speech_recognition, queue_size=10)
##        self.pub_final = rospy.Publisher('speech_recognition/final_result', String, queue_size=10)
##        self.pub_partial = rospy.Publisher('speech_recognition/partial_result', String, queue_size=10)
##
##        rospy.on_shutdown(self.cleanup)
##
##        self.msg = speech_recognition()
##        self.q = queue.Queue()
##
##        # --- Audio device ---
##        self.input_dev_num = sd.query_hostapis()[0]['default_input_device']
##        if self.input_dev_num == -1:
##            rospy.logfatal('No input device found')
##            raise ValueError('No input device found, device number == -1')
##
##        device_info = sd.query_devices(self.input_dev_num, 'input')
##        self.samplerate = int(device_info['default_samplerate'])
##        rospy.set_param('vosk/sample_rate', self.samplerate)
##
##        # --- Model ---
##        self.model = vosk.Model(model_path)
##
##        # --- Subscribers (once) ---
##        rospy.Subscriber('/tts/status', Bool, self.tts_get_status, queue_size=1)
##        rospy.Subscriber('speech_recognition/mic_enable', Int32, self.mic_enable_cb, queue_size=1)
##
##    def cleanup(self):
##        rospy.logwarn("Shutting down VOSK speech recognition node...")
##
##    def stream_callback(self, indata, frames, time_info, status):
##        # Called in audio thread
##        if status:
##            print(status, file=sys.stderr)
##        # Drop audio if not accepting (paused/stopped or TTS speaking)
##        if self.accept_audio:
##            self.q.put(bytes(indata))
##
##    def tts_get_status(self, msg):
##        self.tts_status = msg.data
##        # If TTS starts speaking, stop accepting new audio immediately
##        if self.tts_status:
##            self.accept_audio = False
##
##    def mic_enable_cb(self, msg):
##        want_enable = (int(msg.data) != 0)
##        if want_enable and not self.mic_enabled:
##            # Resume
##            self.mic_enabled = True
##            self.accept_audio = True
##            self.pausing = False
##            rospy.loginfo("Mic ENABLED")
##        elif (not want_enable) and self.mic_enabled:
##            # Request a graceful stop
##            self.mic_enabled = False
##            self.pausing = True
##            # keep accepting audio during pausing so queued frames can be processed
##            self.accept_audio = True
##            rospy.loginfo("Mic DISABLE requested (graceful pause)")
##
##    def _drain_queue_nowait(self):
##        """Empty queue without blocking."""
##        drained = 0
##        try:
##            while True:
##                self.q.get_nowait()
##                drained += 1
##        except queue.Empty:
##            pass
##        return drained
##
##    def speech_recognize(self):
##        try:
##            with sd.RawInputStream(
##                samplerate=self.samplerate,
##                blocksize=16000,
##                device=self.input_dev_num,
##                dtype='int16',
##                channels=1,
##                callback=self.stream_callback
##            ):
##                rospy.loginfo('Audio stream started')
##                rec = vosk.KaldiRecognizer(self.model, self.samplerate)
##                print("Vosk is ready to listen!")
##
##                # loop vars
##                have_partial = False
##                partial_text = "unk"
##
##                rate = rospy.Rate(200)
##                while not rospy.is_shutdown():
##
##                    # --- If TTS is speaking: ignore everything, reset recognizer, drop queue ---
##                    if self.tts_status:
##                        self.accept_audio = False
##                        self._drain_queue_nowait()
##                        rec.Reset()
##                        rate.sleep()
##                        continue
##
##                    # --- Graceful stop (pausing): finish buffered audio, then finalize & stop ---
##                    if self.pausing:
##                        deadline = time.monotonic() + (self.stop_grace_ms / 1000.0)
##                        # Process whatever is still in the queue until grace time expires
##                        while time.monotonic() < deadline:
##                            try:
##                                data = self.q.get_nowait()
##                            except queue.Empty:
##                                # small sleep to allow last frames to arrive
##                                time.sleep(0.01)
##                                continue
##
##                            if rec.AcceptWaveform(data):
##                                # Final chunk recognized during pause; publish final
##                                result_text = json.loads(rec.FinalResult()).get("text", "")
##                                if len(result_text) > 2:
##                                    self.msg.isSpeech_recognized = True
##                                    self.msg.time_recognized = rospy.Time.now()
##                                    self.msg.final_result = result_text
##                                    self.msg.partial_result = "unk"
##                                    self.pub_vosk.publish(self.msg)
##                                    self.pub_final.publish(result_text)
##                                rec.Reset()
##
##                        # After grace window, ask Vosk to flush internal buffers
##                        final_flush = json.loads(rec.FinalResult()).get("text", "")
##                        if len(final_flush) > 2:
##                            self.msg.isSpeech_recognized = True
##                            self.msg.time_recognized = rospy.Time.now()
##                            self.msg.final_result = final_flush
##                            self.msg.partial_result = "unk"
##                            self.pub_vosk.publish(self.msg)
##                            self.pub_final.publish(final_flush)
##
##                        # Now fully stop: stop accepting, clear queue, reset recognizer
##                        self.accept_audio = False
##                        self._drain_queue_nowait()
##                        rec.Reset()
##                        self.pausing = False
##                        rate.sleep()
##                        continue
##
##                    # --- If mic disabled (and not pausing): just idle ---
##                    if not self.mic_enabled:
##                        self.accept_audio = False
##                        self._drain_queue_nowait()
##                        rec.Reset()
##                        rate.sleep()
##                        continue
##
##                    # --- Normal operation (mic enabled) ---
##                    self.accept_audio = True
##                    try:
##                        data = self.q.get(timeout=0.05)
##                    except queue.Empty:
##                        rate.sleep()
##                        continue
##
##                    if rec.AcceptWaveform(data):
##                        # Final result
##                        result_text = json.loads(rec.FinalResult()).get("text", "")
##                        if len(result_text) > 2:
##                            self.msg.isSpeech_recognized = True
##                            self.msg.time_recognized = rospy.Time.now()
##                            self.msg.final_result = result_text
##                            self.msg.partial_result = "unk"
##                            self.pub_vosk.publish(self.msg)
##                            self.pub_final.publish(result_text)
##                        rec.Reset()
##                        have_partial = False
##                        partial_text = "unk"
##                    else:
##                        # Partial result (only publish if non-empty)
##                        ptxt = json.loads(rec.PartialResult()).get("partial", "")
##                        if ptxt:
##                            have_partial = True
##                            partial_text = ptxt
##                            self.msg.isSpeech_recognized = False
##                            self.msg.time_recognized = rospy.Time.now()
##                            self.msg.final_result = "unk"
##                            self.msg.partial_result = partial_text
##                            self.pub_vosk.publish(self.msg)
##                            self.pub_partial.publish(partial_text)
##
##                    rate.sleep()
##
##        except Exception as e:
##            exit(type(e).__name__ + ': ' + str(e))
##        except KeyboardInterrupt:
##            rospy.loginfo("Stopping the VOSK speech recognition node...")
##            rospy.sleep(1)
##            print("node terminated")
##
##if __name__ == '__main__':
##    try:
##        rospy.init_node('vosk', anonymous=False)
##        rec = vosk_sr()
##        rec.speech_recognize()
##    except (KeyboardInterrupt, rospy.ROSInterruptException):
##        rospy.logfatal("Error occurred! Stopping the vosk speech recognition node...")
##        rospy.sleep(1)
##        print("node terminated")
##
##
#####!/usr/bin/env python3
##### -*- coding: utf-8 -*-
####
##### Intergrated by Angelo Antikatzidis https://github.com/a-prototype/vosk_ros
##### Source code based on https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py from VOSK's example code
####
##### Tuned for the python flavor of VOSK: vosk-0.3.31
##### If you do not have vosk then please install it by running $ pip3 install vosk
##### If you have a previous version of vosk installed then update it by running $ pip3 install vosk --upgrade
##### Tested on ROS Noetic & Melodic. Please advise the "readme" for using it with ROS Melodic
####
##### This is a node that intergrates VOSK with ROS and supports a TTS engine to be used along with it
##### When the TTS engine is speaking some words, the recognizer will stop listenning to the audio stream so it won't listen to it self :)
####
##### It publishes to the topic speech_recognition/vosk_result a custom "speech_recognition" message
##### It publishes to the topic speech_recognition/final_result a simple string
##### It publishes to the topic speech_recognition/partial_result a simple string
####
####import os
####import sys
####import json
####import queue
####import vosk
####import sounddevice as sd
####from mmap import MAP_SHARED
####
####import rospy
####import rospkg
####from ros_vosk.msg import speech_recognition
####from std_msgs.msg import String, Bool
##### >>> NEW: use Int32 for 1/0 control
####from std_msgs.msg import Int32
####
####import vosk_ros_model_downloader as downloader
####
####class vosk_sr():
####    def __init__(self):
####        model_name = rospy.get_param('vosk/model', "vosk-model-small-en-us-0.15")
####
####        rospack = rospkg.RosPack()
####        rospack.list()
####        package_path = rospack.get_path('ros_vosk')
####
####        models_dir = os.path.join(package_path, 'models')
####        model_path = os.path.join(models_dir, model_name)
####
####        if not os.path.exists(model_path):
####            print (f"model '{model_name}' not found in '{models_dir}'! Please use the GUI to download it or configure an available model...")
####            model_downloader = downloader.model_downloader()
####            model_downloader.execute()
####            model_name = model_downloader.model_to_download
####
####        if not rospy.has_param('vosk/model'):
####            rospy.set_param('vosk/model', model_name)
####
####        # States
####        self.tts_status = False
####        # >>> NEW: mic enable state (1=enabled, 0=disabled)
####        self.mic_enabled = bool(rospy.get_param('vosk/mic_enabled', 0))
####
####        # ROS pubs
####        self.pub_vosk = rospy.Publisher('speech_recognition/vosk_result', speech_recognition, queue_size=10)
####        self.pub_final = rospy.Publisher('speech_recognition/final_result', String, queue_size=10)
####        self.pub_partial = rospy.Publisher('speech_recognition/partial_result', String, queue_size=10)
####
####        self.rate = rospy.Rate(100)
####        rospy.on_shutdown(self.cleanup)
####
####        self.msg = speech_recognition()
####        self.q = queue.Queue()
####
####        # Audio device
####        self.input_dev_num = sd.query_hostapis()[0]['default_input_device']
####        if self.input_dev_num == -1:
####            rospy.logfatal('No input device found')
####            raise ValueError('No input device found, device number == -1')
####
####        device_info = sd.query_devices(self.input_dev_num, 'input')
####        self.samplerate = int(device_info['default_samplerate'])
####        rospy.set_param('vosk/sample_rate', self.samplerate)
####
####        self.model = vosk.Model(model_path)
####
####        # >>> NEW: set up subscribers ONCE here (not inside the loop)
####        rospy.Subscriber('/tts/status', Bool, self.tts_get_status, queue_size=1)
####        rospy.Subscriber('speech_recognition/mic_enable', Int32, self.mic_enable_cb, queue_size=1)
####
####        #TODO GPUInit automatically selects a CUDA device and allows multithreading.
####        # gpu = vosk.GpuInit() #TODO
####
####    def cleanup(self):
####        rospy.logwarn("Shutting down VOSK speech recognition node...")
####
####    def stream_callback(self, indata, frames, time, status):
####        # Called (from a separate thread) for each audio block
####        if status:
####            print(status, file=sys.stderr)
####        self.q.put(bytes(indata))
####
####    def tts_get_status(self, msg):
####        self.tts_status = msg.data
####
####    # >>> NEW: mic enable/disable via 1/0
####    def mic_enable_cb(self, msg):
####        # Expecting Int32: 1 = enable, 0 = disable (any nonzero treated as enable)
####        self.mic_enabled = (int(msg.data) != 0)
####        rospy.loginfo("Vosk microphone input is now %s", "ENABLED" if self.mic_enabled else "DISABLED")
####
####    # (kept for backward compatibility, but not used in the loop anymore)
####    def tts_status_listenner(self):
####        rospy.Subscriber('/tts/status', Bool, self.tts_get_status, queue_size=1)
####
####    # >>> NEW: helper to safely drain the queue
####    def _drain_queue(self):
####        try:
####            while True:
####                self.q.get_nowait()
####        except queue.Empty:
####            pass
####
####    def speech_recognize(self):
####        try:
####            with sd.RawInputStream(
####                samplerate=self.samplerate,
####                blocksize=16000,
####                device=self.input_dev_num,
####                dtype='int16',
####                channels=1,
####                callback=self.stream_callback
####            ):
####                rospy.logdebug('Started recording')
####
####                rec = vosk.KaldiRecognizer(self.model, self.samplerate)
####                print("Vosk is ready to listen!")
####                isRecognized = False
####                isRecognized_partially = False
####
####                while not rospy.is_shutdown():
####                    # >>> NEW: if TTS speaking OR mic disabled, ignore/flush mic data
####                    if self.tts_status or not self.mic_enabled:
####                        self._drain_queue()
####                        rec.Reset()
####                        rospy.sleep(0.01)
####                        continue
####
####                    # Normal operation
####                    data = self.q.get()
####                    if rec.AcceptWaveform(data):
####                        # Final result
####                        result = rec.FinalResult()
####                        diction = json.loads(result)
####                        lentext = len(diction.get("text", ""))
####
####                        if lentext > 2:
####                            result_text = diction["text"]
####                            rospy.loginfo(result_text)
####                            isRecognized = True
####                        else:
####                            isRecognized = False
####
####                        rec.Reset()  # ready for next utterance
####                    else:
####                        # Partial result
####                        result_partial = rec.PartialResult()
####                        if (len(result_partial) > 20):
####                            isRecognized_partially = True
####                            partial_dict = json.loads(result_partial)
####                            partial = partial_dict.get("partial", "unk")
####                        else:
####                            partial = "unk"
####
####                    if isRecognized is True:
####                        self.msg.isSpeech_recognized = True
####                        self.msg.time_recognized = rospy.Time.now()
####                        self.msg.final_result = result_text
####                        self.msg.partial_result = "unk"
####                        self.pub_vosk.publish(self.msg)
####                        rospy.sleep(0.1)
####                        self.pub_final.publish(result_text)
####                        isRecognized = False
####
####                    elif isRecognized_partially is True:
####                        if partial != "unk":
####                            self.msg.isSpeech_recognized = False
####                            self.msg.time_recognized = rospy.Time.now()
####                            self.msg.final_result = "unk"
####                            self.msg.partial_result = partial
####                            self.pub_vosk.publish(self.msg)
####                            rospy.sleep(0.1)
####                            self.pub_partial.publish(partial)
####                        isRecognized_partially = False
####
####        except Exception as e:
####            exit(type(e).__name__ + ': ' + str(e))
####        except KeyboardInterrupt:
####            rospy.loginfo("Stopping the VOSK speech recognition node...")
####            rospy.sleep(1)
####            print("node terminated")
####
####if __name__ == '__main__':
####    try:
####        rospy.init_node('vosk', anonymous=False)
####        rec = vosk_sr()
####        rec.speech_recognize()
####    except (KeyboardInterrupt, rospy.ROSInterruptException) as e:
####        rospy.logfatal("Error occurred! Stopping the vosk speech recognition node...")
####        rospy.sleep(1)
####        print("node terminated")
####
