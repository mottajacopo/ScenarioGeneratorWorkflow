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
            egostart, targetstart, npc_spawns = util.get_random_spawn_points( 0,kwargs['check_lane'])
        else:
            #put a default position here
            print("default position not setted")
            exit
        
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

        ## create entities

        egoname = 'hero'
        npcname = 'npc'

        entities = pyoscx.Entities()
        entities.add_scenario_object(egoname,ego_veh)

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
        timeofday=pyoscx.TimeOfDay(True,2020,12,11,11,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1",timeofday,weather,roadcond)
        envAct= pyoscx.EnvironmentAction("Environment1", env)

        #default egostart if random position is false
        #egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,80,0.5,4.7))


        ### create init
        init = pyoscx.Init()

        init.add_global_action(envAct)
        init.add_init_action(egoname,egostart)

        #init npcs start positions
        npcstart_list = []
        for i in range(npc_number):
            spawn = random.choice(npc_spawns)
            
            while([spawn.position.x, spawn.position.y] in npcstart_list):
                spawn = random.choice(npc_spawns)
            
            npcstart_list.append([spawn.position.x, spawn.position.y])
            
            init.add_init_action((npcname + str(i)),spawn)
            
        #Create events
        #autopilot
        ap_starttrigger = pyoscx.ValueTrigger('StartCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        ap_eventstart = pyoscx.Event('StartAutopilot',pyoscx.Priority.overwrite)
        ap_eventstart.add_trigger(ap_starttrigger)
        ap_actionstart = pyoscx.ActivateControllerAction(False,True)
        ap_eventstart.add_action('StartAutopilot',ap_actionstart)

        ap_stoptrigger = pyoscx.ValueTrigger('StopCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(29,pyoscx.Rule.greaterThan))
        ap_eventstop = pyoscx.Event('StopAutopilot',pyoscx.Priority.overwrite)
        ap_eventstop.add_trigger(ap_stoptrigger)
        ap_actionstop = pyoscx.ActivateControllerAction(False,False)
        ap_eventstop.add_action('StopAutopilot',ap_actionstop)

        ## create the maneuvers
        #maneuver for hero 
        h_man = pyoscx.Maneuver('AutopilotSequenceHero')
        h_man.add_event(ap_eventstart)
        h_man.add_event(ap_eventstop)

        h_mangr = pyoscx.ManeuverGroup('AutopilotSequenceHero')
        h_mangr.add_actor('hero')
        h_mangr.add_maneuver(h_man)

        
        act_starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        #stoptrigcond = pyoscx.TraveledDistanceCondition(200.0)
        #act_stoptrigger = pyoscx.EntityTrigger('EndCondition',0,pyoscx.ConditionEdge.rising,stoptrigcond,egoname, triggeringpoint='stop')
        act_stoptrigger = pyoscx.ValueTrigger('StopCondition',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(10,pyoscx.Rule.greaterThan), triggeringpoint='stop')
        act = pyoscx.Act('my_act',act_starttrigger,act_stoptrigger)

        act.add_maneuver_group(h_mangr)

        #maneuver for npcs 
        for i in range(npc_number):
            npc_man = pyoscx.Maneuver('AutopilotSequenceNPC'+str(i))
            npc_man.add_event(ap_eventstart)
            #npc_man.add_event(ap_eventstop)
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
        sce = pyoscx.Scenario('freeride','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

        return sce

if __name__ == "__main__":

    start_time = time.time()

    s = Scenario()
 
    parameters = {}

    # JSON file 
    f = open ('param_freeride.json', "r") 
  
    # Reading from file 
    data = json.loads(f.read()) 
  
    #parse json file parameters
    for jsonParam in data['Parameters']: 
        for value in jsonParam:
            parameters[value] = jsonParam[value]
            
    #convert repetirions to list of numbers for correct nember of permutations
    parameters['repetitions'] = list(range(0, parameters["repetitions"][0]))

    s.print_permutations(parameters)
    
    s.generate('FreeRide',parameters)

    print("Process finished --- %s seconds ---" % (time.time() - start_time))


