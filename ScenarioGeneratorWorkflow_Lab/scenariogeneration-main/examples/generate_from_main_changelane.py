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

class Scenario(ScenarioGenerator):
    def __init__(self):
        ScenarioGenerator.__init__(self)
        self.naming = 'numerical'

    def scenario(self,**kwargs):
        
        ### create catalogs
        catalog = pyoscx.Catalog()

        ### create road
        road = pyoscx.RoadNetwork(roadfile=kwargs['Town'],scenegraph=" ")

        ### create parameters
        paramdec = pyoscx.ParameterDeclarations()

        ###create properties

        prop= pyoscx.Properties()
        #prop.add_property

        ### create vehicles

        bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
        fa = pyoscx.Axle(0.523598775598,0.8,1.68,2.98,0.4)
        ba = pyoscx.Axle(0.523598775598,0.8,1.68,0,0.4)
        ego_veh = pyoscx.Vehicle(util.get_random_vehicles(),pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)
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

        """
        for i in range(10):
            npc_veh = pyoscx.Vehicle(util.get_random_vehicles(),pyoscx.VehicleCategory.car,bb,fa,ba,69,10,10)    
            npc_veh.add_property(name='type',value='ego_vehicle')
            entities.add_scenario_object((npcname + str(i)),npc_veh)
        """

        timeofday=pyoscx.TimeOfDay(True,2020,12,11,21,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1", timeofday,weather,roadcond)

        ### create init
        init = pyoscx.Init()

        #environment
        timeofday=pyoscx.TimeOfDay(True,2020,12,11,11,52,10)
        roadcond=pyoscx.RoadCondition(1.0)
        weather=pyoscx.Weather(pyoscx.CloudState.free,1,0,1,pyoscx.PrecipitationType.dry,0,100000)
        env=pyoscx.Environment("Environment1",timeofday,weather,roadcond)
        envAct= pyoscx.EnvironmentAction("Environment1", env)

        #controller
        prop= pyoscx.Properties()
        prop.add_property(name='module',value='external_control')
        contr = pyoscx.Controller('HeroAgent',prop)
        controllerAct = pyoscx.AssignControllerAction(contr)

        step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

        targetspeed = pyoscx.AbsoluteSpeedAction(((kwargs['approachSpeed'])-5),step_time)
        targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,-80,0.5,4.7))

        egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,80,0.5,4.7))
        egospeed = pyoscx.AbsoluteSpeedAction(kwargs['approachSpeed'],pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))


        if(kwargs['randomPosition']):
            egostart, targetstart, npc_spawns = util.get_random_spawn_points(kwargs['initialOffset'],kwargs['check_lane'])

        init.add_global_action(envAct)
        init.add_init_action(egoname,egospeed)
        init.add_init_action(egoname,egostart)
        #init.add_init_action(targetname,controllerAct)

        init.add_init_action(targetname,targetspeed)
        init.add_init_action(targetname,targetstart)

        """
        for i in range(10):
            init.add_init_action((npcname + str(i)),targetspeed)
            init.add_init_action((npcname + str(i)),random.choice(npc_spawns))
            #init.add_init_action((npcname + str(i)),controllerAct)
            #init.add_init_action((npcname + str(i)),controllerAct)        
        """
        ### create an event

        trigcond = pyoscx.RelativeDistanceCondition(40,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)

        trigger = pyoscx.EntityTrigger('distancetrigger',0.0,pyoscx.ConditionEdge.none,trigcond,egoname)

        event = pyoscx.Event('HeroChangesLane',pyoscx.Priority.overwrite)
        event.add_trigger(trigger)
        sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)
        action = pyoscx.RelativeLaneChangeAction(-1,targetname,sin_time)
        event.add_action('HeroChangesLane',action)

        #actionController = pyoscx.ActivateControllerAction(True, True)

        ## create the maneuver 
        man = pyoscx.Maneuver('my_maneuver')
        man.add_event(event)

        mangr = pyoscx.ManeuverGroup('mangroup')
        mangr.add_actor('hero')
        mangr.add_maneuver(man)
        starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
        stoptrigger = pyoscx.ValueTrigger('stop_simulation',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(25,pyoscx.Rule.greaterThan),'stop')
        act = pyoscx.Act('my_act',starttrigger,stoptrigger)
        act.add_maneuver_group(mangr)

        # create the story
        #storyparam = pyoscx.ParameterDeclarations()
        #storyparam.add_parameter(pyoscx.Parameter('adversary',pyoscx.ParameterType.string,targetname))
        story = pyoscx.Story('mystory')
        story.add_act(act)

        ## create the storyboard
        
        sb = pyoscx.StoryBoard(init)
        sb.add_story(story)

        ## create the scenario
        sce = pyoscx.Scenario('change_lane','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

        return sce

if __name__ == "__main__":
    s = Scenario()
 
    parameters = {}

    # JSON file 
    f = open ('param_changelane.json', "r") 
  
    # Reading from file 
    data = json.loads(f.read()) 
  
    for jsonParam in data['Parameters']: 
        for value in jsonParam:
            parameters[value] = jsonParam[value]

    s.print_permutations(parameters)

    s.generate('ChangeLane',parameters)


