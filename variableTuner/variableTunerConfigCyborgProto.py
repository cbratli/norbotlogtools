import pygooey
password = "pwd"
variable = []
variable.append(pygooey.Variable('tunableParam.K_p', '%.4f', 0, 10, 0.001))
variable.append(pygooey.Variable('tunableParam.K_d', '%.5f', 0, 10, 0.0001))
variable.append(pygooey.Variable('tunableParam.CAR_NORMAL_VELOCITY', '%d', 0, 10000, 50))
variable.append(pygooey.Variable('wheelAngle_sp_deg', '%.2f', 0, 180, 0.5))
variable.append(pygooey.Variable('SERVO_STEERING_NOM', '%d', 0, 180, 1))
variable.append(pygooey.Variable('tunableParam.rightGain', '%.2f', 0, 10, 0.01))
variable.append(pygooey.Variable('tunableParam.leftGain', '%.2f', 0, 10, 0.01))



