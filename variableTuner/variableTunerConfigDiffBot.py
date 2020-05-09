import pygooey
password = "pwd"
variable = []
variable.append(pygooey.Variable('tunableParam.K_p', '%.4f', 0, 10, 0.001))
variable.append(pygooey.Variable('tunableParam.K_carSpeed_p', '%.4f', 0, 10000, 0.0001))
variable.append(pygooey.Variable('angle_sp_deg', '%.1f', 0, 180, 5))
variable.append(pygooey.Variable('tunableParam.K_ps', '%.4f', 0, 180, 0.0001))
variable.append(pygooey.Variable('tunableParam.wallOffsetRight', '%d', 0, 100, 5))
variable.append(pygooey.Variable('tunableParam.K_carSpeed_p', '%.5f', 0, 100, 0.00001))
variable.append(pygooey.Variable('tunableParam.controllerType', '%d', 0, 100, 1))
variable.append(pygooey.Variable('tunableParam.v_car_sp', '%.1f', 0, 10000, 5))





