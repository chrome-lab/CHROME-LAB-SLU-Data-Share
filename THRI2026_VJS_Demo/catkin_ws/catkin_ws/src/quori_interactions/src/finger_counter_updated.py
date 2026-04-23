#!/usr/bin/env python3
import os
import time

import cv2

from hand_detector import HandDetector
import rospy

from std_msgs.msg import String

#import movement_control

cam_width, cam_height = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, cam_width)
cap.set(4, cam_height)

##folder_path = "hand-images"
##image_path_list = os.listdir(folder_path)
# overlay the fingers on the camera feed
##overlay_image_list = []
##for image_path in image_path_list:
##    image = cv2.imread(os.path.join(folder_path, image_path))
##    # image = cv2.resize(image, (128, 128))
##    overlay_image_list.append(image)

previous_time = 0
detector = HandDetector(min_detection_confidence=0.95, max_num_hands=1)
tip_ids = [4, 8, 12, 16, 20]
rospy.init_node("Vision_node")
pub = rospy.Publisher("/op_cmd", String, queue_size = -1)
data = String()

#control = movement_control.MovementControl()
while True:

    success, img = cap.read()
    img = cv2.flip(img,1)
    img = detector.find_hands(img)
    landmark_list = detector.find_lm_position(img)

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
        data.data = 'reset'
        pub.publish(data)
        
    elif (total_fingers == 1):
        cv2.putText(img, "Point", (25, 385),
                    cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 0, 0), 10)
        data.data = 'point'
        pub.publish(data)
        
    elif (total_fingers == 2):
        cv2.putText(img, "alert", (25, 385),
                    cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 0, 0), 10)
        data.data = 'alert'
        pub.publish(data)
        
    elif (total_fingers == 5):
        cv2.putText(img, "Wave", (25, 385),
                    cv2.FONT_HERSHEY_PLAIN,
                    3, (255, 0, 0), 10)
        data.data = 'wave'
        pub.publish(data)
        
        

    # embed overlay onto camera feed
    #h, w, c = overlay_image_list[total_fingers].shape
    #img[:h, :w] = overlay_image_list[total_fingers]
    # display total fingers
    # calculate fps
##    current_time = time.time()
##    fps = 1 / (current_time - previous_time)
##    previous_time = current_time
##    cv2.putText(img, str(int(fps)), (400, 70),
##                cv2.FONT_HERSHEY_PLAIN, 3,
##                (255, 0, 0), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
