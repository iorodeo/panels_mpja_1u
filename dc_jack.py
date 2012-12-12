from py2scad import *

defaultParams = { 
        'holeDiameter'  :  0.5*0.437*INCH2MM,
        }


class DCJack(object):

    def __init__(self,params=defaultParams):
        self.params = params

    def __str__(self):
        return self.part.__str__()
