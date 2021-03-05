
import random
import carla
import pyoscx
import math
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

#connect to carla server and get informations of the world
client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()
iteration = -1

def check_town(town):
    current_map = world.get_map()

    if(current_map.name != town):
        client.load_world(town)
        print("The CARLA server uses the wrong map:")
        print("Loading correct map: ...wait")
        time.sleep(4)


def get_random_spawn_points(offset, check_lane):   #get spawn points for ego, adversary and npcs

    current_map = world.get_map()

    # spawn_transforms will be a list of carla.Transform
    spawn_transforms = current_map.get_spawn_points()

    # get a single random spawn transformation over the map
    random_spawn = random.choice(spawn_transforms)

    #convert transform to waypoint
    waypoint = current_map.get_waypoint(random_spawn.location)

    npc_spawns = []

    #check_intersection = waypoint.is_intersection or waypoint.is_junction

    #if scenario requested do a lane check to see if left lane is free
    if(check_lane == "left"):
        while (not(waypoint.lane_change == carla.libcarla.LaneChange.Both or waypoint.lane_change == carla.libcarla.LaneChange.Left)):
            random_spawn = random.choice(spawn_transforms)
            waypoint = current_map.get_waypoint(random_spawn.location)  
    elif(check_lane == "right"):
        while (not(waypoint.lane_change == carla.libcarla.LaneChange.Both or waypoint.lane_change == carla.libcarla.LaneChange.Right)):
            random_spawn = random.choice(spawn_transforms)
            waypoint = current_map.get_waypoint(random_spawn.location)   
    elif(check_lane == "both"):
        while (not(waypoint.lane_change == carla.libcarla.LaneChange.Both)):
            random_spawn = random.choice(spawn_transforms)
            waypoint = current_map.get_waypoint(random_spawn.location)  


    ego_spawn = random_spawn
    ego_waypoint = current_map.get_waypoint(ego_spawn.location)            
                    
    #compute adversary spawn point 
    target_spawn_offset = get_offset_waypoint(ego_waypoint, offset)

    #convert carla location to pyxosc location
    egostart = carla2pyxosc(ego_spawn)
    targetstart = carla2pyxosc(target_spawn_offset.transform)

    npc_spawns, npc_lane = get_random_npc_spawn(current_map, ego_spawn, 150, offset, check_lane)

    """

    im = plt.imread(str(current_map.name) + ".jpg")
    im2 = ndimage.rotate(im, 180)
    im2 = np.flipud(im)

    #plt.imshow(im2, extent=[-10, 403, 10, -338])  #Town01
    #plt.imshow(im2, extent=[-14, 200, -100, -314])  #Town02
    #plt.imshow(im2, extent=[260, -160, 220, -220])  #Town03
    #plt.imshow(im2, extent=[420, -522, 403, -450])  #Town04
    plt.imshow(im2, extent=[-282, 220, 220, -219])  #Town05
    #plt.imshow(im2, extent=[-378, 675, 160, -410])  #Town06

    global iteration 
    iteration += 1
    circle1 = plt.Circle((random_spawn.location.x, (-1)*random_spawn.location.y), 100, color='g', alpha=0.2)
    plt.gca().add_patch(circle1)
    circle2 = plt.Circle((random_spawn.location.x, (-1)*random_spawn.location.y), 5, color='c', alpha=0.2)
    plt.gca().add_patch(circle2)

    for i in spawn_transforms:
        plt.scatter(i.location.x,(-1)*i.location.y,s = 1, c='r')

    for i in npc_spawns:
        plt.scatter(i.position.x,i.position.y,s = 1, c='m')

    for i in npc_lane:
        plt.scatter(i.position.x,i.position.y,s = 1, c='g')

    plt.scatter(egostart.position.x, egostart.position.y ,s = 3, c='b')
    plt.scatter(targetstart.position.x, targetstart.position.y ,s = 3, c='c')

    #plt.show(block=False)
    #plt.pause(1)
    plt.savefig('testplot' + str(iteration) +'.jpg', dpi=300)
    plt.close()
    
    """

    return egostart, targetstart, npc_spawns 

def get_random_vehicles():   #get random vehicle name

    blueprint_library = world.get_blueprint_library()

    vehicles_blacklist = ['vehicle.bh.crossbike',
                        'vehicle.kawasaki.ninja',
                        'vehicle.yamaha.yzf',
                        'vehicle.harley-davidson.low_rider',
                        'vehicle.gazelle.omafiets',
                        'vehicle.diamondback.century',
                        'vehicle.tesla.cybertruck',
                        'vehicle.bmw.isetta',
                        'vehicle.tesla.model3']

    vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
    vehicle_name = vehicle_bp.id

    while (vehicle_name in vehicles_blacklist):
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
        vehicle_name = vehicle_bp.id

    return vehicle_name


def get_offset_waypoint(waypoint_ego, offset):   #computer offset waypoint
    waypoint = waypoint_ego
    traveled_distance = 0
    distance = offset
    while traveled_distance < distance: 
        waypoint_new = waypoint.next(1.0)[-1]
        traveled_distance += waypoint_new.transform.location.distance(waypoint.transform.location)
        waypoint = waypoint_new
    return waypoint

def carla2pyxosc(spawn):   #convert carla location to pyxosc

    x = spawn.location.x
    y = spawn.location.y *(-1)  #multiply for -1 because of carla bug
    z = spawn.location.z
    h = math.radians(spawn.rotation.yaw) *(-1)   #multiply for -1 because of carla bug

    return pyoscx.TeleportAction(pyoscx.WorldPosition(x, y, z, h))


def get_random_npc_spawn(current_map, ego_spawn,radius, offset, check_lane):

    npc_spawns = []

    radius1 = radius
    radius3 = offset

    c_x = ego_spawn.location.x
    c_y = ego_spawn.location.y

    ego_waypoint = current_map.get_waypoint(ego_spawn.location)
    ego_lane_id = ego_waypoint.lane_id

    if (check_lane == "left" and ego_waypoint.get_left_lane() != None):
        lane_change_id = ego_waypoint.get_left_lane().lane_id
    elif(check_lane == "right" and ego_waypoint.get_left_lane() != None):
        lane_change_id = ego_waypoint.get_right_lane().lane_id
    else:
        lane_change_id = 999


    npc_lane = []

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
