#!/usr/bin/env python3

import rospy
from quori_interactions.msg import ArmsCmd
from control_msgs.msg import JointTrajectoryControllerState

from geometry_msgs.msg import Twist
from std_msgs.msg import String
import time

from std_msgs.msg import Int64
from quori_gui.msg import Opcmd
import time

global mvmnt, one, two, five, dst
mvmnt = "reset"

one = 0
two = 0
five = 0
dst = 1.0


class MovementControl:
    def __init__(self):
        rospy.init_node('MovementControl')
        self.home_pos = ArmsCmd()
        self.home_pos.r_shoulder_pitch = 0.0
        self.home_pos.r_shoulder_roll = -1.0
        self.home_pos.l_shoulder_pitch = 0.0
        self.home_pos.l_shoulder_roll = -1.0

        self.arms_cmd_pub = rospy.Publisher('/arms_cmd', ArmsCmd,
                                            queue_size = 10)

        self.cmd_vel_pub = rospy.Publisher('/quori/base_controller/cmd_vel', Twist, queue_size=10)
        self.custom_cmd_vel = rospy.Subscriber('/custom/cmd_vel', Twist, self.custom_cmd_callback)

        self.arms_mov = ArmsCmd()
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        
        rospy.Subscriber('/quori/joint_trajectory_controller/state',
                         JointTrajectoryControllerState,
                         self.get_actual_pos)
        self.actual_arms_pos = [0.0, 0.0, 0.0, 0.0, 0.0]

        rospy.Subscriber('/virtual_joy', Int64, self.joy_callback)
        self.get_state = False
        self.rate = rospy.Rate(1)

    def custom_cmd_callback(self, msg):
        self.cmd_vel_pub.publish(msg)

    def get_actual_pos(self, msg):
        self.actual_arms_pos = msg.actual.positions
        self.get_state = True
        #print(self.actual_arms_pos)

    def joy_callback(self, msg):
        spd = 0.5 # up, down
        roll = 0.3 # left, right
        if msg.data == 1:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2] + spd
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 4:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2] - spd
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 2:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3] + roll
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 3:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            if self.actual_arms_pos[3] > -1.05:
                self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3] - roll
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)

        elif msg.data == 5:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0] + spd
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 8:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0] - spd
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1]
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 6:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            if self.actual_arms_pos[1] > -1.05:
                self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1] - roll
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
        elif msg.data == 7:
            self.arms_mov.l_shoulder_pitch = self.actual_arms_pos[2]
            self.arms_mov.l_shoulder_roll = self.actual_arms_pos[3]
            self.arms_mov.r_shoulder_pitch = self.actual_arms_pos[0]
            self.arms_mov.r_shoulder_roll = self.actual_arms_pos[1] + roll
            print(self.arms_mov)
            self.arms_cmd_pub.publish(self.arms_mov)
            
            

    def mov_arms(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
       # rospy.loginfo("Got arm's positions")
        
        while (self.actual_arms_pos[0] < self.arms_mov.r_shoulder_pitch - 0.06 or self.actual_arms_pos[0] > self.arms_mov.r_shoulder_pitch + 0.06) or\
              (self.actual_arms_pos[1] < self.arms_mov.r_shoulder_roll - 0.05 or self.actual_arms_pos[1] > self.arms_mov.r_shoulder_roll + 0.05) or\
              (self.actual_arms_pos[2] < self.arms_mov.l_shoulder_pitch - 0.06 or self.actual_arms_pos[2] > self.arms_mov.l_shoulder_pitch + 0.06) or\
              (self.actual_arms_pos[3] < self.arms_mov.l_shoulder_roll - 0.05 or self.actual_arms_pos[3] > self.arms_mov.l_shoulder_roll + 0.05):
            #rospy.loginfo(self.actual_arms_pos[0])
            self.arms_cmd_pub.publish(self.arms_mov)
            self.rate.sleep()

        rospy.loginfo("Moved")
            
            

    def wave(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
            
        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing wave!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving right hand up")
        self.arms_mov.r_shoulder_pitch = 2.13
        self.mov_arms()

        rospy.loginfo("Moving right hand to right")
        self.arms_mov.r_shoulder_roll = -0.75
        self.mov_arms()

        rospy.loginfo("Moving right hand to left")
        self.arms_mov.r_shoulder_roll = -1.25
        self.mov_arms()

        rospy.loginfo("Moving right hand to right")
        self.arms_mov.r_shoulder_roll = -1.0
        self.mov_arms()


        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("waved!!!")

    def highfive(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
            
        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing high five!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving right hand up")
        self.arms_mov.r_shoulder_pitch = 2.13
        self.mov_arms()

        rospy.loginfo("Moving right little down")
        self.arms_mov.r_shoulder_pitch = 1.85
        self.mov_arms()

        rospy.loginfo("Moving right hand up")
        self.arms_mov.r_shoulder_pitch = 2.13
        self.mov_arms()


        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("High Five!!!")


    def reset_arms(self):
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("Reset Done")
        
    def point(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()

        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing Point!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving left hand up")
        self.arms_mov.l_shoulder_pitch = 2.13
        self.mov_arms()
        duration = rospy.Duration(2.0)
        rospy.sleep(duration)

        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("pointed!!!")

    def alert(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
            
        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing alert!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving hands up")
        self.arms_mov.r_shoulder_pitch = 2.13
        self.arms_mov.l_shoulder_pitch = 2.13
        self.mov_arms()

##        rospy.loginfo("Moving hands to right")
##        self.arms_mov.r_shoulder_roll = -0.75
##        self.arms_mov.l_shoulder_roll = -0.75
##        self.mov_arms()
##
##        rospy.loginfo("Moving hands to left")
##        self.arms_mov.r_shoulder_roll = -1.25
##        self.arms_mov.l_shoulder_roll = -1.25
##        self.mov_arms()

        rospy.loginfo("Moving hands center")
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()


        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("Alerted!!!")

    def hug(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
            
        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing hug!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving hands up")
        self.arms_mov.r_shoulder_pitch = 2.13
        self.arms_mov.l_shoulder_pitch = 2.13
        self.mov_arms()

        

        rospy.loginfo("Moving hands to close")
        self.arms_mov.r_shoulder_roll = -1.25
        self.arms_mov.l_shoulder_roll = -1.25
        self.mov_arms()
        rospy.loginfo("Waiting 2 sec")
        time.sleep(2)

        rospy.loginfo("Moving hands apart")
        self.arms_mov.r_shoulder_roll = -0.75
        self.arms_mov.l_shoulder_roll = -0.75
        self.mov_arms()


        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("Hugged!!!")

    def fist_bump(self):
        while not self.get_state:
            rospy.logerr("Unable to get the Arm's position")
            self.rate.sleep()
            
        rospy.loginfo("Got arm's positions")
        rospy.loginfo("Initializing Fist Bump!")
        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()

        rospy.loginfo("Moving hand up")
        self.arms_mov.r_shoulder_pitch = 1.7
        #self.arms_mov.l_shoulder_pitch = 1.7
        self.mov_arms()

        rospy.loginfo("Waiting 2 sec")
        time.sleep(2)

        rospy.loginfo("Reseting arms postions")
        self.arms_mov.r_shoulder_pitch = 0.0
        self.arms_mov.r_shoulder_roll = -1.0
        self.arms_mov.l_shoulder_pitch = 0.0
        self.arms_mov.l_shoulder_roll = -1.0
        self.mov_arms()
        rospy.loginfo("Fist Bumped!!!")
    
    def mov_forward(self, d):
        self.cmd_vel_msg = Twist()
        speed = 0.2
        distance = d # 0.5 meters
        
        linear_velocity = speed
        duration = distance / speed

        self.cmd_vel_msg.linear.x = linear_velocity
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        print("Moving Forward")
        start_time = time.time()
        flag = False
        while not flag:
            self.cmd_vel_pub.publish(self.cmd_vel_msg)
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                flag = True

        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)
        print("Moved")

    def mov_backward(self,d):
        self.cmd_vel_msg = Twist()
        speed = 0.2
        distance = d # 0.5 meters
        
        linear_velocity = speed
        duration = distance / speed

        self.cmd_vel_msg.linear.x = -1.0 * linear_velocity
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        print("Moving backward")
        start_time = time.time()
        flag = False
        while not flag:
            self.cmd_vel_pub.publish(self.cmd_vel_msg)
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                flag = True

        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)
        print("Moved")

    def rot_left(self, d):
        self.cmd_vel_msg = Twist()
        speed = 0.1
        distance = d * 0.00371141975308642 # 0.5 meters
        
        linear_velocity = speed
        duration = distance / speed

        self.cmd_vel_msg.linear.x = 0.0#linear_velocity
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = 0.5
        print("rotating left")
        start_time = time.time()
        flag = False
        while not flag:
            self.cmd_vel_pub.publish(self.cmd_vel_msg)
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                flag = True

        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)
        print("Moved")

    def rot_right(self, d):
        self.cmd_vel_msg = Twist()
        speed = 0.1
        distance = d * 0.00371141975308642 # 0.5 meters
        
        linear_velocity = speed
        duration = distance / speed

        self.cmd_vel_msg.linear.x = 0.0#linear_velocity
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = -0.5
        print("rotating right")
        start_time = time.time()
        flag = False
        while not flag:
            self.cmd_vel_pub.publish(self.cmd_vel_msg)
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= duration:
                flag = True

        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)
        print("Moved")
                
        
    def run(self):
        while not rospy.is_shutdown():
            self.rate.sleep()

def mvmnt_gui_Callback(data):
    global mvmnt, dst
    mvmnt = data.data
    dst = data.angle_dist

def mvmnt_Callback(data):
    global mvmnt
    mvmnt = data.data
    
    #print(one, two, five)
##    if mvmnt_temp == 'point':
##        one = one + 1
##        two = 0
##        five = 0
##        if one > 60:
##            mvmnt = 'point'
##
##        else:
##            mvmnt = 'reset'
##            
##    elif mvmnt_temp == 'alert':
##        one = 0
##        two = two + 1
##        five = 0
##        if two > 60:
##            mvmnt = 'alert'
##
##        else:
##            mvmnt = 'reset'
##            
##    elif mvmnt_temp == 'wave':
##        one = 0
##        two = 0
##        five = five + 1
##        if five > 60:
##            mvmnt = 'wave'
##        else:
##            mvmnt = 'reset'
##
##    else:
##        mvmnt = 'reset'
        
    
##
flag_point = False
flag_alert = False
flag_wave = False
flag_forward = False
flag_reverse = False
flag_left = False
flag_right = False

if __name__ == '__main__':
    print("node started")
    movement = MovementControl()
    while not rospy.is_shutdown():
        #global mvmnt
        
        sub = rospy.Subscriber("/op_cmd", String, mvmnt_Callback)
        sub1 = rospy.Subscriber("/op_cmd_gui", Opcmd, mvmnt_gui_Callback)
        pub = rospy.Publisher("/response_to_action", String, queue_size = 1)
        response_data = String()
        response_data.data = "done"
        if mvmnt == 'point':
            print('----point---')
            movement.point()
            mvmnt = "reset"
##            pub.publish(response_data)
                

        elif mvmnt == 'alert':
            print('----alert---')
            movement.alert()
            mvmnt = "reset"
##            pub.publish(response_data)
            

        elif mvmnt == 'wave':
            print('----wave---')
            movement.wave()
            mvmnt = "reset"
##            pub.publish(response_data)
                

        elif mvmnt == 'forward':
            print('----forward---')
            movement.mov_forward(0.5)
            mvmnt = "reset"
##            pub.publish(response_data)

        elif mvmnt == 'reverse':
            print('----backward---')
            movement.mov_backward(0.5)
            mvmnt = "reset"
##            pub.publish(response_data)

        elif mvmnt == 'left':
            print('----left---')
            movement.rot_left(1.0)
            mvmnt = "reset"
##            pub.publish(response_data)

        elif mvmnt == 'right':
            print('----right---')
            movement.rot_right(1.0)
            mvmnt = "reset"
##            pub.publish(response_data)

        elif mvmnt == 'pointb':
            print('----point---')
            movement.point()
            mvmnt = "reset"
            pub.publish(response_data)
                

        elif mvmnt == 'alertb':
            print('----alert---')
            movement.alert()
            mvmnt = "reset"
            pub.publish(response_data)
            

        elif mvmnt == 'waveb':
            print('----wave---')
            movement.wave()
            mvmnt = "reset"
            pub.publish(response_data)
                

        elif mvmnt == 'forwardb':
            print('----forward---')
            movement.mov_forward(dst)
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'reverseb':
            print('----backward---')
            movement.mov_backward(dst)
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'leftb':
            print('----left---')
            movement.rot_left(dst)
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'rightb':
            print('----right---')
            movement.rot_right(dst)
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'RESET_ARMS':
            print('----reseting arm---')
            movement.reset_arms()
            mvmnt = "reset"
##            pub.publish(response_data)

        elif mvmnt == 'hugb':
            print("----hugging---")
            movement.hug()
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'hug':
            print("----hugging---")
            movement.hug()
            mvmnt = "reset"
            #pub.publish(response_data)

        elif mvmnt == 'fist_bumpb':
            print("----fist bump---")
            movement.fist_bump()
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'fist_bump':
            print("----fist bump---")
            movement.fist_bump()
            mvmnt = "reset"
            #pub.publish(response_data)

        elif mvmnt == 'high_fiveb':
            print("----high five---")
            movement.highfive()
            mvmnt = "reset"
            pub.publish(response_data)

        elif mvmnt == 'high_five':
            print("----high five---")
            movement.highfive()
            mvmnt = "reset"
            #pub.publish(response_data)

##        highfive
                    

##        elif mvmnt == 'alert':
##            print('----alert---')
##            movement.alert()
##            mvmnt = 'reset'
##
##        elif mvmnt == 'wave':
##            print('----wave---')
##            movement.wave()
##            mvmnt = 'reset'
        

