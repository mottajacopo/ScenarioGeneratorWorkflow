class OverrideBrakeAction(_PrivateActionType):

    def __init__(self,value, activate):
        """ initalizes the OverrideBrakeAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideBrakeAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideBrakeAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideBrakeAction',self.get_attributes())
        return element
		
----------------------------------------------------------------------------------------------------------------------------

class AssignControllerAction(_PrivateActionType):

    def __init__(self,controller):
        """ initalizes the AssignControllerAction

            Parameters
            ----------
                controller (Controller or Catalogreference): a controller to assign

        """
        if not ( isinstance(controller,Controller) or isinstance(controller,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.controller = controller

    def get_element(self):
        """ returns the elementTree of the AssignControllerAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerActiton')
        controlleraction.append(self.controller.get_element())
        

        return element
        
----------------------------------------------------------------------------------------------------------------------------

        class EnvironmentAction(_ActionType):

    def __init__(self, name, environment):
        """ initalize the EnvironmentAction

            Parameters
            ----------
                name (str): name of the action

                environment (Environment or CatalogReference): the environment to change to

        """
        self.name = name
        if not ( isinstance(environment,Environment) or isinstance(environment,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.environment = environment


    def get_attributes(self):
        """ returns the attributes of the EnvironmentAction as a dict

        """
        retdict = {}
        retdict['name'] = self.name
        return retdict

    def get_element(self):
        """ returns the elementTree of the EnvironmentAction

        """
        element = ET.Element('GlobalAction')
        envaction = ET.SubElement(element, 'EnvironmentAction')
        envaction.append(self.environment.get_element())
        
        return element
        
        
        
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerActiton')
        asscontrolleraction = ET.SubElement(controlleraction,'AssignControllerActiton')
        asscontrolleraction.append(self.controller.get_element())
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ThroAct = pyoscx.OverrideThrottleAction(value='0',activate=False).get_attributes()
