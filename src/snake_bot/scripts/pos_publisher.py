#!/usr/bin/env python

import rospy
from std_msgs.msg import String, Float32MultiArray
from std_msgs.msg import Int64, Int16,Int16MultiArray,MultiArrayLayout,MultiArrayDimension
import numpy as np
import pickle
import sys, select, termios, tty
from threading import Thread

#from pos_publisher_functions import initialize, encoder_sub_cb, control,pos_publish, getKey

pre_rec_poses=[]
pos_cmd_pub = rospy.Publisher('pos_cmd', Float32MultiArray, queue_size=10)
move_pub=rospy.Publisher('move_cmd', Int16, queue_size=10)


settings = termios.tcgetattr(sys.stdin)
global base_loc
global base_locs
base_loc=-915
global speed
speed=150
#pre recorded base loacations

def initialize():
    global pre_rec_poses
    global base_locs
    rospy.init_node('pos_publisher', anonymous=True)

    with open('/home/mohamadi/snake_bot_files/pre_rec_poses.pkl', 'rb') as infile:
        pre_rec_poses =pickle.load(infile)
        pre_rec_poses =pre_rec_poses[0]
        base_locs=np.zeros(len(pre_rec_poses))

    for i in range(len(pre_rec_poses)):
        base_locs[i]=pre_rec_poses[i][0]

    rospy.loginfo("length %i lkdjf" % len(pre_rec_poses))
    rospy.loginfo(pre_rec_poses[0][0])
    rospy.loginfo(pre_rec_poses[0][1])
    rospy.loginfo(pre_rec_poses[0][1][5])

def encoder_sub_cb(data):
    global base_loc
    tmp=data.data*1.1875-915
    base_loc=np.clip(tmp,np.min(base_locs), np.max(base_locs))

def control():
    global base_loc
    global speed
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        hello_str = "\n Time: %s \n Base Location: %.2f mm \n \
        Move Speed: %i \n" % (rospy.get_time(), base_loc, speed)
        rospy.loginfo(hello_str)
        key=getKey()

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

def pos_publish():
    global base_locs
    global base_loc
    rate = rospy.Rate(5)
    pos_cmd=Float32MultiArray()
    while not rospy.is_shutdown():
        int_base_loc=np.rint(base_loc)
        k,=np.where(base_locs==int_base_loc)
        pos_cmd.data=np.rad2deg(pre_rec_poses[k[0]][1])
        pos_cmd_pub.publish(pos_cmd)
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
    Thread(target=pos_publish).start()
    try:
        control()
    except rospy.ROSInterruptException:
        pass
