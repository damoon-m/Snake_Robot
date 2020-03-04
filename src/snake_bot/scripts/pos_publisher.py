#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Int64, Int16,Int16MultiArray,MultiArrayLayout,MultiArrayDimension
import numpy as np
import pickle
import sys, select, termios, tty

pre_rec_poses=[]
pub = rospy.Publisher('pos_cmd', Int16MultiArray, queue_size=10)
move_pub=rospy.Publisher('move_cmd', Int16, queue_size=10)


settings = termios.tcgetattr(sys.stdin)
global base_loc
base_loc=0
global speed
speed=150

def initialize():

    rospy.init_node('pos_publisher', anonymous=True)

    with open('/home/mohamadi/snake_bot_files/pre_rec_poses.pkl', 'rb') as infile:
        pre_rec_poses =pickle.load(infile)
        pre_rec_poses =pre_rec_poses[0]

    rospy.loginfo(pre_rec_poses[0][0])
    rospy.loginfo(pre_rec_poses[0][1])
    rospy.loginfo(pre_rec_poses[0][1][5])

def encoder_sub_cb(data):
    global base_loc
    base_loc=data.data*1.1875

def control():
    global base_loc
    global speed
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        hello_str = "Time: %s \n Base Location: %.2f mm \n \
        Move Speed: %i" % (rospy.get_time(), base_loc, speed)
        rospy.loginfo(hello_str)
        #r=Int16MultiArray(data=[ii, ii+10, ii+100, ii+1000, ii+10000, ii+20000])
        key=getKey()
        #pub.publish(r)

        if key=='w':
            move_pub.publish(+11)
        elif key=="s":
            move_pub.publish(-11)

        elif (key=="q"):
            speed=min(speed+10,500)
            move_pub.publish(speed)
        elif (key=="a") & (speed > 0):
            speed=speed-10
            move_pub.publish(speed)
        elif key=="\x03":
            rospy.signal_shutdown('Bye Bye')
        else:
            move_pub.publish(0)

        rate.sleep()

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


rospy.Subscriber('encoder_pos', Int64, encoder_sub_cb)

if __name__ == '__main__':
    initialize()
    try:
        control()
    except rospy.ROSInterruptException:
        pass
