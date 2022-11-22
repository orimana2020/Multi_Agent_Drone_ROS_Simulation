#! /usr/bin/env python

import numpy as np
from scipy import interpolate


class Trajectory(object):
    def __init__(self, x_span ,y_span ,z_span ,drone_num ,res , safety_distance):
        self.res = res
        self.break_trajecoty_len = 0.4
        self.minimum_floor_distance = 0.4 # meter
        z_span = z_span - self.minimum_floor_distance
        self.grid_3d = np.zeros([int(z_span/res), int(y_span/res), int(x_span/res)], dtype=int) #z y x
        self.grid_3d_shape = self.grid_3d.shape
        self.visited_3d = np.zeros([int(z_span/res), int(y_span/res), int(x_span/res)], dtype=int) #z y x
        z_lim, y_lim, x_lim = self.grid_3d.shape
        self.x_lim = x_lim -1
        self.y_lim = y_lim -1
        self.z_lim = z_lim -1 
        self.safety_distance = safety_distance
        self.block_volume = []
        self.block_volumes_m = [] # used for visualization only
        self.paths_m = [] # used for visualization only
        self.smooth_path_m =[]
        
        for _ in range(drone_num):
            self.block_volume.append([])
            self.block_volumes_m.append([])
            self.paths_m.append([])
            self.smooth_path_m.append([])

        
    def get_neighbors(self, current):
        neighbors = []
        dist = []
        # (Z,Y,X)
        # current[0] = z
        # current[1] = y
        # current[2] = x

        # Down Y-
        if current[1] > 0 and self.visited_3d[current[0],current[1]-1, current[2]] == 0:
            neighbors.append((current[0],current[1]-1, current[2]))
            dist.append(1)

        # UP Y+
        if current[1] < self.y_lim and self.visited_3d[current[0],current[1]+1, current[2]] == 0:
            neighbors.append((current[0],current[1]+1, current[2]))
            dist.append(1)
        
        # RIGHT X+
        if current[2] < self.x_lim and self.visited_3d[current[0], current[1],current[2]+1] == 0:
            neighbors.append((current[0], current[1],current[2]+1))
            dist.append(1)
        
        # LEFT X-
        if current[2] > 0 and self.visited_3d[current[0], current[1],current[2]-1] == 0:
            neighbors.append((current[0], current[1],current[2]-1))
            dist.append(1)
        
        # IN Z+
        if current[0] < self.z_lim and self.visited_3d[current[0]+1, current[1],current[2]] == 0:
            neighbors.append((current[0]+1, current[1],current[2]))
            dist.append(1)

        # out Z-
        if current[0] > 0 and self.visited_3d[current[0]-1, current[1],current[2]] == 0:
            neighbors.append((current[0]-1, current[1],current[2]))
            dist.append(1)
        
        # Down Y- RIGHT X+
        if current[1] > 0 and current[2] < self.x_lim and self.visited_3d[current[0], current[1]-1 ,current[2]+1] == 0:
            neighbors.append((current[0], current[1]-1 ,current[2]+1))
            dist.append(1.414)

        # Down Y- LEFT X-
        if current[1] > 0 and current[2] > 0 and self.visited_3d[current[0], current[1]-1 ,current[2]-1] == 0:
            neighbors.append((current[0], current[1]-1 ,current[2]-1))
            dist.append(1.414)

        #  Down Y- IN Z+ 
        if current[1] > 0 and current[0] < self.z_lim and self.visited_3d[current[0]+1, current[1]-1 ,current[2]] == 0:
            neighbors.append((current[0]+1, current[1]-1 ,current[2]))
            dist.append(1.414)
        
        #  Down Y- out Z-
        if current[1] > 0 and current[0] > 0 and self.visited_3d[current[0]-1, current[1]-1 ,current[2]] == 0:
            neighbors.append((current[0]-1, current[1]-1 ,current[2])) 
            dist.append(1.414)   

        # UP Y+ RIGHT X+
        if current[1] < self.y_lim and current[2] < self.x_lim and self.visited_3d[current[0], current[1]+1 ,current[2]+1] == 0:
            neighbors.append((current[0], current[1]+1 ,current[2]+1)) 
            dist.append(1.414)

        # UP Y+ LEFT X-
        if current[1] < self.y_lim and current[2] > 0 and self.visited_3d[current[0], current[1]+1 ,current[2]-1] == 0:
            neighbors.append((current[0], current[1]+1 ,current[2]-1)) 
            dist.append(1.414)    

        #  UP Y+ IN Z+ 
        if current[1] < self.y_lim and current[0] < self.z_lim and self.visited_3d[current[0]+1, current[1]+1 ,current[2]] == 0:
            neighbors.append((current[0]+1, current[1]+1 ,current[2]))   
            dist.append(1.414)

        #  UP Y+ out Z-
        if current[1] < self.y_lim and current[0] > 0 and self.visited_3d[current[0]-1, current[1]+1 ,current[2]] == 0:
            neighbors.append((current[0]-1, current[1]+1 ,current[2]))  
            dist.append(1.414) 

        # UP Y+ out Z-  RIGHT X+
        if current[0] > 0 and current[1] < self.y_lim and current[2] < self.x_lim and self.visited_3d[current[0]-1, current[1]+1 ,current[2]+1] == 0:
            neighbors.append((current[0]-1, current[1]+1 ,current[2]+1))   
            dist.append(1.732) 

        # UP Y+ out Z-  LEFT X-
        if current[0] > 0 and current[1] < self.y_lim and current[2] > 0 and self.visited_3d[current[0]-1, current[1]+1 ,current[2]-1] == 0:
            neighbors.append((current[0]-1, current[1]+1 ,current[2]-1)) 
            dist.append(1.732)       

        # Down Y- out Z-  RIGHT X+
        if current[0] > 0 and current[1] > 0 and current[2] < self.x_lim and self.visited_3d[current[0]-1, current[1]-1 ,current[2]+1] == 0:
            neighbors.append((current[0]-1, current[1]-1 ,current[2]+1)) 
            dist.append(1.732) 

        #  Down Y- out Z-  LEFT X-
        if current[0] > 0 and current[1] > 0 and current[2] > 0 and self.visited_3d[current[0]-1, current[1]-1 ,current[2]-1] == 0:
            neighbors.append((current[0]-1, current[1]-1 ,current[2]-1))   
            dist.append(1.732)   

        # UP Y+ IN Z+  RIGHT X+
        if current[0] < self.z_lim and current[1] < self.y_lim and current[2] < self.x_lim and self.visited_3d[current[0]+1, current[1]+1 ,current[2]+1] == 0:
            neighbors.append((current[0]+1, current[1]+1 ,current[2]+1)) 
            dist.append(1.732) 

        # UP Y+ IN Z+  LEFT X-
        if current[0] < self.z_lim and current[1] < self.y_lim and current[2] > 0 and self.visited_3d[current[0]+1, current[1]+1 ,current[2]-1] == 0:
            neighbors.append((current[0]+1, current[1]+1 ,current[2]-1)) 
            dist.append(1.732) 

        # Down Y- IN Z+  RIGHT X+
        if current[0] < self.z_lim and current[1] > 0 and current[2] < self.x_lim and self.visited_3d[current[0]+1, current[1]-1 ,current[2]+1] == 0:
            neighbors.append((current[0]+1, current[1]-1 ,current[2]+1)) 
            dist.append(1.732) 

        #  Down Y- IN Z+  LEFT X-
        if current[0] < self.z_lim and current[1] > 0 and current[2] > 0 and self.visited_3d[current[0]+1, current[1]-1 ,current[2]-1] == 0:
            neighbors.append((current[0]+1, current[1]-1 ,current[2]-1))
            dist.append(1.732) 

        return neighbors, dist

    def h(self, p1, p2):
        z1, y1, x1  = p1
        z2, y2, x2 = p2
        return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)


    def reconstruct_path(self, came_from, current, start):
        path = []
        while current in came_from.keys():
            path.append(current)
            current = came_from[current]
        path.append(start)
        return np.array(path[::-1])


    def A_star(self, start, goal):
        came_from = {}
        open_set = {}
        g_score = np.ones(self.grid_3d.shape) * np.inf
        g_score[start] = 0
        f_score = np.ones(self.grid_3d.shape) * np.inf
        f_score[start] = self.h(start, goal)
        open_set[start] = f_score[start]

        while len(open_set) != 0:
            current = min(open_set, key=open_set.get)
            if current == goal:
                return self.reconstruct_path(came_from, current, start)
            
            del open_set[current]
            self.visited_3d[current] = 1 # 1 mark as visited
            neighbors, dist = self.get_neighbors(current)
            for i in range(len(dist)):
                neigbor = neighbors[i]
                tentative_g_score = g_score[current] + dist[i]
                if tentative_g_score < g_score[neigbor]:
                    came_from[neigbor] = current
                    g_score[neigbor] = tentative_g_score
                    f_score[neigbor] = tentative_g_score + self.h(neigbor, goal)
                    if neigbor not in open_set.keys():
                        open_set[neigbor] = f_score[neigbor]
        return False #could not find path


    def get_smooth_path(self, path ,len1 ,len3):
        # s = smoothness, m > k must hold, default k degree is  k=3, m is number of points
        weights = np.ones(len(path))*10
        weights[0:len1] = 100
        weights[len(path)-len3:] = 100
        tck, _ = interpolate.splprep([path[:,0], path[:,1], path[:,2]],w=weights,s=10)  
        u_fine = np.linspace(0,1,30) # determine number of points in smooth path 
        smooth_path = interpolate.splev(u_fine, tck)
        return np.transpose(np.array(smooth_path))

    def inflate(self, path):
        distance_idx = int(self.safety_distance/self.res)
        block_volume = []
        for node in path:
            for z in range(node[0]-3,node[0]+3):
                if z > self.z_lim - 1:
                    z = self.z_lim -1
                if z < 0:
                    z = 0
                for y in range(node[1]-distance_idx,node[1]+distance_idx):
                    if y > self.y_lim - 1:
                        y = self.y_lim -1
                    if y < 0:
                        y = 0
                    for x in range(node[2]-distance_idx, node[2]+ distance_idx):
                        if x > self.x_lim - 1:
                            x = self.x_lim -1
                        if x < 0:
                            x = 0

                        block_volume.append((z,y,x))
        return np.array(block_volume)


    def covert_meter2idx(self, coords_meter): # (x,y,z) -> (z,y,x)
        return (int((coords_meter[2]-self.minimum_floor_distance)/self.res ), int(coords_meter[1]/self.res + self.y_lim/2)  , int(coords_meter[0]/self.res ) ) 

    def convert_idx2meter(self, coords_idx): #(z,y,x) -> (x,y,z)
        coord_m = np.stack(((coords_idx[:,2] ) * self.res, (coords_idx[:,1] - self.y_lim/2) * self.res, coords_idx[:,0] * self.res + self.minimum_floor_distance), axis=-1)
        return coord_m
        

    def get_path(self, start_m, goal_m):
        """
        this function make sure good approach at zero yaw to target and also 0 yaw when return to base
        """
        start = self.covert_meter2idx(start_m)
        goal = self.covert_meter2idx(goal_m)
        break_trajecoty_len = abs(start_m[0] - goal_m[0]) * 0.2
        intermidiate_1 = self.covert_meter2idx((start_m[0] + break_trajecoty_len, start_m[1], start_m[2]))
        intermidiate_2 = self.covert_meter2idx((goal_m[0] - break_trajecoty_len, goal_m[1], goal_m[2]))
        if self.grid_3d[goal] == 1: # fast sanity check of goal occupancy status
            print('sanity check failed')
            return 0 
        try:
            path1 = self.A_star(start, intermidiate_1)
            path1 = path1[:-1]
            self.visited_3d = self.grid_3d.copy()
            path2 = self.A_star(intermidiate_1, intermidiate_2)
            path2 = path2[:-1]
            self.visited_3d = self.grid_3d.copy()
            path3 = self.A_star(intermidiate_2, goal)
            self.visited_3d = self.grid_3d.copy()
            path = np.vstack((path1, path2, path3))
            # -------- convert idx 2 meter
            segment1_m = self.convert_idx2meter(path1)
            segment2_m = self.convert_idx2meter(path2)
            segment3_m = self.convert_idx2meter(path3)
            # --------- replace to accurate location
            segment1_m[:,1] ,segment1_m[:,2] =  start_m[1], start_m[2]
            segment3_m[:,1], segment3_m[:,2] = goal_m[1], goal_m[2]
            return segment1_m, segment2_m, segment3_m, path
        except:
            print('error in creating segments')
            return None

    def plan(self, start_m, goal_m, start_title, goal_title ,drone_idx, drone_num, at_base):
        
        # update grid_3D, exclude current drone block_volume
        self.grid_3d = np.zeros([self.grid_3d_shape[0], self.grid_3d_shape[1], self.grid_3d_shape[2]], dtype=int) #z y x - reset grid_3d
        for i in range(drone_num):
            if (i != drone_idx) and (len(self.block_volume[i]) > 0) and (at_base[i] == 0):
                self.grid_3d[self.block_volume[i][:,0], self.block_volume[i][:,1], self.block_volume[i][:,2]] = 1
        self.visited_3d = self.grid_3d.copy()


        if (start_title == 'base' and goal_title == 'target'):
            try:
                segment1_m, segment2_m, segment3_m, path = self.get_path(start_m, goal_m)
                self.block_volume[drone_idx] = self.inflate(path)
                self.paths_m[drone_idx] = np.vstack((segment1_m, segment2_m, segment3_m))
                self.smooth_path_m[drone_idx] = self.get_smooth_path(path=self.paths_m[drone_idx],len1=len(segment1_m),len3=len(segment3_m))  
                self.block_volumes_m[drone_idx] = self.convert_idx2meter(self.block_volume[drone_idx])
                print('Path Found')
                return 1
            except:
                print(' No Path Found! agent = '+str( drone_idx)+' from '+str(start_title)+ ' to '+ str(goal_title)+' start:'+str(start_m)+' goal:'+str(goal_m) + '')
                return 0
        
        elif (start_title == 'target' and goal_title == 'base'):
            try:
                segment1_m, segment2_m, segment3_m, path = self.get_path(goal_m, start_m)
                self.block_volume[drone_idx] = self.inflate(path)
                self.paths_m[drone_idx] = np.vstack((segment1_m, segment2_m, segment3_m))[::-1]
                self.smooth_path_m[drone_idx] = self.get_smooth_path(path=self.paths_m[drone_idx],len1=len(segment3_m),len3=len(segment1_m))  
                self.block_volumes_m[drone_idx] = self.convert_idx2meter(self.block_volume[drone_idx])
                print('Path Found')
                return 1
            except:
                print(' No Path Found! agent = '+str( drone_idx)+' from '+str(start_title)+ ' to '+ str(goal_title)+' start:'+str(start_m)+' goal:'+str(goal_m) + '')
                return 0


        elif (start_title == 'target' and goal_title == 'target'):
            retreat_dist = 0.7
            intermidiate_m = (min([start_m[0],goal_m[0]]) - retreat_dist, (start_m[1]+goal_m[1])/2, (start_m[2]+goal_m[2])/2)
            try:
                segment1_m, segment2_m, segment3_m, path = self.get_path(start_m, intermidiate_m)
                block_volume1 = self.inflate(path)
                path1_m = np.vstack((segment1_m, segment2_m, segment3_m))
                smooth_path_m1 = self.get_smooth_path(path=path1_m, len1=len(segment1_m), len3=len(segment3_m))
                block_volume1_m = self.convert_idx2meter(self.block_volume[drone_idx])

                segment1_m, segment2_m, segment3_m, path = self.get_path(intermidiate_m, goal_m)
                block_volume2 = self.inflate(path)
                path2_m = np.vstack((segment1_m, segment2_m, segment3_m))
                smooth_path_m2 = self.get_smooth_path(path=path2_m, len1=len(segment1_m), len3=len(segment3_m))
                block_volume2_m = self.convert_idx2meter(self.block_volume[drone_idx])

                self.block_volume[drone_idx] = np.vstack((block_volume1,block_volume2))
                self.paths_m[drone_idx] = np.vstack((path1_m, path2_m))
                self.smooth_path_m[drone_idx] = np.vstack((smooth_path_m1, smooth_path_m2))
                self.block_volumes_m[drone_idx] = np.vstack((block_volume1_m, block_volume2_m))
                return 1
            except:
                print(' No Path Found! agent = '+str( drone_idx)+' from '+str(start_title)+ ' to '+ str(goal_title)+' start:'+str(start_m)+' goal:'+str(goal_m) + ' ')
                return 0
