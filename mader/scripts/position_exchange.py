#!/usr/bin/env python

import math
import os
import time
import rospy
import rosgraph
from geometry_msgs.msg import PoseStamped
from snapstack_msgs.msg import State
import numpy as np
from random import * 

class TermGoalSender:

    def __init__(self):

        # mode
        self.mode = rospy.get_param('mode', 0) #default value is 0

        # home yet?
        self.is_home = False

        # position change
        self.sign = 1

        # initialization done?
        self.is_init_pos = False

        # term_goal init
        self.term_goal=PoseStamped()
        self.term_goal.header.frame_id='world'
        self.pubTermGoal = rospy.Publisher('term_goal', PoseStamped, queue_size=1, latch=True)
        
        # state_pos init ()
        self.state_pos=np.array([0.0, 0.0, 0.0])

        # waypoints
        self.wpidx = 0
        self.wps = np.array([
                            [-3.0, 3.0, 1.5],
                            [3.0, -3.0, 1.9],
                            [-3.0, -3.0, 2.2],
                            [3.0, 3.0, 1.6],
                            ])

        # every 10 sec change goals
        rospy.Timer(rospy.Duration(10.0), self.change_goal)

        # every 0.01 sec timerCB is called back
        self.is_change_goal = True
        self.timer = rospy.Timer(rospy.Duration(0.01), self.timerCB)

        # send goal
        self.sendGoal()

        # set initial time and how long the demo is
        self.time_init = rospy.get_rostime()
        self.total_secs = 60.0; # sec

    def change_goal(self, tmp):
        self.is_change_goal = True
        

    def timerCB(self, tmp):
        
        # term_goal in array form
        self.term_goal_pos=np.array([self.term_goal.pose.position.x,self.term_goal.pose.position.y,self.term_goal.pose.position.z])

        # distance
        dist=np.linalg.norm(self.term_goal_pos-self.state_pos)
        #print("dist=", dist)

        # check distance and if it's close enough publish new term_goal
        dist_limit = 0.3
        if (dist < dist_limit):
            if not self.is_home:
                self.sendGoal()

        # every 10 seconds change the goal (to avoid stuck issue)
        if (self.is_change_goal):
            if not self.is_home:
                self.is_change_goal = False
                print("changed goal every 10 sec")
                self.sendGoal()

        # check if we should go home
        duration = rospy.get_rostime() - self.time_init
        if (duration.to_sec() > self.total_secs):
            self.is_home = True
            self.sendGoalHome()

    def sendGoal(self):

        # # set random goals (exact position exchange, this could lead to drones going to exact same locations)
        # if self.mode == 6:
        #     self.term_goal.pose.position.x = self.sign * -3
        #     self.term_goal.pose.position.y = self.sign * 3
        # elif self.mode == 5:
        #     self.term_goal.pose.position.x = self.sign * 0
        #     self.term_goal.pose.position.y = self.sign * 3
        # elif self.mode == 4:
        #     self.term_goal.pose.position.x = self.sign * 3
        #     self.term_goal.pose.position.y = self.sign * 3
        # elif self.mode == 3:
        #     self.term_goal.pose.position.x = self.sign * -3
        #     self.term_goal.pose.position.y = self.sign * -3
        # elif self.mode == 2:
        #     self.term_goal.pose.position.x = self.sign * 0
        #     self.term_goal.pose.position.y = self.sign * -3
        # elif self.mode == 1:
        #     self.term_goal.pose.position.x = self.sign * 3
        #     self.term_goal.pose.position.y = self.sign * -3
        # elif self.mode == 7: 
        #     self.term_goal.pose.position.x = self.wps[self.wpidx,0]
        #     self.term_goal.pose.position.y = self.wps[self.wpidx,1]
        #     self.term_goal.pose.position.z = self.wps[self.wpidx,2]
        #     self.wpidx = (self.wpidx + 1) % len(self.wps)

        # set random goals ()
        if self.mode == 6:
            self.term_goal.pose.position.x = self.sign * -3
            self.term_goal.pose.position.y = self.sign * 2
        elif self.mode == 5:
            self.term_goal.pose.position.x = self.sign * -1
            self.term_goal.pose.position.y = self.sign * 3
        elif self.mode == 4:
            self.term_goal.pose.position.x = self.sign * 3
            self.term_goal.pose.position.y = self.sign * 2
        elif self.mode == 3:
            self.term_goal.pose.position.x = self.sign * -2
            self.term_goal.pose.position.y = self.sign * -3
        elif self.mode == 2:
            self.term_goal.pose.position.x = self.sign * -1
            self.term_goal.pose.position.y = self.sign * -3
        elif self.mode == 1:
            self.term_goal.pose.position.x = self.sign * 2
            self.term_goal.pose.position.y = self.sign * -3
        elif self.mode == 7: 
            self.term_goal.pose.position.x = self.wps[self.wpidx,0]
            self.term_goal.pose.position.y = self.wps[self.wpidx,1]
            self.term_goal.pose.position.z = self.wps[self.wpidx,2]
            self.wpidx = (self.wpidx + 1) % len(self.wps)

        self.term_goal.pose.position.z = 1.5 + 1.0 * random()
        self.sign = self.sign * (-1)

        self.pubTermGoal.publish(self.term_goal)      

        return

    def sendGoalHome(self):

        # set home goals
        self.term_goal.pose.position.x = self.init_pos[0]
        self.term_goal.pose.position.y = self.init_pos[1]
        self.term_goal.pose.position.z = 1.8

        self.pubTermGoal.publish(self.term_goal)  

        print ("Home Return")
        print("term_goal x = ", self.term_goal.pose.position.x)      
        print("term_goal y = ", self.term_goal.pose.position.y)      
        print("term_goal z = ", self.term_goal.pose.position.z)      

        return

    def stateCB(self, data):
        if not self.is_init_pos:
            self.init_pos = np.array([data.pos.x, data.pos.y, data.pos.z])
            self.is_init_pos = True

        self.state_pos = np.array([data.pos.x, data.pos.y, data.pos.z])

def startNode():
    c = TermGoalSender()
    rospy.Subscriber("state", State, c.stateCB)
    rospy.spin()

if __name__ == '__main__':
    rospy.init_node('TermGoalSender')
    startNode()
