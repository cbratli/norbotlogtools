# The commands is in the format: (command, valueType, description)
# where valueType currently is only %s - sring.
commands = []
commands.append(('run',None,'Start car'))
commands.append(('stop',None,'Stop car'))

commands.append(('wait',None,'car waiting mode'))
commands.append(('manual',None,'car manual mode'))

commands.append(('c1load',None,'Load parameters'))
commands.append(('c1save',None,'Save parameters'))

commands.append(('c1+',None,'Increase speed'))
commands.append(('c1-',None,'Decrease speed'))

commands.append(('a',None,'Increase Kp by 0.001'))
commands.append(('s',None,'Decrease Kp by 0.001'))

commands.append(('z',None,'Increase Kd by 0.0001'))
commands.append(('x',None,'Decrease Kd by 0.0001'))

commands.append(('steeringOn',None,'Steering On'))
commands.append(('steeringOff',None,'Steering Off'))

commands.append(('motorOn',None,'Motor on'))
commands.append(('motorOff',None,'Motor off'))

#commands.append((':pwd:K_p:1.3',None,'Send K_p var'))
#commands.append((':pwd:tunableParam.K_p:1.3',None,'Send TunableParam.K_p'))

commands.append(('printLogOn',None,'printLogOn'))
commands.append(('printLogOff',None,'printLogOff'))

commands.append((':pwd:GET_VARIABLE_VALUES:0',None,'Get tunable values'))
