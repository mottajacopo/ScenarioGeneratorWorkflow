import random
import carla
import json
import math
import pyoscx

client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()
current_map = world.get_map()

# spawn_transforms will be a list of carla.Transform
spawn_transforms = current_map.get_spawn_points()

# get a single random spawn transformation over the map
random_spawn = random.choice(spawn_transforms)
#random_spawn.location.x = -8.5
#random_spawn.location.y = 80
#random_spawn.location.z = 0.5
#random_spawn.rotation.yaw = 90

waypoint = current_map.get_waypoint(random_spawn.location)

traveled_distance = 0
distance = 10
while traveled_distance < distance: 
    waypoint_new = waypoint.next(1.0)[-1]
    traveled_distance += waypoint_new.transform.location.distance(waypoint.transform.location)
    waypoint = waypoint_new

i = 0

ego_x = random_spawn.location.x
ego_y = random_spawn.location.y
ego_z = random_spawn.location.z
ego_h = math.radians(random_spawn.rotation.yaw)

egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(ego_x, ego_y, ego_z, ego_h))

other_x = waypoint.transform.location.x
other_y = waypoint.transform.location.y
other_z = waypoint.transform.location.z
other_h = math.radians(waypoint.transform.rotation.yaw)

targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(other_x, other_y, other_z, other_h))


for waypoints in current_map.get_spawn_points():
    world.debug.draw_string(waypoint.transform.location, 'o', draw_shadow=False,color=carla.Color(r=255, g=255, b=255), life_time=0.2,persistent_lines=True)
											 
											 




"""  #save json file with positions
data = {}
data["Town07"] = []
for pos in spawn_transforms:
    item = {}
    item["x"] = pos.location.x
    item["y"] = pos.location.y
    item["z"] = pos.location.z
    item["h"] = pos.rotation.yaw
    data["Town07"].append(item)


with open('Town07.json', 'w') as outfile:
    json.dump(data, outfile)

"""
