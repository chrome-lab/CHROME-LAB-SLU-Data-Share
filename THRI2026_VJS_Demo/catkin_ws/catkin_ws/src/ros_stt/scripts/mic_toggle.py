#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
stt_toggle_key.py
Toggle-publisher for /speech_recognition/mic_enable (std_msgs/Int32)
- Space: publish 1, then next Space: publish 0, and so on.
- Also subscribes to speech_recognition/final_result and prints recognized text.
- 'q' or Ctrl-C: exit.
"""

import sys
import select
import termios
import tty
import rospy
from std_msgs.msg import Int32, String

class KeyTogglePublisher:
    def __init__(self):
        rospy.init_node("stt_toggle_key", anonymous=False)

        # Initial state can be overridden via ROS param (0 or 1)
        self.state = int(rospy.get_param("~initial_state", 0))
        self.topic = rospy.get_param("~topic", "/speech_recognition/mic_enable")
        self.final_sub_topic = rospy.get_param("~final_topic", "speech_recognition/final_result")

        self.pub = rospy.Publisher(self.topic, Int32, queue_size=1)
        self.sub = rospy.Subscriber(self.final_sub_topic, String, self._on_final_text)


        data = Int32()
        for i in range (5):
            data.data = 0
            self.pub.publish(data)
            rospy.sleep(1)

        rospy.loginfo("Mic Ready")
        # Prepare terminal in cbreak (NOT raw) to keep normal output formatting
        self.fd = sys.stdin.fileno()
        self.orig_attrs = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)  # <-- changed from tty.setraw(self.fd)

        rospy.on_shutdown(self._restore_terminal)

        rospy.loginfo("stt_toggle_key started.")
        rospy.loginfo("Press <SPACE> to toggle & publish on %s (Int32).", self.topic)
        rospy.loginfo("Current state = %d (will publish this on first toggle).", self.state)
        rospy.loginfo("Press 'q' to quit.")

    def _on_final_text(self, msg: String):
        rospy.loginfo("STT FINAL: %s", msg.data)

    def _restore_terminal(self):
        try:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.orig_attrs)
        except Exception:
            pass

    def _key_available(self):
        # Non-blocking check for a keypress
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
        return bool(rlist)

    def spin(self):
        rate = rospy.Rate(100)
        try:
            while not rospy.is_shutdown():
                if self._key_available():
                    ch = sys.stdin.read(1)
                    if ch == ' ':
                        # Toggle and publish
                        self.state = 0 if self.state == 1 else 1
                        self.pub.publish(Int32(data=self.state))
                        rospy.loginfo("Published: %d", self.state)
                    elif ch in ('q', 'Q'):
                        rospy.loginfo("Exiting on 'q'.")
                        break
                    # ignore other keys
                rate.sleep()
        except KeyboardInterrupt:
            pass
        finally:
            self._restore_terminal()

if __name__ == "__main__":
    node = KeyTogglePublisher()
    node.spin()
