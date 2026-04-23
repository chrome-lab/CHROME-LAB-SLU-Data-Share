#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import Int64
from quori_gui.msg import Opcmd
from std_msgs.msg import Int64
import time

class joystick:
    def __init__(self):
        rospy.init_node('joy_node', anonymous=True)

        self.forward = False
        self.backward = False
        self.left = False
        self.right = False

        self.l_up = False
        self.l_down = False
        self.l_left = False
        self.l_right = False

        self.r_up = False
        self.r_down = False
        self.r_left = False
        self.r_right = False

        self.manual_mode = 0
        
        rospy.Subscriber("joy", Joy, self.joy_callback)
        self.key_joy_pub = rospy.Publisher("/virtual_joy", Int64, queue_size=1)
        self.semi_cmd = rospy.Publisher("/op_cmd_gui", Opcmd, queue_size=-1)
        
        self.cmd_vel_pub = rospy.Publisher('/custom/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber("/video_mode", Int64, self.set_mode)
        self.cmd_vel_msg = Twist()
        self.speed = 0.2
        self.rot = 0.5

        self.l_timer = [0, 0, 0, 0] # left joystick timer for up, down, left, right
        self.r_timer = [0, 0, 0, 0]
        self.l_timer_flag = [False, False, False, False]
        self.r_timer_flag = [False, False, False, False]
        
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

    def set_mode(self, data):
        self.manual_mode = data.data
        self.l_timer_flag = [False, False, False, False]
        self.r_timer_flag = [False, False, False, False]
        self.r_left = False
        self.r_right = False
        self.r_up = False
        self.r_down = False
        self.l_left = False
        self.l_right = False
        self.l_up = False
        self.l_down = False

    def reset_semi(self):
        self.l_timer_flag = [False, False, False, False]
        self.r_timer_flag = [False, False, False, False]

    def joy_callback(self,data):
        #rospy.loginfo("Axes: %s", data.axes)
        #rospy.loginfo("Buttons: %s", data.buttons)
        temp_data = Opcmd()

##        if data.buttons[3] == 1.0:
##            print("-- wave")
##            temp_data.data = 'waveb'
##            self.semi_cmd.publish(temp_data)
##        elif data.buttons[0] == 1.0:
##            print("-- point")
##            temp_data.data = 'pointb'
##            self.semi_cmd.publish(temp_data)
##        elif data.buttons[1] == 1.0:
##            print("-- alert")
##            temp_data.data = 'alertb'
##            self.semi_cmd.publish(temp_data)
##        el
        if data.buttons[2] == 1.0:
            print("-- reset arms")
            temp_data.data = "RESET_ARMS"
            temp_data.angle_dist = 0.0
            self.semi_cmd.publish(temp_data)
            
        if self.manual_mode == 0:
            if data.axes[5] == 1.0:
                self.forward = True
                self.backward = False
                self.left = False
                self.right = False
            elif data.axes[5] == -1.0:
                self.forward = False
                self.backward = True
                self.left = False
                self.right = False

            elif data.axes[4] == 1.0:
                self.left = True
                self.right = False
                self.forward = False
                self.backward = False
            elif data.axes[4] == -1.0:
                self.left  =False
                self.right = True
                self.forward = False
                self.backward = False
            else:
                self.left = False
                self.right = False
                self.forward = False
                self.backward = False

            if data.axes[1] == 1.0:
                self.l_up = True
                self.l_down = False
                self.l_left = False
                self.l_right = False
            elif data.axes[1] == -1.0:
                self.l_up = False
                self.l_down = True
                self.l_left = False
                self.l_right = False

            elif data.axes[0] == 1.0:
                self.l_left = True
                self.l_right = False
                self.l_up = False
                self.l_down = False
            elif data.axes[0] == -1.0:
                self.l_left  =False
                self.l_right = True
                self.l_up = False
                self.l_down = False
            else:
                self.l_left = False
                self.l_right = False
                self.l_up = False
                self.l_down = False

            if data.axes[3] == 1.0:
                self.r_up = True
                self.r_down = False
                self.r_left = False
                self.r_right = False
            elif data.axes[3] == -1.0:
                self.r_up = False
                self.r_down = True
                self.r_left = False
                self.r_right = False

            elif data.axes[2] == 1.0:
                self.r_left = True
                self.r_right = False
                self.r_up = False
                self.r_down = False
            elif data.axes[2] == -1.0:
                self.r_left  =False
                self.r_right = True
                self.r_up = False
                self.r_down = False
            else:
                self.r_left = False
                self.r_right = False
                self.r_up = False
                self.r_down = False

        else:
            if data.axes[3] == 1.0: #right_up
                self.r_timer_flag[0] = True
            else:
                self.r_timer_flag[0] = False
                
            if data.axes[3] == -1.0:
                self.r_timer_flag[1] = True
            else:
                self.r_timer_flag[1] = False
                
            if data.axes[2] == 1.0:
                self.r_timer_flag[2] = True
            else:
                self.r_timer_flag[2] = False
                
            if data.axes[2] == -1.0:
                self.r_timer_flag[3] = True
            else:
                self.r_timer_flag[3] = False


            if data.axes[1] == 1.0: #left_up
                self.l_timer_flag[0] = True
            else:
                self.l_timer_flag[0] = False
                
            if data.axes[1] == -1.0:
                self.l_timer_flag[1] = True
            else:
                self.l_timer_flag[1] = False

            if data.axes[0] == 1.0:
                self.l_timer_flag[2] = True
            else:
                self.l_timer_flag[2] = False
                
            if data.axes[0] == -1.0:
                self.l_timer_flag[3] = True
            else:
                self.l_timer_flag[3] = False
            
        
                
                

        

    
if __name__ == "__main__":
    joy = joystick()
    rate = rospy.Rate(5) # 10Hz
    cmd = Int64()

    r_up_flag = False
    r_right_flag = False
    r_right_timer = time.perf_counter()
    r_up_timer = time.perf_counter()
    
    while not rospy.is_shutdown():
        if joy.forward == True:
            print("Forward")
            joy.cmd_vel_msg.linear.x = joy.speed
            joy.cmd_vel_msg.angular.z = 0.0
            joy.cmd_vel_pub.publish(joy.cmd_vel_msg)
        
        elif joy.backward == True:
            print("backward")
            joy.cmd_vel_msg.linear.x = -1.0*joy.speed
            joy.cmd_vel_msg.angular.z = 0.0
            joy.cmd_vel_pub.publish(joy.cmd_vel_msg)

        elif joy.left == True:
            print("Left")
            joy.cmd_vel_msg.linear.x = 0.0
            joy.cmd_vel_msg.angular.z = joy.rot
            joy.cmd_vel_pub.publish(joy.cmd_vel_msg)
            
        elif joy.right == True:
            print("right")
            joy.cmd_vel_msg.linear.x = 0.0
            joy.cmd_vel_msg.angular.z = -1.0*joy.rot
            joy.cmd_vel_pub.publish(joy.cmd_vel_msg)
        else:
            joy.cmd_vel_msg.linear.x = 0.0
            joy.cmd_vel_msg.angular.z = 0.0

        if joy.l_up == True:
            cmd.data = 1
            joy.key_joy_pub.publish(cmd)
            
        elif joy.l_left == True:
            cmd.data = 2
            joy.key_joy_pub.publish(cmd)

        elif joy.l_down == True:
            cmd.data = 4
            joy.key_joy_pub.publish(cmd)

        elif joy.l_right == True:
            cmd.data = 3
            joy.key_joy_pub.publish(cmd)

        if joy.r_up == True:
            cmd.data = 5
            joy.key_joy_pub.publish(cmd)
            
        elif joy.r_left == True:
            cmd.data = 6
            joy.key_joy_pub.publish(cmd)

        elif joy.r_down == True:
            cmd.data = 8
            joy.key_joy_pub.publish(cmd)

        elif joy.r_right == True:
            cmd.data = 7
            joy.key_joy_pub.publish(cmd)


        if joy.r_timer_flag[0] == False:
            joy.r_timer[0] = time.perf_counter()

        if joy.r_timer_flag[1] == False:
            joy.r_timer[1] = time.perf_counter()

        if joy.r_timer_flag[2] == False:
            joy.r_timer[2] = time.perf_counter()

        if joy.r_timer_flag[3] == False:
            joy.r_timer[3] = time.perf_counter()
            

        if joy.l_timer_flag[0] == False:
            joy.l_timer[0] = time.perf_counter()

        if joy.l_timer_flag[1] == False:
            joy.l_timer[1] = time.perf_counter()

        if joy.l_timer_flag[2] == False:
            joy.l_timer[2] = time.perf_counter()

        if joy.l_timer_flag[3] == False:
            joy.l_timer[3] = time.perf_counter()

        l_up = time.perf_counter() - joy.l_timer[0]
        l_down = time.perf_counter() - joy.l_timer[1]
        l_left = time.perf_counter() - joy.l_timer[2]
        l_right = time.perf_counter() - joy.l_timer[3]

        r_up = time.perf_counter() - joy.r_timer[0]
        r_down = time.perf_counter() - joy.r_timer[1]
        r_left = time.perf_counter() - joy.r_timer[2]
        r_right = time.perf_counter() - joy.r_timer[3]

        cmd = Opcmd()

        if float(r_up) >= 2.0:
            if float(l_up) <= 1.0 and l_down <= 1.0:
                print("-----High Five\n")
                cmd.data = "high_fiveb"
                joy.semi_cmd.publish(cmd)
                joy.reset_semi()
            elif l_up >= 2.0:
                print("-----Alert\n")
                cmd.data = "alertb"
                joy.semi_cmd.publish(cmd)
                joy.reset_semi()

##        if l_up >=2.0 and r_up <=1.9:
##            print("-----Point\n")
##            cmd.data = "pointb"
##            joy.semi_cmd.publish(cmd)
##            joy.reset_semi()

        if l_right >= 2.0 and r_left>=2.0:
            print("-----hug\n")
            cmd.data = "hugb"
            joy.semi_cmd.publish(cmd)
            joy.reset_semi()

##        if l_down >=2.0 and r_up >=2.0:
##            print("-----fist bump\n")
##            cmd.data = "fist_bumpb"
##            joy.semi_cmd.publish(cmd)
##            joy.reset_semi()
##
##        if l_left >=2.0 and r_right >= 2.0:
##            print("-----wave\n")
##            cmd.data = "waveb"
##            joy.semi_cmd.publish(cmd)
##            joy.reset_semi()

        if r_up >= 0.5 and r_up <= 1.5 and r_up_flag == False:
            r_up_flag = True
            print("right joy is up for the said time")
            r_up_timer = time.perf_counter()
        else:
            if time.perf_counter()-r_up_timer >= 2.5:
                r_up_flag = False

        if r_right >= 0.5 and r_right <= 1.5 and r_right_flag == False:
            r_right_flag = True
            print("right joy is right for the said time")
            r_right_timer = time.perf_counter()
        else:
            if time.perf_counter()-r_right_timer >= 2.5:
                r_right_flag = False
                

        if r_left >= 0.5 and r_right_flag:
            print("-----wave\n")
            cmd.data = "waveb"
            joy.semi_cmd.publish(cmd)
            joy.reset_semi()
            r_right_flag = False
                

        if r_down >= 0.5 and r_up_flag:
            print("-----fist bump\n")
            cmd.data = "fist_bumpb"
            joy.semi_cmd.publish(cmd)
            joy.reset_semi()
            r_up_flag = False
            
        elif r_up <= 0.45 and r_up >= 0.25 and r_up_flag:
            print("-----point\n")
            cmd.data = "pointb"
            joy.semi_cmd.publish(cmd)
            joy.reset_semi()
            r_up_flag = False
            
        

        print("{:.2f}".format(l_up),
              "{:.2f}".format(l_down),
              "{:.2f}".format(l_left),
              "{:.2f}".format(l_right))
        
        print("{:.2f}".format(r_up),
              "{:.2f}".format(r_down),
              "{:.2f}".format(r_left),
              "{:.2f}".format(r_right))

        print()
            
        
        rate.sleep()

