#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def publish_cmd_vel():
    rospy.init_node('cmd_vel_publisher', anonymous=True)
    cmd_vel_pub = rospy.Publisher('/quori/base_controller/cmd_vel', Twist, queue_size=10)
    cmd_vel_msg = Twist()
    cmd_vel_msg.linear.x = 0.1
    cmd_vel_msg.angular.z = 0.0
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        cmd_vel_pub.publish(cmd_vel_msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        publish_cmd_vel()
    except rospy.ROSInterruptException:
        pass
