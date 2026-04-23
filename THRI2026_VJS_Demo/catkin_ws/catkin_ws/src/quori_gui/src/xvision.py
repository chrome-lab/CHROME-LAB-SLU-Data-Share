#!/usr/bin/env python3

import time

import cv2
import numpy as np
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from hand_detector import HandDetector

from std_msgs.msg import Int64, String

rospy.init_node("Vision_1")
rate = rospy.Rate(30)
green = (0, 255, 0)
purple = (255, 0, 255)

cap = cv2.VideoCapture(0)
cam_width, cam_height = 640, 480
cap.set(3, cam_width)
cap.set(4, cam_height)

previous_time = 0

left_arm_bb = 50, 50, 270, 270
right_arm_bb = 350, 50, 570, 270

color_left = green
up_left = green
down_left = green
left_left = green
right_left = green

color_right = green
up_right = green
down_right = green
left_right = green
right_right = green


smoothening = 7

detector = HandDetector(min_detection_confidence=0.85,
                        max_num_hands=2)

pub = rospy.Publisher("/virtual_joy", Int64, queue_size=1)
data = Int64()

tip_ids = [4, 8, 12, 16, 20]
pub_1 = rospy.Publisher("/op_cmd", String, queue_size = -1)
data_1 = String()
# debug
# min_length = float('inf')
choice = 1
def mode_callback(data):
    global choice
    choice = data.data
    
rospy.Subscriber("/video_mode", Int64, mode_callback)
image_pub = rospy.Publisher('/webcam/image_overlaid', Image, queue_size=1)
bridge = CvBridge()

one = 0
two = 0
three = 0

while True:
    # read frame
    sucess, img = cap.read()
    img = cv2.flip(img,1)
    # find hand landmarks
    img = detector.find_hands(img)
    landmark_list = detector.find_lm_position(img)

    if choice == 0:
        cv2.rectangle(img, (left_arm_bb[0], left_arm_bb[1]),
                      (left_arm_bb[2], left_arm_bb[3]),
                      color_left, 2)
        cv2.putText(img, "UP", (140, 80), cv2.FONT_HERSHEY_PLAIN,
                    2, up_left, 3)
        cv2.putText(img, "DOWN", (120, 260), cv2.FONT_HERSHEY_PLAIN,
                    2, down_left, 3)
        cv2.putText(img, "<-", (53, 165), cv2.FONT_HERSHEY_PLAIN,
                    2, left_left, 3)
        cv2.putText(img, "->", (220, 165), cv2.FONT_HERSHEY_PLAIN,
                    2, right_left, 3)

        # -----------------------------

        cv2.rectangle(img, (right_arm_bb[0], right_arm_bb[1]),
                      (right_arm_bb[2], right_arm_bb[3]),
                      color_right, 2)
        cv2.putText(img, "UP", (440, 80), cv2.FONT_HERSHEY_PLAIN,
                    2, up_right, 3)
        cv2.putText(img, "DOWN", (420, 260), cv2.FONT_HERSHEY_PLAIN,
                    2, down_right, 3)
        cv2.putText(img, "<-", (353, 165), cv2.FONT_HERSHEY_PLAIN,
                    2, left_right, 3)
        cv2.putText(img, "->", (520, 165), cv2.FONT_HERSHEY_PLAIN,
                    2, right_right, 3)
        
        
        color_left = green
        up_left = green
        down_left = green
        left_left = green
        right_left = green

        color_right = green
        up_right = green
        down_right = green
        left_right = green
        right_right = green
    ##
        # get the tip of the index and middle fingers
        if len(landmark_list) != 0:
            x1, y1 = landmark_list[8][1:]
            x2, y2 = landmark_list[12][1:]

            # check which fingers are up
            fingers = detector.find_fingers_up()

            
            # only index finger: moving mode
            if fingers[1] == 1 and fingers[2] == 0:

                if (x1 > left_arm_bb[0]) and (x1 < left_arm_bb[2]) and\
                   (y1 > left_arm_bb[1]) and (y1 < left_arm_bb[3]):

                    color_left = purple

                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                    if (x1 > 128) and (x1 < 195) and (y1 > 50) and (y1 < 90):
                        up_left = purple
                        data.data = 1
                        pub.publish(data)
                    elif (x1 > 50) and (x1 < 115) and (y1 > 130) and (y1 < 175):
                        left_left = purple
                        data.data = 2
                        pub.publish(data)
                    elif (x1 > 205) and (x1 < 270) and (y1 > 130) and (y1 < 175):
                        right_left = purple
                        data.data = 3
                        pub.publish(data)
                    elif (x1 > 105) and (x1 < 220) and (y1 > 225) and (y1 < 270):
                        down_left = purple
                        data.data = 4
                        pub.publish(data)
                        
    ##                print(x1,y1)

                elif (x1 > right_arm_bb[0]) and (x1 < right_arm_bb[2]) and\
                   (y1 > right_arm_bb[1]) and (y1 < right_arm_bb[3]):

                    color_right = purple
                    cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

                    if (x1 > 428) and (x1 < 495) and (y1 > 50) and (y1 < 90):
                        up_right = purple
                        data.data = 5
                        pub.publish(data)
                    elif (x1 > 350) and (x1 < 415) and (y1 > 130) and (y1 < 175):
                        left_right = purple
                        data.data = 6
                        pub.publish(data)
                    elif (x1 > 505) and (x1 < 570) and (y1 > 130) and (y1 < 175):
                        right_right = purple
                        data.data = 7
                        pub.publish(data)
                    elif (x1 > 405) and (x1 < 520) and (y1 > 225) and (y1 < 270):
                        down_right = purple
                        data.data = 8
                        pub.publish(data)
                        
    ##                print(x1,y1)
    else:
        fingers = []
        if len(landmark_list) != 0:
            # determine which fingers are up
            for tip_id in tip_ids:
                # thumb
                if tip_id == 4:
                    # tip is to the left of pip
                    if landmark_list[tip_id][1] < landmark_list[tip_id - 1][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:
                    # comparing tip with pip
                    if landmark_list[tip_id][2] < landmark_list[tip_id - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
        total_fingers = sum(fingers)
        #print(total_fingers)

        if (total_fingers == 0):
            cv2.putText(img, "Resting", (25, 385),
                        cv2.FONT_HERSHEY_PLAIN,
                        3, (255, 0, 0), 10)
##            data_1.data = 'reset'
##            pub_1.publish(data_1)
            one = 0
            two = 0
            three = 0
            
        elif (total_fingers == 1):
            cv2.putText(img, "Point", (25, 385),
                        cv2.FONT_HERSHEY_PLAIN,
                        3, (255, 0, 0), 10)
##            data_1.data = 'point'
##            pub_1.publish(data_1)
            one = one +1
            two = 0
            three = 0
            
        elif (total_fingers == 2):
            cv2.putText(img, "alert", (25, 385),
                        cv2.FONT_HERSHEY_PLAIN,
                        3, (255, 0, 0), 10)
##            data_1.data = 'alert'
##            pub_1.publish(data_1)
            one = 0
            two = two + 1
            three = 0
            
        elif (total_fingers == 5):
            cv2.putText(img, "Wave", (25, 385),
                        cv2.FONT_HERSHEY_PLAIN,
                        3, (255, 0, 0), 10)
##            data_1.data = 'wave'
##            pub_1.publish(data_1)
            one = 0
            two = 0
            three = three + 1

        if one > 30:
            data_1.data = 'point'
            pub_1.publish(data_1)
            one = 0
            two = 0
            three = 0
        elif  two > 30:
            data_1.data = 'alert'
            pub_1.publish(data_1)
            one = 0
            two = 0
            three = 0
        elif three > 30:
            data_1.data = 'wave'
            pub_1.publish(data_1)
            one = 0
            two = 0
            three = 0
            

    ros_image = bridge.cv2_to_imgmsg(img, encoding="bgr8")
    image_pub.publish(ros_image)
    rate.sleep()

##    cv2.imshow('Image', img)
##    cv2.waitKey(1)

