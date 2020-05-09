# The commands is in the format: (command, valueType, description)
# where valueType currently is only %s - sring.
commands = []
commands.append(('run',None,'Start car'))
commands.append(('stop',None,'Stop car'))

commands.append(('load',None,'Load parameters'))
commands.append(('save',None,'Save parameters'))

commands.append(('c1+',None,'Increase speed'))
commands.append(('c1-',None,'Decrease speed'))

commands.append(('a',None,'Increase Kp by 0.001'))
commands.append(('s',None,'Decrease Kp by 0.001'))

commands.append(('z',None,'Increase Kd by 0.0001'))
commands.append(('x',None,'Decrease Kd by 0.0001'))

commands.append(('o',None,'Toggle steering'))
commands.append(('motor',None,'Toggle motor'))