#! /usr/bin/env python
import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import params 


def Get_Drones(uris, base, full_magazine, drone_num):
    drones = []
    for i in range(drone_num):
        drones.append(Drone(index=i, uri=uris[i], base=base[i], full_magazine=full_magazine[i]))
        drones[i].is_active = True
    return drones


class Drone(object):
    def __init__(self, index, uri, base, full_magazine):
        self.ind = index
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
        self.is_available = 0
        self.is_reached_goal = 0
        self.path_found = 0
        self.at_base = 0
        self.is_active = True
        
                
class get_figure(object):
    def __init__(self):
        self.targetpos = params.targetpos
        self.inital_drone_num = params.drone_num
        self.colors = params.colors
        # self.fig = plt.figure()
        # self.ax = Axes3D(self.fig)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max = params.limits
        # self.ax.axes.set_xlim(self.x_min, self.x_max) 
        # self.ax.axes.set_ylim(self.y_min, self.y_max) 
        # self.ax.axes.set_zlim(self.z_min, self.z_max)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        # self.ax.view_init(elev=0, azim=90)
        elev, azim = params.elvazim
        self.ax.view_init(elev=elev, azim=azim)
        self.path_scatter = params.plot_path_scatter
        self.smooth_path_cont = params.plot_smooth_path_cont 
        self.smooth_path_scatter = params.plot_smooth_path_scatter
        self.block_volume = params.plot_block_volume
        self.constant_blocking_area = params.plot_constant_blocking_area
    
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
                if self.constant_blocking_area:
                    self.ax.scatter3D(path_planner.constant_blocking_area_m[j][:,0], path_planner.constant_blocking_area_m[j][:,1], path_planner.constant_blocking_area_m[j][:,2], s= 10, c='m',alpha=0.01,depthshade=False)

    def show(self):
        # self.ax.axes.set_xlim(self.x_min, self.x_max) 
        # self.ax.axes.set_ylim(self.y_min, self.y_max) 
        # self.ax.axes.set_zlim(self.z_min, self.z_max)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('z')
        self.ax.set_xlim3d([self.x_min, self.x_max])
        self.ax.set_ylim3d([self.y_min, self.y_max])
        self.ax.set_zlim3d([self.z_min, self.z_max])
        self.fig.canvas.flush_events()

    def plot_no_path_found(self, drone):
        no_path = np.stack([np.array(drone.start_coords), np.array(drone.goal_coords)], axis=0)
        self.ax.plot(no_path[:,0], no_path[:,1], no_path[:,2], c='m', linewidth=6)

    def plot_history(self, history):
        for j in range(self.inital_drone_num):
            if len(history[j]) > 0:
                self.ax.scatter3D(history[j][:,0], history[j][:,1], history[j][:,2], s =50, c=self.colors[j], alpha=1,depthshade=False)
            
       
# ----------- addtional functions for params --
def grid_shape():
    n = 20
    z_col = np.linspace(1,2.2,4)
    y_row = np.linspace(-3,3,5)
    x = 3.5
    targets = []
    for z in z_col:
        for y in y_row:
            targets.append([x,y,z])
    return np.array(targets)   

def get_span(targetpos, base):
    z_min, z_max = 0, max( max(targetpos[:,2]), max(np.array(base)[:,2]))
    z_span = (z_max - z_min) * 1.3
    y_min, y_max =  min(min(targetpos[:,1]) , min(np.array(base)[:,1]))  , max(max(targetpos[:,1]), max(np.array(base)[:,1]))
    y_span = (y_max - y_min) * 1.3
    x_min, x_max = min(0 , min(np.array(base)[:,0])), max(max(targetpos[:,0]), max(np.array(base)[:,0])) 
    x_span = (x_max - x_min) * 1.3  
    return [x_span, y_span, z_span], [x_min, x_max, y_min, y_max, z_min, z_max]       




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


    