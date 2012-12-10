"""
Makes a single PCB Mount BNC connector. 

Note, measured part sizes - oversized to fit. Units are in mm.
"""
import sys
from py2scad import *


DEFAULT_PARAMS = { 
        'baseX'        : 14.7,
        'baseY'        : 13.71,
        'baseZ'        : 15.2,
        'threadHeight' : 9.2,
        'threadRadius' : 6.7,
        'connHeight'   : 12.05,
        'connRadius'   : 4.82,
        'notchHeight'  : 2.3,
        'notchWidth'   : 8,
        'notchLength'  : 9.6,
        }


class Connector_BNC(object):

    def __init__(self,params=DEFAULT_PARAMS):
        self.params = params
        self.make()

    def make(self):

        baseX = self.params['baseX']
        baseY = self.params['baseY']
        baseZ = self.params['baseZ']
        threadHeight = self.params['threadHeight']
        threadRadius = self.params['threadRadius']
        connHeight = self.params['connHeight']
        connRadius = self.params['connRadius']
        notchHeight = self.params['notchHeight']
        notchWidth = self.params['notchWidth']
        notchLength = self.params['notchLength']

        base = Cube(size=(baseX,baseY,baseZ))
        thread = Cylinder(h=threadHeight, r1=threadRadius, r2=threadRadius)
        thread =  Rotate(thread, a = 90, v=[1,0,0])
        thread = Translate(thread, v=[0,-(0.5*baseY + 0.5*threadHeight),0])
        end = Cylinder(h=connHeight,r1=connRadius,r2=connRadius)
        end =  Rotate(end, a = 90, v=[1,0,0])
        end = Translate(end, v=[0,-(0.5*baseY + 1*threadHeight + 0.5*connHeight),0])
        notch = Cube(size=[notchWidth, notchLength, notchHeight]) 
        notch = Translate(notch, v=[0,-(0.5*baseY + 0.5*threadHeight),0.5*baseZ - 0.5*2.3])
        thread = Difference([thread,notch])
        self.part = Union([base,thread,end]);

    def __str__(self):
        return self.part.__str__()



# -----------------------------------------------------------------------------
if __name__ == "__main__":

    conn = Connector_BNC()
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(conn)
    prog.write('connector_bnc.scad')     

