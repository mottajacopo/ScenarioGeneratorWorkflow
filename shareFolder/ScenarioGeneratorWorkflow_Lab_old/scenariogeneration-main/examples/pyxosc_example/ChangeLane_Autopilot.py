import pyoscx   

### create catalogs
catalog = pyoscx.Catalog()

### create road
road = pyoscx.RoadNetwork(roadfile='Town04',scenegraph=" ")


### create parameters
paramdec = pyoscx.ParameterDeclarations()

###create properties

prop= pyoscx.Properties()
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
#prop= pyoscx.Properties()
#prop.add_property(name='module',value='external_control')
#contr = pyoscx.Controller('HeroAgent',prop)
#controllerAct = pyoscx.AssignControllerAction(contr)

step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

targetspeed = pyoscx.AbsoluteSpeedAction(5,step_time)
targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,30,0.5,4.7))


#egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-9.4,-152.8,0.5,1.57079632679))
egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,150,0.5,4.7))
egospeed = pyoscx.AbsoluteSpeedAction(8,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))


init.add_global_action(envAct)
#init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)
#init.add_init_action(egoname,controllerAct)
#init.add_init_action(targetname,targetspeed)
init.add_init_action(targetname,targetstart)

### create an event


#autopilot stimulation time condition
ap_starttrigger = pyoscx.ValueTrigger('StartCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
ap_eventstart = pyoscx.Event('StartAutopilot',pyoscx.Priority.overwrite)


ap_eventstart.add_trigger(ap_starttrigger)
ap_actionstart = pyoscx.ActivateControllerAction(True,True)
ap_eventstart.add_action('StartAutopilot',ap_actionstart)


stoptrigcond = pyoscx.TraveledDistanceCondition(300.0)
ap2_stoptrigger = pyoscx.EntityTrigger('EndCondition',1,pyoscx.ConditionEdge.rising,stoptrigcond,egoname)

ap3_trigcond = pyoscx.RelativeDistanceCondition(51,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)
ap3_trigger = pyoscx.EntityTrigger('distancetrigger',1,pyoscx.ConditionEdge.none,ap3_trigcond,egoname)


ap_stoptrigger = pyoscx.ValueTrigger('StopCondition',1,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(30,pyoscx.Rule.greaterThan))
ap_eventstop = pyoscx.Event('StopAutopilot',pyoscx.Priority.overwrite)
ap_eventstop.add_trigger(ap3_trigger)
ap_actionstop = pyoscx.ActivateControllerAction(False,False)
ap_eventstop.add_action('StopAutopilot',ap_actionstop)

#change lane
cl_trigcond2 = pyoscx.StoryboardElementStateCondition(pyoscx.StoryboardElementType.action,"StopAutopilot",pyoscx.StoryboardElementState.completeState)
cl_trigger2 = pyoscx.ValueTrigger('AfterStopAutopilot',2,pyoscx.ConditionEdge.rising,cl_trigcond2)

cl_trigcond = pyoscx.RelativeDistanceCondition(30,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,targetname,freespace=False)
cl_trigger = pyoscx.EntityTrigger('distancetrigger',1,pyoscx.ConditionEdge.none,cl_trigcond,egoname)
cl_event = pyoscx.Event('HeroChangesLane',pyoscx.Priority.overwrite)
cl_event.add_trigger(cl_trigger2)
sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)
cl_action = pyoscx.RelativeLaneChangeAction(-1,targetname,sin_time)
cl_event.add_action('HeroChangesLane',cl_action)

#speed

sp_trigcond2 = pyoscx.StoryboardElementStateCondition(pyoscx.StoryboardElementType.action,"StopAutopilot",pyoscx.StoryboardElementState.completeState)
sp_trigger2 = pyoscx.ValueTrigger('AfterStopAutopilot',1,pyoscx.ConditionEdge.rising,sp_trigcond2)

sp_trigcond = pyoscx.SpeedCondition(24,pyoscx.Rule.greaterThan)
sp_trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,pyoscx.ConditionEdge.none,sp_trigcond,egoname)
sp_event = pyoscx.Event('myfirstevent',pyoscx.Priority.overwrite)
sp_event.add_trigger(sp_trigger2)
sp_sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.time,5)
sp_action = pyoscx.AbsoluteSpeedAction(10,sin_time)
sp_event.add_action('newspeed',sp_action)

## create the maneuvers
#maneuver for hero 
h_man = pyoscx.Maneuver('AutopilotSequenceHero')
h_man.add_event(ap_eventstart)
h_man.add_event(ap_eventstop)
h_man.add_event(cl_event)
h_man.add_event(sp_event)

h_mangr = pyoscx.ManeuverGroup('AutopilotSequenceHero')
h_mangr.add_actor('hero')
h_mangr.add_maneuver(h_man)

#maneuver for adversary
a_man = pyoscx.Maneuver('AutopilotSequenceAdversary')
a_man.add_event(ap_eventstart)
a_man.add_event(ap_eventstop)

a_mangr = pyoscx.ManeuverGroup('AutopilotSequenceAdversary')
a_mangr.add_actor('adversary')
a_mangr.add_maneuver(a_man)

#act and stopcondition of scenario
act_starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
stoptrigcond = pyoscx.TraveledDistanceCondition(500.0)
act_stoptrigger = pyoscx.EntityTrigger('EndCondition',0,pyoscx.ConditionEdge.rising,stoptrigcond,egoname, triggeringpoint='stop')
act = pyoscx.Act('my_act',act_starttrigger,act_stoptrigger)
act.add_maneuver_group(h_mangr)
act.add_maneuver_group(a_mangr)

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

# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
sce.write_xml('ChangeLane.xosc',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
#pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')