#!/usr/bin/env python  
# Kota Kondo

#  Commands: Open three terminals and execute this:
#  python missed_msgs_count.py

import bagpy
from bagpy import bagreader
import pandas as pd

import rosbag
import rospy
import math
import tf2_ros
import geometry_msgs.msg
import tf
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

if __name__ == '__main__':

    # rosbag name

    is_oldmader = True # change here

    # number of agents
    num_of_agents = 10 
    
    if is_oldmader:
        cd_list = [0, 50, 100, 200, 300]
    else:
        cd_list = [50, 100, 100, 200, 300]

    for cd in cd_list:

        is_oldmader=True

        if cd == 0:
            dc_list = [0, 100, 20, 8, 1] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 50:
            dc_list = [0, 120, 56, 51, 50.8, 35, 15] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
            # dc_list = [0, 120] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 100:
            dc_list = [0, 190, 105, 101.3, 101, 75, 25] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
            # dc_list = [0, 170] #dc_list[0] will be used for old mader (which doesn't need delay check) so enter some value (default 0)
        elif cd == 200:
            dc_list = [0, 300]
        elif cd == 300:
            dc_list = [0, 400]

        for dc in dc_list:

            dc_in_ms = dc/1000;
            cd_in_ms = cd/1000;

            if dc == 50.8:
                str_dc = "51_8"
            elif dc == 101.3:
                str_dc = "101_3"
            else:
                str_dc = str(dc)

            dist_matrix_dc = np.zeros([num_of_agents, num_of_agents])

            if is_oldmader:
                source_dir = "/home/kota/data/csv/oldmader/cd"+str(cd)+"ms" # change the source dir accordingly #10 agents
            else:
                source_dir = "/home/kota/data/csv/rmader/cd"+str(cd)+"ms/dc"+str_dc+"ms" # change the source dir accordingly #10 agents
            
            source_len = len(source_dir)
            source_csvs = source_dir + "/*.csv" # change the source dir accordingly

            csv_list = glob.glob(source_csvs)
            csv_list.sort() #alphabetically order
            csv = []

            for csv_each in csv_list:
                csv.append(csv_each)

            # print(csv)

            num_of_sims = len(csv)
            print(num_of_sims)

            # going through the csvs (sims)
            for i in range(len(csv)):
                dist_matrix = pd.read_csv(csv[i])
                dist_matrix = dist_matrix.to_numpy()
                dist_matrix = dist_matrix[:,1:]

                # print(dist_matrix)

                # going through the agents
                dist_matrix_dc = np.add(dist_matrix_dc, dist_matrix)

            # averageing over num of sim
            num_of_sims_matrix = num_of_sims * np.ones((num_of_agents,num_of_agents))
            # print(num_of_sims_matrix)
            dist_matrix_dc = dist_matrix_dc / num_of_sims_matrix
            # print(dist_matrix_dc)

            # create symmetric matrix
            for i in range(num_of_agents):
                for j in range(i+1, num_of_agents):
                    dist_matrix_dc[j,i] = dist_matrix_dc[i,j]

            # print(dist_matrix_dc)

            sum_of_rows = dist_matrix_dc.sum(axis=1)
            # print(sum_of_rows)
            ave_per_dc = sum_of_rows / ((num_of_agents-1)*np.ones(num_of_agents)) #num_of_agents-1 is becasue you don't calcuate the distance from itself to itself 
            # print(ave_per_dc)

            os.system('echo "'+source_dir+'" >> /home/kota/data/ave_distance.txt')
            for i in range(num_of_agents):
                if i<=9:
                    sim_id = "0"+str(i)
                else:
                    sim_id = str(i)
                # os.system('echo "SQ'+sim_id+' '+str(ave_per_dc[i])+'" >> /home/kota/data/ave_distance.txt')

            total_ave_dist = sum(ave_per_dc)/len(ave_per_dc)
            os.system('echo "total distance '+str(round(total_ave_dist,2))+'m" >> /home/kota/data/ave_distance.txt')
            os.system('echo "------------------------------------------------------------" >> /home/kota/data/ave_distance.txt')

            is_oldmader = False