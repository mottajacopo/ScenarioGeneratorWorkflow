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
import util
import time

class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.naming = 'numerical'

    def scenario(self,**kwargs):

        #get random position for ego, target and npcs
        if(kwargs['randomPosition']):
            targetstart, egostart, npc_spawns = util.get_random_spawn_points( kwargs['initialOffset'],kwargs['check_lane'])   #inverto posizioni di ego rispetto a adversary per il cutin
        else:
            #put a default position here
            print("default position not setted")
            exit

        targetstart = util.shift_lane(targetstart, kwargs['check_lane'])  ###################cutin
        
        ### create catalogs
        catalog = pyoscx.Catalog()

        ### create road
        road = pyoscx.RoadNetwork(roadfile=kwargs['Town'],scenegraph=" ")

        ### create parameters
        paramdec = pyoscx.ParameterDeclarations()

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
        other_veh = pyoscx.Vehicle(util.get_random_vehicles(),pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)
        other_veh.add_property(name='type',value='simulation')

        ## create entities

        egoname = 'hero'
        targetname = 'adversary'
        npcname = 'npc'

        entities = pyoscx.Entities()

        entities.add_scenario_object(egoname,ego_veh)
        entities.add_scenario_object(targetname,other_veh)

        if (kwargs['npc_number'] > len(npc_spawns)):
            npc_number = len(npc_spawns)
        else:
            npc_number = kwargs['npc_number']

        #create npcs entities with random vehicle
        for i in range(npc_number):
            npc_veh = pyoscx.Vehicle(util.get_random_vehicles(),pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)    
            npc_veh.add_property(name='type',value='ego_vehicle')
            entities.add_scenario_object((npcname + str(i)),npc_veh)     


        #environment
        timeofday=pyoscx.TimeOfDay(True,2020,12,11,kwargs['hourOfDay'],52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        if(kwargs['isRaining']):
            weather=pyoscx.Weather(pyoscx.CloudState.overcast,1,0,1,pyoscx.PrecipitationType.rain,1,100000)
        else:
            weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,1,100000)
        env=pyoscx.Environment("Environment1",timeofday,weather,roadcond)
        envAct= pyoscx.EnvironmentAction("Environment1", env)


        #targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,-80,0.5,4.7))
        #step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)
        #targetspeed = pyoscx.AbsoluteSpeedAction(15,step_time)

        #egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-2.6,80,0.5,4.7))
        egospeed = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed']/2,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))
        targetspeed = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed'],pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))


        ### create init
        init = pyoscx.Init()

        init.add_global_action(envAct)
        init.add_init_action(egoname,egospeed)
        init.add_init_action(egoname,egostart)
        init.add_init_action(targetname,targetspeed)
        init.add_init_action(targetname,targetstart)

        #init npcs start positions
        npcstart_list = []
        for i in range(npc_number):
            spawn = random.choice(npc_spawns)
            while([spawn.position.x, spawn.position.y] in npcstart_list):
                spawn = random.choice(npc_spawns)
            
            npcstart_list.append([spawn.position.x, spawn.position.y])
            init.add_init_action((npcname + str(i)),spawn)

        ### create an event

        #autopilot for npcs
        ap_starttrigger = pyoscx.ValueTrigger('StartCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        ap_eventstart = pyoscx.Event('StartAutopilot',pyoscx.Priority.overwrite)
        ap_eventstart.add_trigger(ap_starttrigger)
        ap_actionstart = pyoscx.ActivateControllerAction(False,True)
        ap_eventstart.add_action('StartAutopilot',ap_actionstart)

        ap_stoptrigger = pyoscx.ValueTrigger('StopCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(30,pyoscx.Rule.greaterThan))
        ap_eventstop = pyoscx.Event('StopAutopilot',pyoscx.Priority.overwrite)
        ap_eventstop.add_trigger(ap_stoptrigger)
        ap_actionstop = pyoscx.ActivateControllerAction(False,False)
        ap_eventstop.add_action('StopAutopilot',ap_actionstop)


        #adv cut lane
        trigcond = pyoscx.RelativeDistanceCondition(4,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,egoname,freespace=False)
        trigger = pyoscx.EntityTrigger('distancetrigger',0.0,pyoscx.ConditionEdge.none,trigcond,targetname)

        event = pyoscx.Event('AdvChangesLane',pyoscx.Priority.overwrite)
        event.add_trigger(trigger)
        sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)

        if(kwargs['check_lane'] == 'left'):
            lane_offset = 1
        elif(kwargs['check_lane'] == 'right'):
            lane_offset = -1
        else:
            lane_offset = 1

        action = pyoscx.RelativeLaneChangeAction(lane_offset ,targetname,sin_time)
        event.add_action('AdvChangesLane',action)

        ## create the maneuver 
        man = pyoscx.Maneuver('my_maneuver')
        man.add_event(event)

        mangr = pyoscx.ManeuverGroup('mangroup')
        mangr.add_actor('adversary')
        mangr.add_maneuver(man)
        starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        stoptrigger = pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(10,pyoscx.Rule.greaterThan),'stop')
        act = pyoscx.Act('my_act',starttrigger,stoptrigger)

        act.add_maneuver_group(mangr)

        #maneuver for npcs 
        for i in range(npc_number):
            npc_man = pyoscx.Maneuver('AutopilotSequenceNPC'+str(i))
            npc_man.add_event(ap_eventstart)
            npc_man.add_event(ap_eventstop)
            npc_mangr = pyoscx.ManeuverGroup('AutopilotSequenceNPC'+str(i))
            npc_mangr.add_actor('npc'+str(i))
            npc_mangr.add_maneuver(npc_man)

            act.add_maneuver_group(npc_mangr)

        # create the story
        story = pyoscx.Story('mystory')
        story.add_act(act)

        ## create the storyboard
        sb = pyoscx.StoryBoard(init)
        sb.add_story(story)

        ## create the scenario
        sce = pyoscx.Scenario('cut_in','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

        return sce

if __name__ == "__main__":

    start_time = time.time()

    s = Scenario()
 
    parameters = {}

    # JSON file 
    f = open ('param_cutin.json', "r") 
  
    # Reading from file 
    data = json.loads(f.read()) 
  
    for jsonParam in data['Parameters']: 
        for value in jsonParam:
            parameters[value] = jsonParam[value]

    #convert repetirions to list of numbers for correct nember of permutations
    parameters['repetitions'] = list(range(0, parameters["repetitions"][0]))

    town = parameters["Town"][0]
    util.check_town(town)

    s.print_permutations(parameters)

    s.generate('CutIn',parameters)

    print("Process finished --- %s seconds ---" % (time.time() - start_time))

