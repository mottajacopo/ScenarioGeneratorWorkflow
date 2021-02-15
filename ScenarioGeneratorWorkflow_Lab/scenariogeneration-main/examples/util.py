
import random
import carla
import pyoscx
import math

#connect to carla server and get informations of the world
client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()
current_map = world.get_map()

def get_random_spawn_points(offset, check_lane):   #get spawn points for ego, adversary and npcs

    # spawn_transforms will be a list of carla.Transform
    spawn_transforms = current_map.get_spawn_points()

    # get a single random spawn transformation over the map
    random_spawn = random.choice(spawn_transforms)

    #convert transform to waypoint
    waypoint = current_map.get_waypoint(random_spawn.location)

    #if scenario requested do a lane check to see if left lane is free
    if(check_lane):
        while (not(waypoint.lane_change == carla.libcarla.LaneChange.Both or waypoint.lane_change == carla.libcarla.LaneChange.Left)):
            random_spawn = random.choice(spawn_transforms)
            waypoint = current_map.get_waypoint(random_spawn.location)  
                  
    #compute adversary spawn point 
    random_spawn_offset = get_offset_waypoint(waypoint, offset)

    #convert carla location to pyxosc location
    egostart = carla2pyxosc(random_spawn)
    targetstart = carla2pyxosc(random_spawn_offset.transform)

    npc_spawns = get_random_npc_spawn(random_spawn,80)

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
                        'vehicle.bmw.isetta']

    vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
    vehicle_name = vehicle_bp.id

    while (vehicle_name in vehicles_blacklist):
        vehicle_bp = random.choice(blueprint_library.filter('vehicle.*.*'))
        vehicle_name = vehicle_bp.id

    return vehicle_name







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

def get_random_npc_spawn(ego_spawn,radius):
    npc_spawns = []

    radius1 = radius
    radius2 = 5
    c_x = ego_spawn.location.x
    c_y = ego_spawn.location.y

    for i in range(2):
        spawn_transforms = current_map.get_spawn_points()
        for spawn in spawn_transforms:
            if (c_x-spawn.location.x)**2 + (c_y-spawn.location.y)**2 <= radius1**2:
                if (c_x-spawn.location.x)**2 + (c_y-spawn.location.y)**2 >= radius2**2:
                    npc_spawns.append(carla2pyxosc(spawn))


    return npc_spawns
