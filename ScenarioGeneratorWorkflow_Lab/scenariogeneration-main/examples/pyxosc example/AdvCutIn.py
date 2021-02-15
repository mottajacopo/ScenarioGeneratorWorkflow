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
# prop= pyoscx.Properties()
# prop.add_property(name='module',value='external_control')
# contr = pyoscx.Controller('HeroAgent',prop)
# controllerAct = pyoscx.AssignControllerAction(contr)

step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

targetspeed = pyoscx.AbsoluteSpeedAction(15,step_time)
targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(-2.6,80,0.5,4.7))
#targetstart = pyoscx.TeleportAction(pyoscx.WorldPosition(190,133,0.5,0))

#egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-9.4,-152.8,0.5,1.57079632679))
egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,-80,0.5,4.7))
egospeed = pyoscx.AbsoluteSpeedAction(5,pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.distance,10))


init.add_global_action(envAct)
init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)
#init.add_init_action(egoname,controllerAct)
init.add_init_action(targetname,targetspeed)
init.add_init_action(targetname,targetstart)



### create an event

trigcond = pyoscx.RelativeDistanceCondition(8,pyoscx.Rule.lessThan, pyoscx.RelativeDistanceType.cartesianDistance,egoname,freespace=False)


trigger = pyoscx.EntityTrigger('distancetrigger',0.0,pyoscx.ConditionEdge.none,trigcond,targetname)

event = pyoscx.Event('AdvChangesLane',pyoscx.Priority.overwrite)
event.add_trigger(trigger)
sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)
action = pyoscx.RelativeLaneChangeAction(1,targetname,sin_time)
event.add_action('AdvChangesLane',action)


## create the maneuver 
man = pyoscx.Maneuver('my_maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor('adversary')
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
sce = pyoscx.Scenario('adv_cut_in','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
#pyoscx.prettyprint(sce.get_element())

# if you want to save it
sce.write_xml('AdvCutIn.xosc',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
#pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')