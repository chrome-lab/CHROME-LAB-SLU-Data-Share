#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image, CompressedImage, Joy
#import pyautogui
from cv_bridge import CvBridge
import cv2
import tkinter as tk
from PIL import Image as PILImage, ImageTk
from std_msgs.msg import Int64, String
from geometry_msgs.msg import Twist
from control_msgs.msg import JointTrajectoryControllerState

from quori_gui.msg import Opcmd
import os
import time

class DelayKey:
    def __init__(self, sec):
        self.ctime = time.perf_counter()
        self.flag = False
        self.sec = sec

    def update(self):
        if time.perf_counter() - self.ctime > (self.sec + 0.5):
            self.flag = False
            
        if self.flag == False:
            self.ctime = time.perf_counter()
            self.flag = True

        if time.perf_counter() - self.ctime >= self.sec and self.flag:
            #print("{:.3f}".format(time.perf_counter() - self.ctime))
            self.flag = False
            return True
        
        return False

class ROSGUI:
    def __init__(self, root, width, height, background_image):
        self.root = root
        self.root.title("ROS GUI")
        self.root.geometry(f"{width}x{height}")

        # Publishers
        self.video_mode_pub = rospy.Publisher("/video_mode", Int64, queue_size = 1)
        self.video_mode = Int64()
        self.video_mode.data = 0
        self.video_mode_pub.publish(self.video_mode)

        self.semi_button_pub = rospy.Publisher("/op_cmd_gui", Opcmd, queue_size = -1)
        self.semi_button_data = Opcmd()

        self.key_joy_pub = rospy.Publisher("/virtual_joy", Int64, queue_size=1)

        rospy.Subscriber("/response_to_action", String, self.response_callback)
        #rospy.Subscriber("/joy", Joy, self.joy_callback)
        
        self.cmd_vel_pub = rospy.Publisher('/custom/cmd_vel', Twist, queue_size=10)
        self.cmd_vel_msg = Twist()
        self.speed = 0.2
        self.rot = 0.5
        
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.linear.z = 0.0
        self.cmd_vel_msg.angular.x = 0.0
        self.cmd_vel_msg.angular.y = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

        # Load background image
        bg_image = PILImage.open(background_image)
        bg_image = ImageTk.PhotoImage(bg_image)
        self.background_label = tk.Label(root, image=bg_image)
        self.background_label.image = bg_image
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.v_label = tk.Label(root)
        
        self.video_canvas = tk.Canvas(root, width=640, height=480, bg="#0E2429")
        self.video_canvas.place(x=0, y=0)

##        self.f_video_canvas = tk.Canvas(root, width=345, height=240, bg="#0E2429")
##        self.f_video_canvas.place(x=647, y=0)


        self.video_mode_button = tk.Button(root, text="Start Video Modes!", command=self.video_mode_button_callback)
        self.video_mode_button.place(x=15, y=500)
        self.video_mode_flag = True

        
        

        #subscriber
        rospy.Subscriber('/quori/joint_trajectory_controller/state',
                         JointTrajectoryControllerState,
                         self.get_actual_pos)

        # Subscribe to the image topic
        rospy.Subscriber("/webcam/image_overlaid", Image, self.image_callback)
##        rospy.Subscriber("/astra_ros/devices/default/color/image_color/compressed",
##                         CompressedImage, self.front_cam_callback)
##        # Initialize CV bridge
        self.bridge = CvBridge()

        self.root.bind('<Motion>', self.mouse_motion_callback)
        root.bind("<Up>", self.up_key_pressed)
        root.bind("<Down>", self.down_key_pressed)
        root.bind("<Left>", self.left_key_pressed)
        root.bind("<Right>", self.right_key_pressed)
        root.bind('<KeyPress>', self.key_press)

##        root.bind('<KeyPress-t>', self.testing)
##        self.t = DelayKey(2.0)
        #root.bind('<KeyRelease-t>', self.testingr)
##        self.p_time = time.perf_counter()
##        self.t_flag = False
        
        root.bind('<i>', self.on_key_i)
        root.bind('<j>', self.on_key_j)
        root.bind('<k>', self.on_key_k)
        root.bind('<l>', self.on_key_l)

        root.bind('<a>', self.on_key_a)
        root.bind('<s>', self.on_key_s)
        root.bind('<d>', self.on_key_d)
        root.bind('<w>', self.on_key_w)

        root.bind('<KeyPress-3>', self.on_key_z) #wave
        self.z = DelayKey(2.0)
        
        root.bind('<KeyPress-2>', self.on_key_v) #point
        self.v = DelayKey(2.0)
        
        root.bind('<KeyPress-6>', self.on_key_c) #alert
        self.c = DelayKey(2.0)
        
        root.bind('<KeyPress-1>', self.on_key_x) #fist bump
        self.x = DelayKey(2.0)
        
        root.bind('<KeyPress-5>', self.on_key_b) #high five
        self.b = DelayKey(2.0)
        
        root.bind('<KeyPress-4>', self.on_key_n) #hug
        self.n = DelayKey(2.0)
        
        

##        root.bind("<KeyRelease-Up>", self.up_key_released)
##        root.bind("<KeyRelease-Down>", self.down_key_released)
##        root.bind("<KeyRelease-Left>", self.left_key_released)
##        root.bind("<KeyRelease-Right>", self.right_key_released)

        #labels
        self.mode_label_actions = tk.Label(root, text="--- Actions for semi autonomous", font=("Helvetica", 14, "bold"), bg="#282828", fg="white")
        self.mode_label_actions.place(x=15, y=553)

        self.semi_mode_label = tk.Label(root, text="--- Arms Position", font=("Helvetica", 14, "bold"), bg="#282828", fg="white")
        self.semi_mode_label.place(x=665, y=8) 

        self.semi_mode_label = tk.Label(root, text="--- Actions Sequence", font=("Helvetica", 14, "bold"), bg="#282828", fg="white")
        self.semi_mode_label.place(x=665, y=180)

        self.semi_mode_label = tk.Label(root, text="Left Arm Roll:", font=("Helvetica", 14), bg="#282828", fg="white")
        self.semi_mode_label.place(x=701, y=37)
        self.left_arm_roll_label = tk.Label(root, text=str(0.0), font=("Helvetica", 14), bg="#282828", fg="white")
        self.left_arm_roll_label.place(x=847, y=37)

        self.semi_mode_label = tk.Label(root, text="Left Arm Pitch:", font=("Helvetica", 14), bg="#282828", fg="white")
        self.semi_mode_label.place(x=701, y=61)
        self.left_arm_pitch_label = tk.Label(root, text=str(0.0), font=("Helvetica", 14), bg="#282828", fg="white")
        self.left_arm_pitch_label.place(x=847, y=61)

        self.semi_mode_label = tk.Label(root, text="Right Arm Roll:", font=("Helvetica", 14), bg="#282828", fg="white")
        self.semi_mode_label.place(x=701, y=100)
        self.right_arm_roll_label = tk.Label(root, text=str(0.0), font=("Helvetica", 14), bg="#282828", fg="white")
        self.right_arm_roll_label.place(x=847, y=100)

        self.semi_mode_label = tk.Label(root, text="Right Arm Pitch:", font=("Helvetica", 14), bg="#282828", fg="white")
        self.semi_mode_label.place(x=701, y=124)
        self.right_arm_pitch_label = tk.Label(root, text=str(0.0), font=("Helvetica", 14), bg="#282828", fg="white")
        self.right_arm_pitch_label.place(x=847, y=124)

        #buttons
        self.semi_mode_wave = tk.Button(root, text="Wave", command=self.semi_mode_wave_callback)
        self.semi_mode_wave.place(x=45, y=580)

        self.semi_mode_point = tk.Button(root, text="Point", command=self.semi_mode_point_callback)
        self.semi_mode_point.place(x=120, y=580)

        self.semi_mode_alert = tk.Button(root, text="Alert", command=self.semi_mode_alert_callback)
        self.semi_mode_alert.place(x=191, y=580)

        self.semi_mode_forward = tk.Button(root, text="Forward", command=self.semi_mode_forward_callback)
        self.semi_mode_forward.place(x=261, y=580)
        self.forward_dist = tk.Text(root, width=9, height=1, fg="white", bg="black")
        self.forward_dist.place(x = 263, y = 615)
        

        self.semi_mode_reverse = tk.Button(root, text="Reverse", command=self.semi_mode_reverse_callback)
        self.semi_mode_reverse.place(x=353, y=580)
        self.reverse_dist = tk.Text(root, width=9, height=1, fg="white", bg="black")
        self.reverse_dist.place(x = 355, y = 615)

        self.semi_mode_left = tk.Button(root, text="Left", command=self.semi_mode_left_callback)
        self.semi_mode_left.place(x=445, y=580)
        self.left_rot = tk.Text(root, width=6, height=1, fg="white", bg="black")
        self.left_rot.place(x = 445, y = 615)

        self.semi_mode_right = tk.Button(root, text="Right", command=self.semi_mode_right_callback)
        self.semi_mode_right.place(x=509, y=580)
        self.right_rot = tk.Text(root, width=7, height=1, fg="white", bg="black")
        self.right_rot.place(x = 509, y = 615)

        ##############kill switch
        self.kill_switch = tk.Button(root, text="KILL", font=("Arial", 18, "bold"), width = 7,
                                     height=2, bg="#ff0000", fg="white", command=self.kill_callback)
        self.kill_switch.place(x=870, y=570)
        #########################

        self.delay_button = tk.Button(root, text="Delay (s)", command=self.delay_callback)
        self.delay_button.place(x=580, y=580)
        self.delay_time = tk.Text(root, width=10, height=1, fg="white", bg="black")
        self.delay_time.place(x = 580, y = 615)


        

        self.next= tk.Button(root, text="Next >>", command=self.next_callback)
        self.next.place(x=831, y=486)
##        self.next_flag = True
##        self.next.place(x=671, y=215)

        self.make_seq= tk.Button(root, text="Make Sequence", command=self.make_seq_callback)
        self.make_seq.place(x=671, y=220)
        self.make_seq_flag = False

        self.sequence_clear= tk.Button(root, text="Clear", command=self.sequence_clear)
        self.sequence_clear.place(x=853, y=220)

        #updated button
        self.auto_mode = tk.Button(root, text="Auto Start", command=self.auto_callback)
        self.auto_mode.place(x = 160, y = 500)
        self.auto_flag = False

        # add textbox
        self.text_seq = tk.Text(root, width=30, height=13, fg="white", bg="black")
        self.text_seq.place(x=670, y=255)
        

        self.semi_mode_wave.configure(state=tk.DISABLED)
        self.semi_mode_point.configure(state=tk.DISABLED)
        self.semi_mode_alert.configure(state=tk.DISABLED)
        self.semi_mode_forward.configure(state=tk.DISABLED)
        self.semi_mode_reverse.configure(state=tk.DISABLED)
        self.semi_mode_left.configure(state=tk.DISABLED)
        self.semi_mode_right.configure(state=tk.DISABLED)

        #updated
##        rospy.Duration(5000)
        self.video_mode_button_callback()


    def testing(self, event):
        if self.t.update():
            print("2 sec passed")
        #print("the test key pressed")
##        if time.perf_counter() - self.p_time >= 2.5:
##            self.t_flag = False
##            self.p_time = time.perf_counter()
##            
##        if self.t_flag == False:
##            self.p_time = time.perf_counter()
##            self.t_flag=True
##        if time.perf_counter() - self.p_time >= 2.0 and self.t_flag:
##            print("{:.3f}".format(time.perf_counter() - self.p_time))
##            self.t_flag = False
##            print("2 sec done")

    def testingr(self, event):
        print("the test key released")
        
    def on_key_i(self, event):
        if self.video_mode_flag == True:
            print("right arm up")
            cmd = Int64()
            cmd.data = 5
            self.key_joy_pub.publish(cmd)

    def on_key_j(self, event):
        if self.video_mode_flag == True:
            print("right arm left")
            cmd = Int64()
            cmd.data = 6
            self.key_joy_pub.publish(cmd)

    def on_key_k(self, event):
        if self.video_mode_flag == True:
            print("right arm down")
            cmd = Int64()
            cmd.data = 8
            self.key_joy_pub.publish(cmd)

    def on_key_l(self, event):
        if self.video_mode_flag == True:
            print("right arm right")            
            cmd = Int64()
            cmd.data = 7
            self.key_joy_pub.publish(cmd)

    def on_key_w(self, event):
        if self.video_mode_flag == True:
            print("left arm up")            
            cmd = Int64()
            cmd.data = 1
            self.key_joy_pub.publish(cmd)

    def on_key_a(self, event):
        if self.video_mode_flag == True:
            print("left arm left")            
            cmd = Int64()
            cmd.data = 2
            self.key_joy_pub.publish(cmd)

    def on_key_s(self, event):
        if self.video_mode_flag == True:
            print("left arm down")            
            cmd = Int64()
            cmd.data = 4
            self.key_joy_pub.publish(cmd)

    def on_key_d(self, event):
        if self.video_mode_flag == True:
            print("left arm right")            
            cmd = Int64()
            cmd.data = 3
            self.key_joy_pub.publish(cmd)
    
    def delay_callback(self):
##        print("The setted delay is ", self.delay_time.get("1.0", "1.end")," sec" )
        if self.make_seq_flag == True and self.delay_time.get("1.0", "1.end") != "":
            text = "delay,"+ self.delay_time.get("1.0", "1.end") + "\n"
            self.text_seq.insert("end", text)


    def kill_callback(self):
        print("Killing Initiated")
        nodes = os.popen("rosnode list").readlines()
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")

        for node in nodes:
            os.system("rosnode kill "+ node)

    def key_press(self, event):
        if event.char == 'h':
            if self.video_mode_flag == True:
                print("reset arms")
                
                self.semi_button_data.data = "RESET_ARMS"
                self.semi_button_data.angle_dist = 0.0
                self.semi_button_pub.publish(self.semi_button_data)

    def make_seq_callback(self):
        if self.make_seq_flag == False:
            self.make_seq.configure(bg="green")
            self.make_seq_flag = True
            self.next.configure(state=tk.DISABLED)
        else:
            self.make_seq_flag = False
            self.make_seq.configure(bg="#d9d9d9")
            self.next.configure(state=tk.NORMAL)
            
            
    def response_callback(self, msg):
        if msg.data == "done":
            self.next.configure(state=tk.NORMAL)
            if self.auto_flag == False:
                self.semi_mode_wave.configure(state=tk.NORMAL)
                self.semi_mode_point.configure(state=tk.NORMAL)
                self.semi_mode_alert.configure(state=tk.NORMAL)
                self.semi_mode_forward.configure(state=tk.NORMAL)
                self.semi_mode_reverse.configure(state=tk.NORMAL)
                self.semi_mode_left.configure(state=tk.NORMAL)
                self.semi_mode_right.configure(state=tk.NORMAL)
                self.video_mode_button.configure(state=tk.NORMAL)
                self.next.configure(state=tk.NORMAL)
                self.auto_mode.configure(text="Auto Start")
            else:
                if self.text_seq.get("1.0", "1.end") == "":
                    print("flag false")
                    auto_flag = False
                    self.auto_mode.configure(text="Auto Start")
                    self.video_mode_button.configure(state=tk.NORMAL)
                    self.semi_mode_wave.configure(state=tk.NORMAL)
                    self.semi_mode_point.configure(state=tk.NORMAL)
                    self.semi_mode_alert.configure(state=tk.NORMAL)
                    self.semi_mode_forward.configure(state=tk.NORMAL)
                    self.semi_mode_reverse.configure(state=tk.NORMAL)
                    self.semi_mode_left.configure(state=tk.NORMAL)
                    self.semi_mode_right.configure(state=tk.NORMAL)
                    self.next.configure(state=tk.NORMAL)
                    self.video_mode_button.configure(state=tk.NORMAL)
                else:
                    print("calling next sequence")
                    self.next_callback()
##                    time.sleep(int(self.spinbox.get()))

            

    def sequence_clear(self):
        self.text_seq.delete("1.0", "end")
        

    def next_callback(self):
        print("Sequence")
        current_action_tmp = self.text_seq.get("1.0", "1.end")
        self.current_action = current_action_tmp.split(",")
##        print(self.current_action)
        self.text_seq.delete("1.0", "1.end+1c")
##        self.next.configure(state=tk.DISABLED)
##        self.next_flag = False

        self.semi_mode_wave.configure(state=tk.DISABLED)
        self.semi_mode_point.configure(state=tk.DISABLED)
        self.semi_mode_alert.configure(state=tk.DISABLED)
        self.semi_mode_forward.configure(state=tk.DISABLED)
        self.semi_mode_reverse.configure(state=tk.DISABLED)
        self.semi_mode_left.configure(state=tk.DISABLED)
        self.semi_mode_right.configure(state=tk.DISABLED)

        

        if self.current_action[0] == "wave":
            self.next.configure(state=tk.DISABLED)
            self.semi_mode_wave_callback()
        elif self.current_action[0] == "point":
            self.next.configure(state=tk.DISABLED)
            self.semi_mode_point_callback()
        
        elif self.current_action[0] == "alert":
            self.next.configure(state=tk.DISABLED)
            self.semi_mode_alert_callback()
        elif self.current_action[0] == "delay":
            time.sleep(int(self.current_action[1]))
            self.next.configure(state=tk.NORMAL)
            self.next_callback()

        else:
            self.semi_mode_seq(self.current_action[0] ,float(self.current_action[1]))
        
        

    def auto_callback(self):
        if self.auto_flag == True:
            self.auto_flag = False
            self.auto_mode.configure(text="Auto Start")
            self.video_mode_button.configure(state=tk.NORMAL)
            self.next.configure(state=tk.NORMAL)
        else:
            self.auto_flag = True
            self.auto_mode.configure(text="Auto Stop")
            self.next.configure(state=tk.DISABLED)
            self.video_mode_button.configure(state=tk.DISABLED)
            self.make_seq_flag = False
            self.make_seq.configure(bg="#d9d9d9")
            self.next.configure(state=tk.NORMAL)
            
            if self.text_seq.get("1.0", "1.end") != "":
                self.next_callback()
            else:
                self.auto_flag = False
                self.video_mode_button.configure(state=tk.NORMAL)
                self.next.configure(state=tk.NORMAL)
                
    def map_value(self, x, min_from, max_from, min_to, max_to):
        y = min_to + ((x - min_from) / (max_from - min_from)) * (max_to - min_to)
        return y

    def get_actual_pos(self, msg):
        self.actual_arms_pos = msg.actual.positions
        self.left_arm_roll_label.configure(text="{:.1f}".format(self.map_value(self.actual_arms_pos[3],-1, 1.288, 15, 140)))
        self.left_arm_pitch_label.configure(text="{:.1f}".format(self.map_value(self.actual_arms_pos[2],0, 2.385, 0, 125)))
        self.right_arm_roll_label.configure(text="{:.1f}".format(self.map_value(self.actual_arms_pos[1], -1, 1.284, 15, 150)))
        self.right_arm_pitch_label.configure(text="{:.1f}".format(self.map_value(self.actual_arms_pos[0], 0, 2.389, 0, 130)))

    def get_dist(self, name):
        if name == "forward":
            dist = self.forward_dist.get("1.0", "1.end")
            if dist == "":
                return 1.0
            else:
                return float(dist)
        elif name == "reverse":
            dist = self.reverse_dist.get("1.0", "1.end")
            if dist == "":
                return 1.0
            else:
                return float(dist)
        elif name == "left":
            dist = self.left_rot.get("1.0", "1.end")
            if dist == "":
                return 1.0
            else:
                return float(dist)

        elif name == "right":
            dist = self.right_rot.get("1.0", "1.end")
            if dist == "":
                return 1.0
            else:
                return float(dist)

    def semi_mode_right_callback(self):
        print("Right Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'rightb'
            self.semi_button_data.angle_dist = self.get_dist("right")
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            dist = self.right_rot.get("1.0", "1.end")
            if dist == "":
                text = "right,45\n"
            else:
                text = "right,"+ dist + "\n"
            self.text_seq.insert("end", text)
        
    def semi_mode_left_callback(self):
        print("Left Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'leftb'
            self.semi_button_data.angle_dist = self.get_dist("left")
            self.semi_button_pub.publish(self.semi_button_data)
            
        else:
            dist = self.left_rot.get("1.0", "1.end")
            if dist == "":
                text = "left,45\n"
            else:
                text = "left,"+ dist + "\n"
            self.text_seq.insert("end", text)

    

    def semi_mode_reverse_callback(self):
        print("Reverse Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'reverseb'
            self.semi_button_data.angle_dist = self.get_dist("reverse")
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            dist = self.reverse_dist.get("1.0", "1.end")
            if dist == "":
                text = "reverse,1.0\n"
            else:
                text = "reverse,"+ dist + "\n"
            self.text_seq.insert("end", text)

    

    def semi_mode_forward_callback(self):
        print("Forward Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'forwardb'
            self.semi_button_data.angle_dist = self.get_dist("forward")
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            dist = self.forward_dist.get("1.0", "1.end")
            if dist == "":
                text = "forward,1.0\n"
            else:
                text = "forward,"+ dist + "\n"
            self.text_seq.insert("end", text)

    def semi_mode_seq(self, cmd ,dist):
##        print("Pressed with dist ", dist)
        self.semi_button_data.data = cmd + "b"
        self.semi_button_data.angle_dist = dist
        self.semi_button_pub.publish(self.semi_button_data)

##    def semi_mode_reverse_seq(self, dist):
##        print("Reverse Pressed with dist ", dist)
##        self.semi_button_data.data = 'reverseb'
##        self.semi_button_data.angle_dist = dist
##        self.semi_button_pub.publish(self.semi_button_data)
##
##    def semi_mode_left_seq(self, dist):
##        print("Reverse Pressed with dist ", dist)
##        self.semi_button_data.data = 'leftb'
##        self.semi_button_data.angle_dist = dist
##        self.semi_button_pub.publish(self.semi_button_data)
##
##    def semi_mode_right_seq(self, dist):
##        print("Reverse Pressed with dist ", dist)
##        self.semi_button_data.data = 'rightb'
##        self.semi_button_data.angle_dist = dist
##        self.semi_button_pub.publish(self.semi_button_data)
        
    def on_key_z(self, event):
        if self.video_mode_flag == False and self.z.update():
            self.semi_mode_wave_callback()

    def on_key_v(self, event):
        if self.video_mode_flag == False and self.v.update():
            self.semi_mode_point_callback()

    def on_key_c(self, event):
        if self.video_mode_flag == False and self.c.update():
            self.semi_mode_alert_callback()

    def on_key_x(self, event):
        if self.video_mode_flag == False and self.x.update():
            self.semi_button_data.data = 'fist_bumpb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)

    def on_key_b(self, event):
        if self.video_mode_flag == False and self.b.update():
            self.semi_button_data.data = 'high_fiveb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)

    def on_key_n(self, event):
        if self.video_mode_flag == False and self.n.update():
            self.semi_button_data.data = 'hugb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)
        
    def semi_mode_wave_callback(self):
        print("Wave Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'waveb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            self.text_seq.insert("end", "wave\n")

    def semi_mode_point_callback(self):
        print("Point Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'pointb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            self.text_seq.insert("end", "point\n")

    def semi_mode_alert_callback(self):
        print("Alert Pressed")
        if self.make_seq_flag == False:
            self.semi_button_data.data = 'alertb'
            self.semi_button_data.angle_dist = 0.0
            self.semi_button_pub.publish(self.semi_button_data)
        else:
            self.text_seq.insert("end", "alert\n")

    def up_key_pressed(self, event):
##        if self.video_mode_flag == True:
        print("up")
        self.cmd_vel_msg.linear.x = self.speed
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

##    def up_key_released(self, event):
##        if self.video_mode_flag ==  True:
##            print("up release")
##            self.cmd_vel_msg.linear.x = 0.0
##            self.cmd_vel_pub.publish(self.cmd_vel_msg)

    def down_key_pressed(self, event):
##        if self.video_mode_flag ==  True:
        print("down")
        self.cmd_vel_msg.linear.x = -1.0 * self.speed
        self.cmd_vel_msg.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

##    def down_key_released(self, event):
##        if self.video_mode_flag ==  True:
##            print("down release")
##            self.cmd_vel_msg.linear.x = 0.0
##            self.cmd_vel_pub.publish(self.cmd_vel_msg)

    def left_key_pressed(self, event):
##        if self.video_mode_flag ==  True:
        self.cmd_vel_msg.angular.z = self.rot
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

##    def left_key_released(self, event):
##        if self.video_mode_flag ==  True:
##            self.cmd_vel_msg.angular.z = 0.0
##            self.cmd_vel_pub.publish(self.cmd_vel_msg)

    def right_key_pressed(self, event):
##        if self.video_mode_flag ==  True:
        self.cmd_vel_msg.angular.z = -1.0 * self.rot
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel_msg)

##    def right_key_released(self, event):
##        if self.video_mode_flag ==  True:
##            self.cmd_vel_msg.angular.z = 0.0
##            self.cmd_vel_pub.publish(self.cmd_vel_msg)


    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Resize image to fit the GUI
            cv_image = cv2.resize(cv_image, (640, 480))

            # Convert the image to PhotoImage format
            image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
            image = ImageTk.PhotoImage(image)

            # Update the label with the new image
            self.v_label.configure(image=image)
            self.v_label.image = image

            # Display video on the Canvas widget at 0,0
            self.video_canvas.create_image(0, 0, anchor=tk.NW, image=image)
            ###############################################################

        except Exception as e:
            rospy.logerr(f"Error processing image: {str(e)}")

##    def front_cam_callback(self, msg):
##        try:
##            # Convert ROS Image message to OpenCV format
##            np_arr = np.frombuffer(msg.data, np.uint8)
##            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
####            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
##
##            # Resize image to fit the GUI
##            cv_image = cv2.resize(cv_image, (345, 240))
##
##            # Convert the image to PhotoImage format
##            image = PILImage.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
##            image = ImageTk.PhotoImage(image)
##
##            # Update the label with the new image
##            self.v_label.configure(image=image)
##            self.v_label.image = image
##
##            # Display video on the Canvas widget at 0,0
##            self.f_video_canvas.create_image(0, 0, anchor=tk.NW, image=image)
##            ###############################################################
##
##        except Exception as e:
##            rospy.logerr(f"Error processing image: {str(e)}")

    def video_mode_button_callback(self):
        print("Button clicked!")
        # when false its auto
        if self.video_mode_flag == True:
            self.video_mode_button.configure(text = "Video Manual!")
            self.video_mode.data = 1
            self.video_mode_pub.publish(self.video_mode)
            self.video_mode_flag = False

            self.semi_mode_wave.configure(state=tk.NORMAL)
            self.semi_mode_point.configure(state=tk.NORMAL)
            self.semi_mode_alert.configure(state=tk.NORMAL)
            self.semi_mode_forward.configure(state=tk.NORMAL)
            self.semi_mode_reverse.configure(state=tk.NORMAL)
            self.semi_mode_left.configure(state=tk.NORMAL)
            self.semi_mode_right.configure(state=tk.NORMAL)
            
        else:
            self.video_mode_button.configure(text = "Video SemiAuto!")
            self.video_mode.data = 0
            self.video_mode_pub.publish(self.video_mode)
            self.video_mode_flag = True
            
            self.semi_mode_wave.configure(state=tk.DISABLED)
            self.semi_mode_point.configure(state=tk.DISABLED)
            self.semi_mode_alert.configure(state=tk.DISABLED)
            self.semi_mode_forward.configure(state=tk.DISABLED)
            self.semi_mode_reverse.configure(state=tk.DISABLED)
            self.semi_mode_left.configure(state=tk.DISABLED)
            self.semi_mode_right.configure(state=tk.DISABLED)

    def mouse_motion_callback(self, event):
        x, y = event.x, event.y
        #print(f"Mouse position: x={x}, y={y}")

def main():
    rospy.init_node('ros_gui_node')#, anonymous=True)
    
    root = tk.Tk()
    gui = ROSGUI(root, 998, 650, "/home/akash/catkin_ws/src/quori_gui/src/GUI.jpg")

    # Run the Tkinter event loop
    root.mainloop()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
