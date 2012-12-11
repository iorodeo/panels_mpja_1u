"""
Makes an LED component - Digikey part 516-1757-ND
"""

import sys
import scipy
from py2scad import *

defaultParamsLed = {
    'baseSize'    :  (5.65, 9.1, 7.35),
    'lensRadius'  :  2.0,
    }

defaultParamsLedArray = {
        'number' : 3,
        'space'  :  0.00,
        'led'    : defaultParamsLed,
        }

class Led(object):

    def __init__(self,params=defaultParamsLed):
        self.params = params
        self.make()

    def make(self):
        base = Cube(size=self.params['baseSize'])
        lens = Sphere(r=self.params['lensRadius'])
        v = self.getLensTranslation()
        lens = Translate(lens, v=v)
        self.part = Union([base, lens]);

    def getLensTranslation(self):
        return [0, -0.5*self.params['baseSize'][1], 0]

    def __str__(self):
        return self.part.__str__()


class LedArray(object):

    def __init__(self,params=defaultParamsLedArray):
        self.params = params
        self.make()

    def make(self):
        led = Led(self.params['led'])
        ledList = []
        for v in self.getLedTranslationList():
            ledNew = Translate(led, v=v)
            ledList.append(ledNew)
        self.part = Union(ledList)

    def getLedTranslationList(self):
        number = self.params['number']
        space = self.params['space']
        ledX = self.params['led']['baseSize'][0]
        transList = []
        for i in range(0,number):
            x=i*(ledX + space) - 0.5*(number-1)*(ledX + space)
            transList.append([x,0,0])
        return transList

    def __str__(self):
        return self.part.__str__()

# -----------------------------------------------------------------------------

if __name__ == "__main__":

    part = LedArray()
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(part)
    prog.write('led_array.scad')     

