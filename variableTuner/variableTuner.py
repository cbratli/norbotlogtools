import sys, os
sys.path.insert(0, os.path.abspath('..'))

import pygooey
import pygame as pg

import variableTunerConfig as config

import configuration.messageBrokerConfig as broker

import mapCreator.mqttDatapump as mqttDatapump

class VariableTuner:

    def __init__(self, msgPublisher, topic):
        self.msgPublisher = msgPublisher
        
        self.topic = topic
        self.password = config.password

    def sendValue(self, command):
        """ Sends the value via MQTT """
        self.msgPublisher.publishMessage(self.topic, command)
        

    def textbox_callback(self, id, final):
        print('enter pressed, textbox contains {}'.format(final))
        print('id {}'.format(id.name))
        self.createVariableSetterMessage(id.name, id.displayFormat % (float(final)) ) 
        
    def button_callback(self, button,returnObject):
        print( "You pressed the button")
        print('button pressed, textbox contains {}'.format(returnObject.final))
        print('button pressed, textbox contains {}'.format(returnObject.id.name))
        print(returnObject.id.displayFormat)
        varAsString = returnObject.id.displayFormat % (float(returnObject.final))
        self.createVariableSetterMessage(returnObject.id.name, returnObject.id.displayFormat % float(returnObject.final) ) 

    def button_callback_increment(self, button,returnObject):
        print('Increment pressed, textbox contains {}'.format(button.id.buffer))
        print(' --- increment pressed, textbox contains {}'.format(returnObject.id.name))
        self.createVariableSetterMessage(returnObject.id.name, self.getIncrementedValue(button, returnObject.id.increment) ) 
        

    def button_callback_decrement(self, button,returnObject):
        print('Decrement pressed, textbox contains {}'.format(returnObject.final))
        print(' --- decrement pressed, textbox contains {}'.format(returnObject.id.name))
        print(' --- decrement pressed, textbox contains {%f}' % returnObject.id.increment)
        self.createVariableSetterMessage(returnObject.id.name, self.getIncrementedValue(button, -returnObject.id.increment) ) 

    def getIncrementedValue(self, button, increment):
        valueAsString = button.id.buffer
        print(valueAsString)
        val = float(valueAsString)
        print(increment)
        
        newValue = float(valueAsString) + float(increment)
        return button.id.id.displayFormat % (newValue)
       
    
    def createVariableSetterMessage(self, variable, newValue):
        """The variable messsage looks like
            :pwd:variable:newValue  
            
            Where:
                pwd : A password that is one or more characters in length. The password is to protect the car so others cant control variables.
                variable: The variable name. For instance "K_p"
                newValue: is the new value. 
                Example: 
                    :pwd:K_p:1.23
        """
        
        command = ":%s:%s:%s" % (self.password, variable, newValue)
        print("Sending command:")
        print(command)
        self.sendValue(command)
    
    
    def mainLoop(self):
        pg.init()
        screen = pg.display.set_mode((600,400))
        screen_rect = screen.get_rect()
        done = False
        widgets = []

    
        #see all settings help(pygooey.TextBox.__init__)
        entry_settings = {
            "inactive_on_enter" : False,
            'active':False
        }

        #see all settings help(pygooey.Button.__init__)
        btn_settings = {
            "clicked_font_color" : (0,0,0),
            "hover_font_color"   : (205,195, 100),
            'font'               : pg.font.Font(None,16),
            'font_color'         : (255,255,255),
            'border_color'       : (0,0,0),
        }

        varDisplays = []
        valueDisplays = []
        yBias = 0
        for v in config.variable:
            entry = pygooey.TextBox(rect=(100,10+yBias,100,30), command=self.textbox_callback, **entry_settings)
            entry.id = v
            widgets.append(entry)
            btn = pygooey.Button(rect=(10,10+yBias,90,30), command=self.button_callback,returnObject=entry, text='Set value', **btn_settings)
            widgets.append(btn)
            
            display = pygooey.TextBox(rect=(210,10+yBias,130,30), command=self.textbox_callback, **entry_settings)
            display.disabled = True
            display.id = v
            display.color = pg.Color("gray")
            widgets.append(display)    
            varDisplays.append(display)

            display = pygooey.TextBox(rect=(345,10+yBias,100,30), command=self.textbox_callback, **entry_settings)
            display.disabled = True
            display.id = v
            display.color = pg.Color("gray")
            entry.display = display
            widgets.append(display)    
            valueDisplays.append(display)

            btn = pygooey.Button(rect=(450,10+yBias,20,15), command=self.button_callback_increment,returnObject=entry, text='+', **btn_settings)
            btn.id = display
            widgets.append(btn)
            btn = pygooey.Button(rect=(450,10+yBias+15,20,15), command=self.button_callback_decrement,returnObject=entry, text='-', **btn_settings)
            btn.id = display
            widgets.append(btn)

            yBias +=40
            
            
        dataload = mqttDatapump.MqttDatapump()
        dataload.startDatapump()

        # Send  GET_VARIABLE_VALUES
        self.createVariableSetterMessage("GET_VARIABLE_VALUES", 0)
        
        

        data = {}
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    done = True
                for w in widgets:
                    w.get_event(event)
                    
            for disp in varDisplays:        
                disp.buffer = ("%s" % disp.id.name)
            
            while dataload.getDataLength() > 0:
                data = dataload.getData()
                for disp in valueDisplays:        
                    if disp.id.name in data.keys():
                        #disp.buffer =  disp.id.displayFormat
                        disp.buffer = (disp.id.displayFormat % data[disp.id.name])
            
            for w in widgets:
                w.update()
                w.draw(screen)
            pg.display.update()

if __name__ == '__main__':
    vs = VariableTuner(broker.msgPublisher, broker.robotInputQueue)
    print("Sending to: %s" % broker.robotInputQueue)
    vs.mainLoop()
    