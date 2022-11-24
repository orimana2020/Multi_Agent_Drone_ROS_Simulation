#! /usr/bin/env python
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import params 

class Env(object):
    def __init__(self, drone_performace, drone_num):
        self.drone_num = drone_num
        self.drone_peformace = np.zeros([self.drone_num, 100])
        for i in range(self.drone_num):
            self.drone_peformace[i,0:drone_performace[i]] = 1
    def reached_goal(self, drone_idx, goal=None): 
        if self.drone_peformace[drone_idx, random.randint(0,99)] == 1:
            return 1
        return 0


def Get_Drones(uris, base, full_magazine, drone_num):
    drones = []
    for i in range(drone_num):
        drones.append(Drone(uri=uris[i], base=base[i], full_magazine=full_magazine[i]))
    return drones


class Drone(object):
    def __init__(self, uri, base, full_magazine):
        self.uri = uri
        self.base = base
        self.start_coords = base
        self.goal_coords = None
        self.full_magazine = full_magazine
        self.current_magazine = full_magazine
        self.start_title = 'base'
        self.goal_title = 'target'
        self.current_pos_title = 'base'
        self.current_pos_coords = base
        self.is_available = 1
        self.is_reached_goal = 0
        self.path_found = 0
        self.at_base = 0
        
                
class get_figure(object):
    def __init__(self):
        self.targetpos = params.targetpos
        self.inital_drone_num = params.drone_num
        self.colors = params.colors
        self.fig = plt.figure(1)
        self.ax =  Axes3D(self.fig)
        self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max = params.limits
        self.ax.axes.set_xlim(self.x_min, self.x_max) 
        self.ax.axes.set_ylim(self.y_min, self.y_max) 
        self.ax.axes.set_zlim(self.z_min, self.z_max)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        # self.ax.view_init(elev=0, azim=90)
        elev, azim = params.elvazim
        self.ax.view_init(elev=elev, azim=azim)
        self.path_scatter = params.path_scatter
        self.smooth_path_cont = params.smooth_path_cont 
        self.smooth_path_scatter = params.smooth_path_scatter
        self.block_volume = params.block_volume
    
    def plot_all_targets(self):
        self.ax.scatter3D(self.targetpos[:,0], self.targetpos[:,1], self.targetpos[:,2], s= 10, c='k',alpha=1, depthshade=False)
    
    def plot_current_targets(self, current_idx, drone_num):
        for j in range(drone_num):
            self.ax.scatter3D(self.targetpos[current_idx[j], 0], self.targetpos[current_idx[j], 1], self.targetpos[current_idx[j], 2], s =50, c=self.colors[j], alpha=1,depthshade=False)

    def plot_trajectory(self, path_planner, drones ,drone_num):
        for j in range(drone_num):
            if drones[j].path_found:
                if self.path_scatter:
                    self.ax.scatter3D(path_planner.paths_m[j][:,0], path_planner.paths_m[j][:,1], path_planner.paths_m[j][:,2], s= 15, c='r',alpha=1, depthshade=False)
                if self.smooth_path_cont:  
                    if drones[j].goal_title =='base':
                        color = 'r' 
                    else:
                        color = 'b'
                    self.ax.plot(path_planner.smooth_path_m[j][:,0],path_planner.smooth_path_m[j][:,1],path_planner.smooth_path_m[j][:,2], c=color, linewidth=4)
                if self.smooth_path_scatter:
                    self.ax.scatter3D(path_planner.smooth_path_m[j][:,0],path_planner.smooth_path_m[j][:,1],path_planner.smooth_path_m[j][:,2],s= 25, c='g',alpha=1, depthshade=False)
                if self.block_volume:
                    self.ax.scatter3D(path_planner.block_volumes_m[j][:,0], path_planner.block_volumes_m[j][:,1], path_planner.block_volumes_m[j][:,2], s= 10, c='g',alpha=0.01,depthshade=False)

    def show(self):
        self.ax.axes.set_xlim(self.x_min, self.x_max) 
        self.ax.axes.set_ylim(self.y_min, self.y_max) 
        self.ax.axes.set_zlim(self.z_min, self.z_max)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        self.fig.canvas.flush_events()

    def plot_no_path_found(self, drone):
        coord = np.stack([np.array(drone.start_coords), np.array(drone.goal_coords)], axis=0)
        self.ax.plot(coord[:,0],coord[:,1],coord[:,2], c='m', linewidth=6)

    def plot_history(self, history):
        for j in range(self.inital_drone_num):
            if len(history[j]) > 0:
                self.ax.scatter3D(history[j][:,0], history[j][:,1], history[j][:,2], s =50, c=self.colors[j], alpha=1,depthshade=False)
            
        
        

 







    