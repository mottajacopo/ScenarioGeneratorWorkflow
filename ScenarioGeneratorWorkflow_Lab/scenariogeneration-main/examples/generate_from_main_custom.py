""" example of creating OpenSCENARIO and OpenDRIVE file, with the parameters defined outside the class structure

    Example usage: when a itterative procedure is defined and the parameters to the Scenario will change

    Will generate N scenarios
"""

import pyodrx
import math
import pyoscx
from scenariogeneration import ScenarioGenerator
import json
import random
import carla

def get_random_spawn_points(offset):

    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0)
    world = client.get_world()
    current_map = world.get_map()

    # spawn_transforms will be a list of carla.Transform
    spawn_transforms = current_map.get_spawn_points()

    # get a single random spawn transformation over the map
    random_spawn = random.choice(spawn_transforms)

    waypoint = current_map.get_waypoint(random_spawn.location)

    traveled_distance = 0
    distance = offset
    while traveled_distance < distance: 
        waypoint_new = waypoint.next(1.0)[-1]
        traveled_distance += waypoint_new.transform.location.distance(waypoint.transform.location)
        waypoint = waypoint_new


    ego_x = random_spawn.location.x
    ego_y = random_spawn.location.y *(-1)
    ego_z = random_spawn.location.z
    ego_h = math.radians(random_spawn.rotation.yaw) *(-1)

    egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(ego_x, ego_y, ego_z, ego_h))

    other_x = waypoint.transform.location.x
    other_y = waypoint.transform.location.y *(-1)
    other_z = waypoint.transform.location.z
    other_h = math.radians(waypoint.transform.rotation.yaw) *(-1)

    targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(other_x, other_y, other_z, other_h))


    return egostart, targetstart 


class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.naming = 'numerical'

    def scenario(self,**kwargs):
        
        ### create catalogs
        catalog = pyoscx.Catalog()

        ### create road
        road = pyoscx.RoadNetwork(roadfile='Town06',scenegraph=" ")


        ### create parameters
        paramdec = pyoscx.ParameterDeclarations()
        paramdec.add_parameter(pyoscx.Parameter('leadingSpeed',pyoscx.ParameterType.double,'0.0'))

        ###create properties

        #prop= pyoscx.Properties()
        #prop.add_property


        ### create vehicles

        bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
        fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
        ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
        ego_veh = pyoscx.Vehicle('vehicle.tesla.model3',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)
        ego_veh.add_property(name='type',value='ego_vehicle')
        ego_veh.add_property(name='color',value='255,69,0')
        bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
        fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
        ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
        other_veh = pyoscx.Vehicle('vehicle.tesla.model3',pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)
        other_veh.add_property(name='type',value='simulation')

        ## create entities

        egoname = 'hero'
        targetname = 'adversary'

        entities = pyoscx.Entities()

        entities.add_scenario_object(egoname,ego_veh)

        entities.add_scenario_object(targetname,other_veh)


        timeofday=pyoscx.TimeOfDay(True,2020,12,11,21,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1", timeofday,weather,roadcond)

        # egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-9.4,-152.8,0.5,1.57079632679))


        # prop= pyoscx.Properties()
        # prop.add_property(name='module',value='external_control')
        # contr = pyoscx.Controller('HeroAgent',prop)


        ### create init
        init = pyoscx.Init()

        #environment
        timeofday=pyoscx.TimeOfDay(True,2020,12,11,11,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1",timeofday,weather,roadcond)
        envAct= pyoscx.EnvironmentAction("Environment1", env)

        #controller
        # prop= pyoscx.Properties()
        # prop.add_property(name='module',value='external_control')
        # contr = pyoscx.Controller('HeroAgent',prop)
        # controllerAct = pyoscx.AssignControllerAction(contr)

        #step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

        #targetspeed = pyoscx.AbsoluteSpeedAction(15,step_time)
        targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,-80,0.5,4.7))
        #targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(190,133,0.5,0))

        #egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-9.4,-152.8,0.5,1.57079632679))
        egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,80,0.5,4.7))
        egospeed = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed'],pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))
        
        if(kwargs['randomPosition']):
            egostart, targetstart = get_random_spawn_points(kwargs['initialOffset'])


        init.add_global_action(envAct)
        init.add_init_action(egoname,egospeed)
        init.add_init_action(egoname,egostart)
        #init.add_init_action(egoname,controllerAct)
        #init.add_init_action(targetname,targetspeed)
        init.add_init_action(targetname,targetstart)


        ### create an event

        trigcond = pyoscx.RelativeDistanceCondition(50,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)


        trigger = pyoscx.EntityTrigger('distancetrigger',0.0,pyoscx.ConditionEdge.none,trigcond,egoname)

        event = pyoscx.Event('HeroSotps',pyoscx.Priority.overwrite)
        event.add_trigger(trigger)
        linear = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,30)
        action1 = pyoscx.AbsoluteSpeedAction('$leadingSpeed',linear)
        event.add_action('HeroStops',action1)


        ## create the maneuver 
        man = pyoscx.Maneuver('my_maneuver')
        man.add_event(event)

        mangr = pyoscx.ManeuverGroup('mangroup')
        mangr.add_actor('hero')
        mangr.add_maneuver(man)
        starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        act = pyoscx.Act('my_act',starttrigger)
        act.add_maneuver_group(mangr)

        # create the story
        #storyparam = pyoscx.ParameterDeclarations()
        #storyparam.add_parameter(pyoscx.Parameter('adversary',pyoscx.ParameterType.string,targetname))
        story = pyoscx.Story('mystory')
        story.add_act(act)


        ## create the storyboard
        sb = pyoscx.StoryBoard(init,pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(75,pyoscx.Rule.greaterThan),'stop'))
        sb.add_story(story)

        ## create the scenario
        sce = pyoscx.Scenario('approaching_static_object','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

        return sce

if __name__ == "__main__":
    s = Scenario()
 
    parameters = {}
    #parameters['approachSpeed2'] = [10, 20, 30]
    #parameters['initialOffset2'] = [100, 150]
    #parameters['randomPosition2'] = [True]

    # JSON file 
    f = open ('param.json', "r") 
  
    # Reading from file 
    data = json.loads(f.read()) 
  
    for jsonParam in data['Parameters']: 
        for value in jsonParam:
            parameters[value] = jsonParam[value]

    s.print_permutations(parameters)

    s.generate('my_scenarios',parameters)


