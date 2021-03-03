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
import util 
import time

class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.naming = 'numerical'

    def scenario(self,**kwargs):

        #get random position for ego, target and npcs
        if(kwargs['randomPosition']):
            egostart, targetstart, npc_spawns = util.get_random_spawn_points( kwargs['initialOffset'],kwargs['check_lane'])
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
        bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
        fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
        ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
        other_veh = pyoscx.Vehicle(util.get_random_vehicles(),pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)    
        other_veh.add_property(name='type',value='ego_vehicle')

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
            npc_veh.add_property(name='type',value='other_vehicle')
            entities.add_scenario_object((npcname + str(i)),npc_veh)         


        ### create init
        init = pyoscx.Init()

        #environment
        timeofday=pyoscx.TimeOfDay(True,2020,12,11,15,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1",timeofday,weather,roadcond)
        envAct= pyoscx.EnvironmentAction("Environment1", env)


        #targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,-80,0.5,4.7))
        #step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)
        #targetspeed = pyoscx.AbsoluteSpeedAction(((kwargs['approachSpeed'])-5),step_time)

        #egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,80,0.5,4.7))
        #egospeed = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed'],pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))


        init.add_global_action(envAct)
        #init.add_init_action(egoname,egospeed)
        init.add_init_action(egoname,egostart)

        #init.add_init_action(targetname,targetspeed)
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

        #speed ego
        sp_starttrigger = pyoscx.ValueTrigger('StartCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))

        sp_event = pyoscx.Event('myfirstevent',pyoscx.Priority.overwrite)
        sp_event.add_trigger(sp_starttrigger)
        sp_sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,5)
        sp_action = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed'],sp_sin_time)
        sp_event.add_action('newspeed',sp_action)

        #speed adversary
        spa_starttrigger = pyoscx.ValueTrigger('StartCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))

        spa_event = pyoscx.Event('StartSpeedAdv',pyoscx.Priority.overwrite)
        spa_event.add_trigger(spa_starttrigger)
        spa_sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,5)
        spa_action = pyoscx.AbsoluteSpeedAction(2,spa_sin_time)
        spa_event.add_action('newspeed',spa_action)       

        #change lane
        cl_trigcond = pyoscx.RelativeDistanceCondition(30,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)
        cl_trigger = pyoscx.EntityTrigger('distancetrigger',1,pyoscx.ConditionEdge.none,cl_trigcond,egoname)

        cl_event = pyoscx.Event('HeroChangesLane',pyoscx.Priority.overwrite)
        cl_event.add_trigger(cl_trigger)
        sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)
        cl_action = pyoscx.RelativeLaneChangeAction(-1,targetname,sin_time)
        cl_event.add_action('HeroChangesLane',cl_action)


        #autopilot adevrsary
        apa_trigcond = pyoscx.TraveledDistanceCondition(20.0)
        apa_starttrigger = pyoscx.EntityTrigger('StartAutopilot',0,pyoscx.ConditionEdge.rising,apa_trigcond,targetname)
        apa_eventstart = pyoscx.Event('StartAutopilot',pyoscx.Priority.overwrite)
        apa_eventstart.add_trigger(apa_starttrigger)
        apa_actionstart = pyoscx.ActivateControllerAction(False,True)
        apa_eventstart.add_action('StartAutopilot',apa_actionstart)

        #autopilot hero
        aph_trigcond = pyoscx.RelativeDistanceCondition(5,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)
        aph_starttrigger = pyoscx.EntityTrigger('distancetrigger',1,pyoscx.ConditionEdge.none,aph_trigcond,egoname)
        aph_eventstart = pyoscx.Event('StartAutopilot',pyoscx.Priority.overwrite)
        aph_eventstart.add_trigger(aph_starttrigger)
        aph_actionstart = pyoscx.ActivateControllerAction(False,True)
        aph_eventstart.add_action('StartAutopilot',aph_actionstart)

        #autopilot npc
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


        ## create the maneuvers
        #maneuver for hero 
        h_man = pyoscx.Maneuver('AutopilotSequenceHero')
        h_man.add_event(sp_event)
        h_man.add_event(cl_event)
        h_man.add_event(aph_eventstart)     
        h_man.add_event(ap_eventstop)

        h_mangr = pyoscx.ManeuverGroup('AutopilotSequenceHero')
        h_mangr.add_actor('hero')
        h_mangr.add_maneuver(h_man)

        #maneuver for adversary
        a_man = pyoscx.Maneuver('AutopilotSequenceAdversary')
        a_man.add_event(spa_event)
        a_man.add_event(apa_eventstart)
        a_man.add_event(ap_eventstop)

        a_mangr = pyoscx.ManeuverGroup('AutopilotSequenceAdversary')
        a_mangr.add_actor('adversary')
        a_mangr.add_maneuver(a_man)

        #act and stopcondition of scenario
        act_starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        act_stoptrigger = pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(20,pyoscx.Rule.greaterThan),'stop')
        act = pyoscx.Act('my_act',act_starttrigger,act_stoptrigger)

        act.add_maneuver_group(h_mangr)
        act.add_maneuver_group(a_mangr)

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
        sce = pyoscx.Scenario('change_lane','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

        return sce

if __name__ == "__main__":

    start_time = time.time()

    s = Scenario()
 
    parameters = {}

    # JSON file 
    f = open ('param_changelane.json', "r") 
  
    # Reading from file 
    data = json.loads(f.read()) 
  
    for jsonParam in data['Parameters']: 
        for value in jsonParam:
            parameters[value] = jsonParam[value]

    #convert repetirions to list of numbers for correct nember of permutations
    parameters['repetitions'] = list(range(0, parameters["repetitions"][0]))

    s.print_permutations(parameters)

    s.generate('ChangeLane',parameters)

    print("Process finished --- %s seconds ---" % (time.time() - start_time))

