#!/usr/bin/env python3

import rospy
import pygame
from control_msgs.msg import JointTrajectoryControllerState

# Initialize the ROS node
rospy.init_node("Arms_Angle_GUI")

# Define some colors
BLACK = (0, 0, 0)
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
front_quori = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/center_without_arm.png")
left_quori = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/left_quori.png")
right_quori = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/right_quori.png")

# arms
right_arm = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/right_arm.png")
left_arm = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/left_arm.png")
center_left_arm = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/center_left_arm.png")
center_right_arm = pygame.image.load("/home/akash/catkin_ws/src/quori_gui/src/guipygame/center_right_arm.png")

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

def map_value(x, min_from, max_from, min_to, max_to):
    y = min_to + ((x - min_from) / (max_from - min_from)) * (max_to - min_to)
    return y


# Callback function for the ROS subscriber
def get_actual_pos(msg):
    global right_arm_pitch, right_arm_roll, left_arm_pitch, left_arm_roll
    
    pos = msg.actual.positions
    left_arm_roll = map_value(pos[3], -1, 1.288, 15, 140)
    right_arm_roll = map_value(pos[1], -1, 1.284, -15, -150)

    left_arm_pitch = map_value(pos[2], 0, 2.385, 0, -125)
    right_arm_pitch = map_value(pos[0], 0, 2.389, 0, 130)
    
    #print(msg)

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
    blitRotate(screen, center_left_arm, (484, 128), (0, 16), left_arm_roll)
    blitRotate(screen, center_right_arm, (400, 128), (32, 16), right_arm_roll)

    screen.blit(front_quori, (389, 24))

    label = label_font.render('R Pitch', True, BLACK)
    screen.blit(label, (25,17))
    label = label_font.render('L Pitch', True, BLACK)
    screen.blit(label, (785,17))
    label = label_font.render('Roll', True, BLACK)
    screen.blit(label, (425,135))
    label = label_font_1.render('L', True, BLACK)
    screen.blit(label, (517,257))
    label = label_font_1.render('R', True, BLACK)
    screen.blit(label, (344,257))

    label = label_font.render('{:.1f}'.format(right_arm_pitch), True, GREEN)
    screen.blit(label, (45,102))
    label = label_font.render('{:.1f}'.format(-1*left_arm_pitch), True, GREEN)
    screen.blit(label, (805,102))
    label = label_font.render('{:.1f}'.format(-1*right_arm_roll), True, GREEN)
    screen.blit(label, (342,102))
    label = label_font.render('{:.1f}'.format(left_arm_roll), True, GREEN)
    screen.blit(label, (502,102))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
