#!/usr/bin/env python3

import rospy
import pygame
from control_msgs.msg import JointTrajectoryControllerState

# Initialize the ROS node
rospy.init_node("Quori_Arms_Angle_GUI")

# Directory
directory = "/home/akash/catkin_ws/src/quori_gui/src/updated_GUI_with_hands/"

# Define some colors
BLACK = (41, 36, 14)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
background = (142,141,141)

pygame.init()

size = (886, 300)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Quori Arm Angles")

done = False
#font
label_font = pygame.font.Font(None, 30)
label_font_1 = pygame.font.Font(None, 50)
label = label_font.render('Right Arm Pitch', True, BLACK)

# quori
front_quori = pygame.image.load(directory+"center_without_arm.png")
left_quori = pygame.image.load(directory+"left_quori.png")
right_quori = pygame.image.load(directory+"right_quori.png")

# arms
right_arm = pygame.image.load(directory+"right_arm.png")
left_arm = pygame.image.load(directory+"left_arm.png")
#center_left_arm = pygame.image.load("center_left_arm.png")
#center_right_arm = pygame.image.load("center_right_arm.png")

class arms:
    def __init__(self, image_name, pos, originPos=(0,0) ,rot=0):
        self.image = pygame.image.load(image_name)
        self.pos = pos
        self.rot = rot
        self.originPos = originPos

arm = [arms(directory+str(i)+".png", (0,0)) for i in range(18)]
arm[0].pos = (476,110)
arm[1].pos = (375,110)
#1
arm[2].pos = (478,110)
arm[3].pos = (375,110)

arm[4].pos = (478,110)
arm[5].pos = (315,110)
#2
arm[6].pos = (478,110)
arm[7].pos = (368,110)

arm[8].pos = (476,110)
arm[9].pos = (289,110)
#3
arm[10].pos = (478,83)
arm[11].pos = (368,83)

arm[12].pos = (476,83)
arm[13].pos = (289,83)
#4
arm[14].pos = (478,44)
arm[15].pos = (368,44)

arm[16].pos = (476,52)
arm[17].pos = (289,52)



def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

    surf.blit(rotated_image, rotated_image_rect)

clock = pygame.time.Clock()
i = 0
right_arm_pitch = 0
right_arm_roll = 0
left_arm_pitch = 0
left_arm_roll = 0

leftarm=0
rightarm=1

def map_value(x, min_from, max_from, min_to, max_to):
    y = min_to + ((x - min_from) / (max_from - min_from)) * (max_to - min_to)
    return y

def getLeftArm(roll, pitch):
    #for left arm, left_arm_roll, left_arm_pitch
    #              - 0 -   - 1 -
    #              14.1    28.0     25.8 - 1 ->  2 4
    #               2       4       74.4 - 2 ->  6 8
    #               6       8       95.9 - 3 -> 10 12
    #               10      12      124  - 4 -> 14 16
    #               14      16

    roll_min_max = [[2,4],[6,8],[10,12],[14,16]]
    pitch_lev = [25, 74, 96, 124]
    

    dist = [0, 0, 0, 0]
    for i in range(4):
        dist[i] = abs(abs(pitch) - abs(pitch_lev[i]))

    #print(dist)

    group = dist.index(min(dist))
    roll_dist = [abs(abs(roll) - 14.1), abs(abs(roll) - 28.0)]
    val = roll_dist.index(min(roll_dist))

    return roll_min_max[group][val]


def getRightArm(roll, pitch):
    #for left arm, left_arm_roll, left_arm_pitch
    #              - 0 -   - 1 -
    #              14.1    30.0     25.8 - 1 ->  3 5
    #               3       5       78.0 - 2 ->  7 9
    #               7       9       103  - 3 -> 11 13
    #               11      13      124  - 4 -> 15 17
    #               15      17

    roll_min_max = [[3,5],[7,9],[11,13],[15,17]]
    pitch_lev = [25, 78, 103, 124]

    dist = [0, 0, 0, 0]
    for i in range(4):
        dist[i] = abs(abs(pitch) - abs(pitch_lev[i]))

    group = dist.index(min(dist))
    roll_dist = [abs(abs(roll) - 14.1), abs(abs(roll) - 30.0)]
    val = roll_dist.index(min(roll_dist))
    #print(roll_dist)
    return roll_min_max[group][val]


# Callback function for the ROS subscriber
def get_actual_pos(msg):
    global right_arm_pitch, right_arm_roll, left_arm_pitch, left_arm_roll
    global leftarm, rightarm
    
    pos = msg.actual.positions
    left_arm_roll = map_value(pos[3], -1, 1.288, 15, 140)
    right_arm_roll = map_value(pos[1], -1, 1.284, -15, -150)

    left_arm_pitch = map_value(pos[2], 0, 2.385, 0, -125)
    right_arm_pitch = map_value(pos[0], 0, 2.389, 0, 130)

    leftarm = getLeftArm(left_arm_roll, left_arm_pitch)
    rightarm = getRightArm(right_arm_roll, right_arm_pitch)
    #print(leftarm, rightarm)


# ROS subscriber for the arm angle
rospy.Subscriber('/quori/joint_trajectory_controller/state',
                 JointTrajectoryControllerState,
                 get_actual_pos)


    

while not rospy.is_shutdown() and not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            print(mouse_pos)

    screen.fill(background)
    
    screen.blit(left_quori, (704, 24))
    screen.blit(right_quori, (67, 24))
    blitRotate(screen, right_arm, (125, 132), (18.5, 18.5), right_arm_pitch)
    blitRotate(screen, left_arm, (756, 132), (18.5, 18.5), left_arm_pitch)
    #blitRotate(screen, center_left_arm, (484, 128), (0, 16), left_arm_roll)
    #blitRotate(screen, center_right_arm, (400, 128), (32, 16), right_arm_roll)

    
    blitRotate(screen, arm[leftarm].image, arm[leftarm].pos, arm[leftarm].originPos, arm[leftarm].rot)
    blitRotate(screen, arm[rightarm].image, arm[rightarm].pos, arm[rightarm].originPos, arm[rightarm].rot)
    

    screen.blit(front_quori, (389, 24))

    label = label_font.render('Right', True, BLACK)
    screen.blit(label, (25,17))
    label = label_font.render('Left', True, BLACK)
    screen.blit(label, (785,17))
    label = label_font.render('Right', True, BLACK)
    screen.blit(label, (289,41))
    label = label_font.render('Left', True, BLACK)
    screen.blit(label, (543,41))
##    label = label_font.render('Roll', True, BLACK)
##    screen.blit(label, (425,135))
##    label = label_font_1.render('L', True, BLACK)
##    screen.blit(label, (517,257))
##    label = label_font_1.render('R', True, BLACK)
##    screen.blit(label, (344,257))

    label = label_font.render('P: {:.1f}'.format(right_arm_pitch), True, GREEN)
    screen.blit(label, (306,243))
    screen.blit(label, (30,46))
    label = label_font.render('R: {:.1f}'.format(-1*right_arm_roll), True, GREEN)
    screen.blit(label, (306,263))

    label = label_font.render('P: {:.1f}'.format(-1*left_arm_pitch), True, GREEN)
    screen.blit(label, (526,243))
    screen.blit(label, (804,46))
    label = label_font.render('R: {:.1f}'.format(left_arm_roll), True, GREEN)
    screen.blit(label, (526,263))
    

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
