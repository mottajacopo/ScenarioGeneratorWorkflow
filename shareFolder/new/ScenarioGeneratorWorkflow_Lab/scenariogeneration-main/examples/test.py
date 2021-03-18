
import random
import carla
import pyoscx
import math

#import Image

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage


#connect to carla server and get informations of the world
client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()
current_map = world.get_map()
i = current_map.name

def carla2pyxosc(spawn):   #convert carla location to pyxosc

    x = spawn.location.x
    y = spawn.location.y *(-1)  #multiply for -1 because of carla bug
    z = spawn.location.z
    h = math.radians(spawn.rotation.yaw) *(-1)   #multiply for -1 because of carla bug

    return pyoscx.TeleportAction(pyoscx.WorldPosition(x, y, z, h))

def shift_lane(pos, direction):
    current_map = world.get_map()

    new_pos = pos
    carla_loc = carla.Location(new_pos.position.x, new_pos.position.y, new_pos.position.z)
    waypoint = current_map.get_waypoint(carla_loc)

    if (direction == 'right'):
        lane_change = waypoint.get_right_lane()
        new_c = lane_change.transform.location

    elif(direction == 'left'):
        lane_change = waypoint.get_left_lane()
        new_c = lane_change.transform.location

    new_pos.position.x = new_c.x
    new_pos.position.y = new_c.y
    new_pos.position.z = new_c.z

    return pos

def get_random_npc_spawn(current_map, ego_spawn,radius,check_lane):

    npc_spawns = []

    radius1 = radius
    radius3 = 50

    c_x = ego_spawn.location.x
    c_y = ego_spawn.location.y #*(-1)

    ego_waypoint = current_map.get_waypoint(ego_spawn.location)
    ego_lane_id = ego_waypoint.lane_id
    
    if (check_lane == "left" ):
        lane_change_id = ego_waypoint.get_left_lane().lane_id
    elif(check_lane == "right" ):
        lane_change_id = ego_waypoint.get_right_lane().lane_id
    else:
        lane_change_id = 999

    npc_lane = []
    npc_lane_id = []

    spawn_transforms = current_map.get_spawn_points()
    for spawn in spawn_transforms:
        random_waypoint = current_map.get_waypoint(spawn.location)
        random_lane_id = random_waypoint.lane_id
        if(spawn != ego_spawn):
            if (c_x-spawn.location.x)**2 + (c_y-spawn.location.y)**2 <= radius1**2:
                if ((random_lane_id != lane_change_id) and (random_lane_id != ego_lane_id)):
                    npc_spawns.append(carla2pyxosc(spawn))
                    #npc_lane.append(carla2pyxosc(spawn))
                elif(c_x-spawn.location.x)**2 + (c_y-spawn.location.y)**2 >= (radius3 + 10)**2:
                    npc_lane.append(carla2pyxosc(spawn))
                    npc_spawns.append(carla2pyxosc(spawn))

    
    return npc_spawns, npc_lane

def get_random_spawn_points(offset, check_lane):   #get spawn points for ego, adversary and npcs

    current_map = world.get_map()
    # spawn_transforms will be a list of carla.Transform
    spawn_transforms = current_map.get_spawn_points()

    # get a single random spawn transformation over the map
    random_spawn = random.choice(spawn_transforms)

    #convert transform to waypoint
    waypoint = current_map.get_waypoint(random_spawn.location)

    npc_spawns = []

    random_spawn = random.choice(spawn_transforms)

    #random_spawn.location.x = 43.45
    #random_spawn.location.y = -84.09
    #random_spawn.location.z = 0.5
    #random_spawn.rotation.yaw = -82

    #avoid spawn points near intersections
    while (waypoint.is_intersection or waypoint.is_junction):
        random_spawn = random.choice(spawn_transforms)
        waypoint = current_map.get_waypoint(random_spawn.location) 
        #if scenario requested do a lane check to see if left lane is free
        if(check_lane == "left"):
            while ((waypoint.lane_change != carla.libcarla.LaneChange.Both or waypoint.lane_change != carla.libcarla.LaneChange.Left) and waypoint.get_left_lane() ):
                random_spawn = random.choice(spawn_transforms)
                waypoint = current_map.get_waypoint(random_spawn.location)  
        elif(check_lane == "right"):
            while ((waypoint.lane_change != carla.libcarla.LaneChange.Both or waypoint.lane_change != carla.libcarla.LaneChange.Right) and waypoint.get_right_lane() ):
                random_spawn = random.choice(spawn_transforms)
                waypoint = current_map.get_waypoint(random_spawn.location)   
        elif(check_lane == "both"):
            while (waypoint.lane_change != carla.libcarla.LaneChange.Both and waypoint.get_right_lane() ):
                random_spawn = random.choice(spawn_transforms)
                waypoint = current_map.get_waypoint(random_spawn.location)   
   

    #random_spawn.location.x = 43.45
    #random_spawn.location.y = -84.09
    #random_spawn.location.z = 0.5
    #random_spawn.rotation.yaw = -82



    waypoint = current_map.get_waypoint(random_spawn.location)
    lane_change = waypoint.get_left_lane()
    lane_change_id = waypoint.get_left_lane().lane_id

    #compute adversary spawn point 
    random_spawn_offset = get_offset_waypoint(waypoint, offset)


    shifted_position = pyoscx.LanePosition(waypoint.s, 0, waypoint.lane_id, waypoint.road_id)
    #convert carla location to pyxosc location
    egostart = carla2pyxosc(random_spawn)
    targetstart = carla2pyxosc(random_spawn_offset.transform)

    egostart = shift_lane(egostart, 'right')



    npc_spawns, npc_lane = get_random_npc_spawn(current_map, random_spawn,100,check_lane)

    
    im = plt.imread(str(current_map.name) + ".jpg")
    im2 = ndimage.rotate(im, 180)
    #im2 = np.flipud(im)

    #plt.imshow(im2, extent=[-10, 403, 10, -338])  #Town01
    #plt.imshow(im2, extent=[-14, 200, -100, -314])  #Town02
    #plt.imshow(im2, extent=[260, -160, 220, -220])  #Town03
    plt.imshow(im2, extent=[420, -522, 403, -450])  #Town04
    #plt.imshow(im2, extent=[-282, 220, 220, -219])  #Town05
    #plt.imshow(im2, extent=[-378, 675, 160, -410])  #Town06


    circle1 = plt.Circle((random_spawn.location.x, (-1)*random_spawn.location.y), 100, color='g', alpha=0.2)
    plt.gca().add_patch(circle1)
    circle2 = plt.Circle((random_spawn.location.x, (-1)*random_spawn.location.y), 50, color='c', alpha=0.2)
    plt.gca().add_patch(circle2)

    for i in spawn_transforms:
        plt.scatter(i.location.x,(-1)*i.location.y,s = 3, c='r')

    for i in npc_spawns:
        plt.scatter(i.position.x,i.position.y,s = 3, c='m')

    for i in npc_lane:
        plt.scatter(i.position.x,i.position.y,s = 3, c='g')

    plt.scatter(egostart.position.x, egostart.position.y ,s = 5, c='b')
    plt.scatter(targetstart.position.x, targetstart.position.y ,s = 5, c='c')

    plt.show()
    #plt.pause(1)
    #plt.savefig('testplot' + str(random_spawn) +'.jpg', dpi=300)
    #plt.close()
    
    
    return egostart, targetstart, npc_spawns 

def get_offset_waypoint(waypoint_ego, offset):   #computer offset waypoint
    waypoint = waypoint_ego
    traveled_distance = 0
    distance = offset
    while traveled_distance < distance: 
        waypoint_new = waypoint.next(1.0)[-1]
        traveled_distance += waypoint_new.transform.location.distance(waypoint.transform.location)
        waypoint = waypoint_new
    return waypoint




targetstart, egostart,  npc_spawns = get_random_spawn_points( 50,'right')

