#!/usr/bin/env python3

import cv2
import mediapipe as mp

import numpy as np
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Int64, String


# Initialize mediapipe hand detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Finger tip landmarks according to Mediapipe documentation
finger_tips = [4, 8, 12, 16, 20]

# Names for fingers (thumb, index, middle, ring, pinky)
finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
left_hand = [0, 0, 0, 0, 0]
right_hand = [0, 0, 0, 0, 0]


# Function to count fingers for one hand
def count_fingers(hand_landmarks, hand_label):
    count = 0
    finger_status = []
    global left_hand, right_hand
    
    # Check for each finger whether it is up or down (Index to Pinky fingers)
    for i in range(1, 5):  # Checking index to pinky fingers
        if hand_landmarks.landmark[finger_tips[i]].y < hand_landmarks.landmark[finger_tips[i] - 2].y:
            if hand_label == "Right":
                right_hand[i] = 1
            else:
                left_hand[i] = 1
        else:
            if hand_label == "Right":
                right_hand[i] = 0
            else:
                left_hand[i] = 0

    # Thumb: Need different logic for left and right hands
    if hand_label == 'Right':  # Right hand thumb
        if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0] - 2].x:
            right_hand[0] = 1
        else:
            right_hand[0] = 0
            
    else:  # Left hand thumb
        if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[finger_tips[0] - 2].x:
            left_hand[0] = 1
        else:
            left_hand[0] = 0

    return count, finger_status


rospy.init_node("Vision_1")
rate = rospy.Rate(30)
green = (0, 255, 0)
purple = (255, 0, 255)

# Start capturing video from webcam
cap = cv2.VideoCapture(0)
cam_width, cam_height = 640, 480
cap.set(3, cam_width)
cap.set(4, cam_height)

#################################################
# parameters
#################################################
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

pub = rospy.Publisher("/virtual_joy", Int64, queue_size=1)
data = Int64()

pub_1 = rospy.Publisher("/op_cmd", String, queue_size = -1)
data_1 = String()

choice = 1
mode = 'Semi-Auto'

def mode_callback(data):
    global choice, mode
    choice = data.data
    if choice == 1:
        mode = 'Semi-Auto'
    else:
        mode = 'Manual'

rospy.Subscriber("/video_mode", Int64, mode_callback)
image_pub = rospy.Publisher('/webcam/image_overlaid', Image, queue_size=1)
bridge = CvBridge()

wave = 0
fist_bump = 0
high_five = 0
alert = 0
point= 0
hug = 0

joy_flag = False

# Mediapipe hands processing
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.75, max_num_hands=2) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        left_hand = [0, 0, 0, 0, 0]
        right_hand = [0, 0, 0, 0, 0]
        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Convert the BGR frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect hands and landmarks
        results = hands.process(rgb_frame)
        h,w,_ = rgb_frame.shape
        x1 = 0
        y1 = 0
        
        cv2.putText(frame, mode, (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (41, 36, 14), 5)
        
        # Draw hand landmarks and count fingers if hands are detected
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                #print(hand_landmarks.landmark[8])
##                if results.multi_handedness[idx].classification[0].label == 'Right'
                x1 = int(hand_landmarks.landmark[8].x * w)
                y1 = int(hand_landmarks.landmark[8].y * h)
                
                #print(x1,y1)
                # Draw hand landmarks on the frame
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Hand label (left or right)
                hand_label = 'Right' if results.multi_handedness[idx].classification[0].label == 'Right' else 'Left'

                # Count fingers for this hand
                count, finger_status = count_fingers(hand_landmarks, hand_label)
                #cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            if choice == 0:
                
                cv2.rectangle(frame, (left_arm_bb[0], left_arm_bb[1]),
                              (left_arm_bb[2], left_arm_bb[3]),
                              color_left, 2)
                cv2.putText(frame, "UP", (140, 80), cv2.FONT_HERSHEY_PLAIN,
                            2, up_left, 3)
                cv2.putText(frame, "DOWN", (120, 260), cv2.FONT_HERSHEY_PLAIN,
                            2, down_left, 3)
                cv2.putText(frame, "<-", (53, 165), cv2.FONT_HERSHEY_PLAIN,
                            2, left_left, 3)
                cv2.putText(frame, "->", (220, 165), cv2.FONT_HERSHEY_PLAIN,
                            2, right_left, 3)

                # -----------------------------

                cv2.rectangle(frame, (right_arm_bb[0], right_arm_bb[1]),
                              (right_arm_bb[2], right_arm_bb[3]),
                              color_right, 2)
                cv2.putText(frame, "UP", (440, 80), cv2.FONT_HERSHEY_PLAIN,
                            2, up_right, 3)
                cv2.putText(frame, "DOWN", (420, 260), cv2.FONT_HERSHEY_PLAIN,
                            2, down_right, 3)
                cv2.putText(frame, "<-", (353, 165), cv2.FONT_HERSHEY_PLAIN,
                            2, left_right, 3)
                cv2.putText(frame, "->", (520, 165), cv2.FONT_HERSHEY_PLAIN,
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

                if (left_hand[1] == 1 or right_hand[1] == 1) and\
                   (x1 > left_arm_bb[0]) and (x1 < left_arm_bb[2]) and\
                   (y1 > left_arm_bb[1]) and (y1 < left_arm_bb[3]):

                    color_left = purple
                    cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

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

                elif (left_hand[1] == 1 or right_hand[1] == 1) and\
                     (x1 > right_arm_bb[0]) and (x1 < right_arm_bb[2]) and\
                     (y1 > right_arm_bb[1]) and (y1 < right_arm_bb[3]):

                    
                    color_right = purple
                    cv2.circle(frame, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

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

            elif choice == 1:
                if right_hand == [0,0,0,0,0] and left_hand == [0,0,0,0,0]:
                    cv2.putText(frame, "Fist Bump", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = 0
                    fist_bump = fist_bump + 1
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif (right_hand == [1,1,1,1,1] and left_hand == [0,0,0,0,0]) or\
                     (left_hand == [1,1,1,1,1] and right_hand == [0,0,0,0,0]):
                    cv2.putText(frame, "High Five", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = 0
                    fist_bump = 0
                    high_five = high_five + 1
                    alert = 0
                    point= 0
                    hug = 0

                elif right_hand == [1,1,1,1,1] and left_hand == [1,1,1,1,1]:
                    cv2.putText(frame, "Alert", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = alert + 1
                    point= 0
                    hug = 0

                elif right_hand == [0,1,0,0,0] or left_hand == [0,1,0,0,0]:
                    cv2.putText(frame, "Point", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= point + 1
                    hug = 0

                elif right_hand == [1,1,0,0,0] or left_hand == [1,1,0,0,0]:
                    cv2.putText(frame, "Hug", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = hug + 1

                elif right_hand == [0,1,1,1,1] or left_hand == [0,1,1,1,1]:
                    cv2.putText(frame, "Wave", (25, 385), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 10)
                    wave = wave + 1
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                if wave > 30:
                    print("---- wave")
                    data_1.data = 'wave'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif fist_bump > 30:
                    print("---- fist bump")
                    data_1.data = 'fist_bump'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif high_five > 30:
                    print("---- high five")
                    data_1.data = 'high_five'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif alert > 30:
                    print("---- alert")
                    data_1.data = 'alert'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif point > 30:
                    print("---- point")
                    data_1.data = 'point'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

                elif hug > 30:
                    print("---- hug")
                    data_1.data = 'hug'
                    pub_1.publish(data_1)
                    wave = 0
                    fist_bump = 0
                    high_five = 0
                    alert = 0
                    point= 0
                    hug = 0

        else:
            wave = 0
            fist_bump = 0
            high_five = 0
            alert = 0
            point= 0
            hug = 0

        # Display the frame
        #print(left_hand)
        #print(right_hand,"\n")
        ros_image = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        image_pub.publish(ros_image)
        #cv2.imshow('Finger Detection', frame)

        # Press 'q' to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
