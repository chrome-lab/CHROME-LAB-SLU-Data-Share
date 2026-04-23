#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Image, CompressedImage, Joy
#import pyautogui
from cv_bridge import CvBridge
import cv2
import tkinter as tk
from PIL import Image as PILImage, ImageTk
from std_msgs.msg import Int64, String, Int32
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
    def __init__(self, root, width, height, background_image=None):
        self.root = root
        self.root.title("ROS GUI")
        self.root.geometry(f"{width}x{height}")
        bg = "#282828"


        # Publishers
        self.video_mode_pub = rospy.Publisher("/video_mode", Int64, queue_size = 1)
        self.video_mode = Int64()
        self.video_mode.data = 0
        self.video_mode_pub.publish(self.video_mode)

        self.mic_enable_pub = rospy.Publisher("/speech_recognition/mic_enable", Int32, queue_size=1);

        self.semi_button_pub = rospy.Publisher("/op_cmd_gui", Opcmd, queue_size = -1)
        self.semi_button_data = Opcmd()

        self.key_joy_pub = rospy.Publisher("/virtual_joy", Int64, queue_size=1)

        rospy.Subscriber("/response_to_action", String, self.response_callback)
        #rospy.Subscriber("/joy", Joy, self.joy_callback)
        rospy.Subscriber("speech_recognition/final_result", String, self.notify_speech_cb)
        rospy.Subscriber("/quori/intent", String, self.get_intent_cb)
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
        #bg_image = PILImage.open(background_image)
        #bg_image = ImageTk.PhotoImage(bg_image)
        #self.background_label = tk.Label(root, image=bg_image)
        #self.background_label.image = bg_image
        #self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.configure(bg=bg)
        self.bg_frame = tk.Frame(root, bg=bg)
        self.bg_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_frame.lower() 

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
        self.z = DelayKey(1.0)
        
        root.bind('<KeyPress-2>', self.on_key_v) #point
        self.v = DelayKey(1.0)
        
        root.bind('<KeyPress-6>', self.on_key_c) #alert
        self.c = DelayKey(1.0)
        
        root.bind('<KeyPress-1>', self.on_key_x) #fist bump
        self.x = DelayKey(1.0)
        
        root.bind('<KeyPress-5>', self.on_key_b) #high five
        self.b = DelayKey(1.0)
        
        root.bind('<KeyPress-4>', self.on_key_n) #hug
        self.n = DelayKey(1.0)

        root.bind('<space>', self.toggle_mic_color)
        self.mic_size = (32, 32)
        self.mic_colors = ["red", "green"]
        self.mic_index = 0
        mic_files = {
            "red": "mic red.png",
            #"yellow": "mic yellow.png",
            "green": "mic green.png",
        }

        

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
        #self.next.place(x=831, y=486)
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
        self.notification_label = tk.Label(root, text="--- Notification", font=("Helvetica", 14, "bold"), bg="#282828", fg="white")
        self.notification_label.place(x=550, y=517)

        self.foldername = "/home/akash/catkin_ws/src/quori_gui/src/"
        self.filenames = ["keyboard.png","cv.png", "joystick.png", "vision.png"]
        self.ind = -1
        self.help_canvas = tk.Canvas(root, width=341, height=480, bg="#0E2429")
        self.help_canvas.place(x=649, y=0)
        self.help_label = tk.Label(root)
        
        
        self.help_but= tk.Button(root, text="Instructions >>", command=self.help_update)
        self.help_but.place(x=862, y=486)

        self.notification = tk.Text(root, width=82, height=6, fg="white", bg="black")
        self.notification.place(x = 16, y = 539)

        self.notification_button = tk.Button(root, text="Clear",width = 6, height = 5,fg="red", \
                                             font=("Arial", 12, "bold"), command=self.clearNotification)
        self.notification_button.place(x = 683, y = 539)

        scrollbar = tk.Scrollbar(root, command=self.notification.yview)
        scrollbar.place(x=665, y=539, height=107)  # Adjust x and y according to your layout

        # Attach the scrollbar to the Text widget
        self.notification.config(yscrollcommand=scrollbar.set)

        #mic image
        self.mic_images = {}
        for color, fname in mic_files.items():
            img = PILImage.open(os.path.join(self.foldername, fname))
            img = img.resize(self.mic_size, PILImage.LANCZOS)
            self.mic_images[color] = ImageTk.PhotoImage(img)

        self.mic_label = tk.Label(root, bd=0, highlightthickness=0, borderwidth=0)
        self.mic_label.place(x=275, y=500)

        self.update_mic_image()

        

        mvmt_sub = rospy.Subscriber("/op_cmd", String, self.mvmt_Callback)
        mvmt_sub1 = rospy.Subscriber("/op_cmd_gui", Opcmd, self.mvmt_gui_Callback)
        
        self.video_mode_button_callback()
        self.help_update()

        mic = Int32()
        mic.data = 0
        self.mic_enable_pub.publish(mic)


        self.scripts = {
            "Script 1": [
                "PRACTICE SCRIPT", 
                "HIGH FIVE \n\n-------------------------------------------\n Say High five.",
                "SCRIPT 1",
                "WAVE \n\n-------------------------------------------\n Reply with a greeting and introduce yourself.",
                "Reply with your major.",
                "HIGH FIVE \n\n-------------------------------------------\n Say High Five.",
                "Answer Samantha's question.",
                "ALERT \n\n-------------------------------------------\n Get Samantha's attention and offer to help locate her belongings.",
                "POINT \n\n-------------------------------------------\n Indicate the location of the item.",
                "FIST BUMP \n\n-------------------------------------------\n Conclude the interaction with a farewell message.",
                "COMPLETE QUESTIONAIRES"
            ],
            "Script 2": [
                "PRACTICE SCRIPT",
                "HIGH FIVE \n\n-------------------------------------------\n Say High five.",
                "SCRIPT 2",
                "WAVE \n\n-------------------------------------------\n Reply with a greeting and introduce yourself.",
                "Reply with your favourite class.",
                "HIGH FIVE \n\n-------------------------------------------\n Say High Five.",
                "Answer Samantha's question.",
                "ALERT \n\n-------------------------------------------\n Get Samantha's attention and offer to help locate her belongings.",
                "POINT \n\n-------------------------------------------\n Indicate the location of the item.",
                "FIST BUMP \n\n-------------------------------------------\n Conclude the interaction with a farewell message.",
                "COMPLETE QUESTIONAIRES"
            ],
        }

        self._init_script_navigator(x=1005, y=10, w=265, h=630)


    def _init_script_navigator(self, x: int, y: int, w: int, h: int):
        bg = "#282828"
        card_bg = "#1f1f1f"
        card_border = "#3a3a3a"
        txt_color = "#f2f2f2"
        sub_color = "#bdbdbd"
        cmd_green = "#39d353"  # nice readable green

        self._nav_frame = tk.Frame(self.root, bg=bg)
        self._nav_frame.place(x=x, y=y, width=w, height=h)

        title = tk.Label(self._nav_frame, text="Interactions Guide",
                        font=("Helvetica", 14, "bold"), bg=bg, fg=txt_color)
        title.place(x=10, y=10)

        # Script selector
        self._script_var = tk.StringVar(value="Script 1")
        r1 = tk.Radiobutton(
            self._nav_frame, text="1",
            variable=self._script_var, value="Script 1",
            command=self._on_script_change,
            bg=bg, fg=txt_color, selectcolor=bg,
            activebackground=bg, activeforeground=txt_color
        )
        r2 = tk.Radiobutton(
            self._nav_frame, text="2",
            variable=self._script_var, value="Script 2",
            command=self._on_script_change,
            bg=bg, fg=txt_color, selectcolor=bg,
            activebackground=bg, activeforeground=txt_color
        )
        r1.place(x=10, y=45)
        r2.place(x=110, y=45)

        # Card container (frame with border vibe)
        card = tk.Frame(self._nav_frame, bg=card_border)
        card.place(x=10, y=80, width=w-20, height=h-170)

        inner = tk.Frame(card, bg=card_bg)
        inner.place(x=2, y=2, width=(w-20)-4, height=(h-170)-4)

        # Read-only styled text widget (this enables per-word coloring/bold/underline)
        self._script_text = tk.Text(
            inner,
            bg=card_bg, fg=txt_color,
            relief="flat",
            wrap="word",
            borderwidth=0,
            highlightthickness=0,
            padx=12, pady=12,
            font=("Helvetica", 12)
        )
        self._script_text.place(x=0, y=0, relwidth=1, relheight=1)

        # Define tags (styles)
        self._script_text.tag_configure("title", font=("Helvetica", 13, "bold"), underline=1)
        self._script_text.tag_configure("cmd", font=("Helvetica", 12, "bold"), foreground=cmd_green)
        self._script_text.tag_configure("body", font=("Helvetica", 12), foreground=txt_color)

        self._script_text.config(state="disabled")

        self._step_label = tk.Label(self._nav_frame, text="", font=("Helvetica", 10),
                                    bg=bg, fg=sub_color)
        self._step_label.place(x=10, y=h-80)

        # Prev / Next buttons
        self._prev_btn = tk.Button(self._nav_frame, text="◀ Prev", command=self._prev_step,
                                bg="#202020", fg=txt_color, relief="flat")
        self._next_btn = tk.Button(self._nav_frame, text="Next ▶", command=self._next_step,
                                bg="#202020", fg=txt_color, relief="flat")

        self._prev_btn.place(x=10, y=h-55, width=(w-30)//2, height=40)
        self._next_btn.place(x=20 + (w-30)//2, y=h-55, width=(w-30)//2, height=40)

        # Hover effect
        def hover(btn, on):
            btn.configure(bg="#2b2b2b" if on else "#202020")
        self._prev_btn.bind("<Enter>", lambda e: hover(self._prev_btn, True))
        self._prev_btn.bind("<Leave>", lambda e: hover(self._prev_btn, False))
        self._next_btn.bind("<Enter>", lambda e: hover(self._next_btn, True))
        self._next_btn.bind("<Leave>", lambda e: hover(self._next_btn, False))

        # Keyboard shortcuts
        self.root.bind("<Right>", lambda e: self._next_step())
        self.root.bind("<Left>",  lambda e: self._prev_step())

        # Index per script
        self._script_index = {"Script 1": 0, "Script 2": 0}

        # Show initial (NO animation)
        self._show_current()



    def _rounded_rect(self, canvas, x1, y1, x2, y2, r=18, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)


    def _on_script_change(self):
        # When switching scripts, show that script's current index
        self._show_current()


    def _next_step(self):
        name = self._script_var.get()
        steps = self.scripts.get(name, [])
        if not steps:
            return
        self._script_index[name] = (self._script_index[name] + 1) % len(steps)  # wrap-around
        self._show_current()


    def _prev_step(self):
        name = self._script_var.get()
        steps = self.scripts.get(name, [])
        if not steps:
            return
        self._script_index[name] = (self._script_index[name] - 1) % len(steps)  # wrap-around
        self._show_current()


    
    def _show_current(self):
        name = self._script_var.get()
        steps = self.scripts.get(name, [])
        if not steps:
            self._render_rich_text("(No text in this script)")
            self._step_label.config(text="")
            return

        idx = self._script_index[name]
        full_text = steps[idx]
        self._step_label.config(text=f"{idx+1}/{len(steps)}")

        self._render_rich_text(full_text)



    def _typewriter(self, text, pos=0):
        # speed (ms per char) — tweak as you like
        speed_ms = 12

        shown = text[:pos]
        self._card.itemconfig(self._text_id, text=shown)

        if pos >= len(text):
            self._tw_job = None
            return

        self._tw_job = self.root.after(speed_ms, lambda: self._typewriter(text, pos+1))

        
    def _render_rich_text(self, text: str):
        titles = {"PRACTICE SCRIPT", "SCRIPT 1", "SCRIPT 2", "COMPLETE QUESTIONAIRES"}
        commands = ["WAVE", "FIST BUMP", "HIGH FIVE", "POINT", "ALERT"]

        # Prepare header/body split (header = first line)
        lines = text.split("\n")
        header = lines[0].strip()
        body = "\n".join(lines[1:]).lstrip("\n")  # keep your spacing but avoid leading empty junk

        self._script_text.config(state="normal")
        self._script_text.delete("1.0", "end")

        # Insert header with style
        if header in titles:
            self._script_text.insert("end", header + "\n", ("title",))
        else:
            # If header starts with a command (HIGH FIVE, WAVE, etc), make it green
            matched_cmd = None
            for cmd in commands:
                if header.upper().startswith(cmd):
                    matched_cmd = cmd
                    break

            if matched_cmd is not None:
                # color only the header line (command)
                self._script_text.insert("end", header + "\n", ("cmd",))
            else:
                self._script_text.insert("end", header + "\n", ("body",))

        # Insert body (normal)
        if body.strip():
            self._script_text.insert("end", body, ("body",))

        self._script_text.config(state="disabled")

        
    def notify_speech_cb(self, data):
        self.notify("STT --> "+data.data)

    def mvmt_Callback(self, data):
        self.notify("Commanded "+data.data)

    def mvmt_gui_Callback(self, data):
        self.notify("Commanded "+data.data[:-1])
        

    def clearNotification(self):
        self.notification.config(state='normal')
        self.notification.delete("1.0", "end")
        self.notification.config(state='disabled')

    def notify(self, text):
        self.notification.config(state='normal')

        text = "[INFO] ["+ str(time.perf_counter()) + "]: "+ text + ".\n"
        self.notification.insert("end", text)

        self.notification.yview('end')
        self.notification.config(state='disabled')

        
        
    def help_update(self):
        self.ind = self.ind+1
        if self.ind > 3:
            self.ind = 0

        #print(self.foldername + self.filenames[self.ind])
        image = PILImage.open(self.foldername + self.filenames[self.ind])
        image = ImageTk.PhotoImage(image)
        self.help_label.configure(image=image)
        self.help_label.image = image
        self.help_canvas.create_image(0, 0, anchor=tk.NW, image=image)

        if self.ind == 0:
            self.notify("Showing Keyboard Controls on Right Side of the GUI")
        elif self.ind == 1:
            self.notify("Showing Computer Vision Gesture Controls on Right Side of the GUI")
        else:
            self.notify("Showing Joystick Controls on Right Side of the GUI")
        


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

    def update_mic_image(self):
        """Update the mic icon according to current color index."""
        color = self.mic_colors[self.mic_index]
        img = self.mic_images[color]
        self.mic_label.configure(image=img)
        self.mic_label.image = img  # keep reference so it isn't garbage-collected

    def toggle_mic_color(self, event=None):
        """Cycle mic color: red → yellow → green → red when Space is pressed."""
        self.mic_index = (self.mic_index + 1) % len(self.mic_colors)
        #print(self.mic_index)
        enable_mic = Int32()
        enable_mic.data = self.mic_index
        self.mic_enable_pub.publish(enable_mic)
        self.update_mic_image()
    
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
            self.fist_bump()
            

    def fist_bump(self):
        self.semi_button_data.data = 'fist_bumpb'
        self.semi_button_data.angle_dist = 0.0
        self.semi_button_pub.publish(self.semi_button_data)

    def on_key_b(self, event):
        if self.video_mode_flag == False and self.b.update():
            self.high_five()
            

    def high_five(self):
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

    def get_intent_cb(self, data):
        if data.data == "wave":
            self.semi_mode_wave_callback()

        elif data.data == "Alert":
            self.semi_mode_alert_callback()

        elif data.data == "point":
            self.semi_mode_point_callback()

        elif data.data == "highfive":
            self.high_five()

        elif data.data == "fist bump":
            self.fist_bump()
        

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
            self.notify("Video Mode Changed to Semi-Auto")
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
            self.notify("Video Mode Changed to Manual")
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
    gui = ROSGUI(root, 1280, 650)#, "/home/hassan/Downloads/catkin_ws/src/quori_gui/src/GUI.jpg")

    # Run the Tkinter event loop
    root.mainloop()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
