import math

steel_yield = 235 #/ 1.1  # MPa
E = 210000 #MPa
moment_inertia = {"MQ-41-L": 58800,"MQ-41": 58800, "MQ-41/3": 77000, "MQ-52": 124200, "MQ-72": 309900, "MQ-41 D": 255700}  # mm4
permtion_modulus = {"MQ-41-L": 2670,"MQ-41": 2710, "MQ-41/3": 3490, "MQ-52": 4550, "MQ-72": 8280, "MQ-41 D": 6190}  # mm3
permissable_moment = {key: value * steel_yield / 1000000 for (key, value) in permtion_modulus.items()}  # kNm

class Beam():
    def __init__(self, type, span):
        self.type = type
        self.moment_of_inertia = moment_inertia[type]
        self.permissable_moment = permissable_moment[type]
        self.deformation_limit = span/200
        self.span = span

    def deflection_perpendicular(self, depth, self_weight, vertical_wind):
        a = (self.span - depth) / 2 #m
        delta_self_weight = (self_weight * a) / (24*E*1000*self.moment_of_inertia/(1000**4))*(3*self.span**2 - 4*a**2) #m
        #####
        b = self.span - a
        x = math.sqrt((self.span**2 - b**2)/3)
        x2 = self.span - x
        #delta_self_weight = self_weight * b * x/(6*self.span*E*1000*self.moment_of_inertia/(1000**4))*(self.span/b*(x-a)**3+(self.span**2-b**2)*x-x**3)
        delta_wind_1 = -(vertical_wind * b * x/(6*self.span*E*1000*self.moment_of_inertia/(1000**4))*(self.span/b*(x-a)**3+(self.span**2-b**2)*x-x**3))
        delta_wind_2 = vertical_wind * b * x/(6*self.span*E*1000*self.moment_of_inertia/(1000**4))*(self.span**2-x**2-b**2)
        delta_wind = delta_wind_1 + delta_wind_2
        delta = (delta_self_weight + delta_wind)*1000 #mm
        return delta

    def deflection_parallel(self, load):
        delta = 5/384 * load * self.span**4/(E*1000*self.moment_of_inertia/(1000**4)) * 1000 #mm
        return delta
    
    def deflection_continous_3(self, load):
        delta = (0.00521 * load * self.span**4) / (E*1000*self.moment_of_inertia/(1000**4)) * 1000 #mm
        return delta
    
    def deflection_continous_4(self, load):
        delta = (0.00677 * load * self.span**4) / (E*1000*self.moment_of_inertia/(1000**4)) * 1000 #mm
        return delta