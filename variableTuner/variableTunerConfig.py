import pygooey
password = "pwd"
variable = []
variable.append(pygooey.Variable('K_p', '%.2f', 0, 10, 0.01))
variable.append(pygooey.Variable('Kp_goToAngle', '%.3f', 0, 10000, 0.001))
variable.append(pygooey.Variable('PWM_SPEED', '%d', 0, 255, 5))
variable.append(pygooey.Variable('CRASH_DISTANCE', '%d', 0, 180, 1))






