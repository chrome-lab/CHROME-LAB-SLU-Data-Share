#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from quori_interactions.msg import ArmsCmd
from sensor_msgs.msg import JointState

class QuoriTeleop:
    def __init__(self):
        rospy.init_node('quori_arm_movement', anonymous=True)

        self.joint_names = [
            "r_shoulder_pitch",
            "r_shoulder_roll",
            "l_shoulder_pitch",
            "l_shoulder_roll",
            "waist_pitch"
        ]

        self.joint_traj_pub = rospy.Publisher('/quori/joint_trajectory_controller/command', JointTrajectory, queue_size=1)
        self.joint_states_sub = rospy.Subscriber('/joint_states', JointState, self.on_joint_states)
        self.arms_pos = ArmsCmd()
        self.arms_pos.r_shoulder_pitch = 0.0
        self.arms_pos.r_shoulder_roll = -1.0
        self.arms_pos.l_shoulder_pitch = 0.0
        self.arms_pos.l_shoulder_roll = -1.0
        self.arms_pos.waist_pitch = 0.0

        rospy.Subscriber = rospy.Subscriber('/arms_cmd', ArmsCmd, self.arm_cmd_callback)
        
        
        self.rate = rospy.Rate(25.0)

    def arm_cmd_callback(self, msg):
        self.arms_pos = msg
        #print(self.arm_pos)

    def on_joint_states(self, msg):
        # Update joint positions from joint_states message
        self.joint_positions = dict(zip(msg.name, msg.position))

    def publish_static_position(self):
        # Create JointTrajectory message
        joint_traj_msg = JointTrajectory()
        joint_traj_msg.joint_names = self.joint_names

        # Set static joint positions
        #static_positions = [0.0] * len(self.joint_names)
        #static_positions = [0.0, -1.0, 0.0, -1.0, 0.0]
        static_positions = [ self.arms_pos.r_shoulder_pitch,
                             self.arms_pos.r_shoulder_roll,
                             self.arms_pos.l_shoulder_pitch,
                             self.arms_pos.l_shoulder_roll,
                             self.arms_pos.waist_pitch ]
        #print(self.arm_pos)

        # Create JointTrajectoryPoint
        point = JointTrajectoryPoint()
        point.positions = static_positions
        point.time_from_start = rospy.Duration(0.5)

        # Add the point to the trajectory
        joint_traj_msg.points.append(point)

        # Publish the trajectory
        self.joint_traj_pub.publish(joint_traj_msg)

    def run(self):
        while not rospy.is_shutdown():
            self.publish_static_position()
            self.rate.sleep()

if __name__ == '__main__':
    quori_teleop = QuoriTeleop()
    quori_teleop.run()
