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

## create entities

egoname = 'hero'

entities = pyoscx.Entities()

entities.add_scenario_object(egoname,ego_veh)

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
prop.add_property(name='ControllerCatalog',value='ExternalControl')
contr = pyoscx.Controller('HeroAgent',prop)
controllerAct = pyoscx.AssignControllerAction(contr)

egostart = pyoscx.TeleportAction(pyoscx.WorldPosition(-8.6,80,0.5,4.7))
step_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.step,pyoscx.DynamicsDimension.time,1)

egospeed = pyoscx.AbsoluteSpeedAction(15,step_time)

init.add_global_action(envAct)

init.add_init_action(egoname,egostart)
init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,controllerAct)

### create an event

starttrigger = pyoscx.ValueTrigger('starttrigger',0,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))

#trigger = pyoscx.EntityTrigger('distancetrigger',0.0,pyoscx.ConditionEdge.none,starttrigger,egoname)

event = pyoscx.Event('StartEvent',pyoscx.Priority.overwrite)
event.add_trigger(starttrigger)
#sin_time = pyoscx.TransitionDynamics(pyoscx.DynamicsShapes.linear,pyoscx.DynamicsDimension.distance,25)
action = pyoscx.ActivateControllerAction(True,True)
event.add_action('StartEvent',action)

## create the maneuver 
man = pyoscx.Maneuver('my_maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor('hero')
mangr.add_maneuver(man)
starttrigger = pyoscx.ValueTrigger('starttrigger',50,pyoscx.ConditionEdge.rising,pyoscx.SimulationTimeCondition(0,pyoscx.Rule.greaterThan))
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
sce = pyoscx.Scenario('freeride','Bonora_Motta',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)

# display the scenario
pyoscx.prettyprint(sce.get_element())

# if you want to save it
sce.write_xml('Freeride.xosc',True)

# if you have esmini downloaded and want to see the scenario (add path to esmini as second argument)
#pyoscx.esminiRunner(sce,esminipath='/home/mander76/local/scenario_creation/esmini')