"""
Makes a minipcb

"""
import sys
import scipy
from py2scad import *

defaultParams = { 
        'x'                 : 1*INCH2MM,
        'y'                 : 1.4*INCH2MM,
        'thickness'         : 1.75,
        'holePosX'          : 0.4*INCH2MM,
        'holePosY'          : 0.6*INCH2MM,
        'holeRadius'        : 0.060*INCH2MM,
        'tapHoleRadius'     : 0.044*INCH2MM,
        'cutoutX'           : 0.5*INCH2MM,
        'cutoutY'           : 1.325*INCH2MM,
        'standoffHeight'    : 0.125*INCH2MM,
        'standoffRadius'    : 0.5*0.25*INCH2MM,
        }

class ProgrammerPCB(object):

    def __init__(self,params=defaultParams):
        self.params = params
        self.make()

    def make(self):
        x = self.params['x']
        y = self.params['y']
        thickness = self.params['thickness']
        holePosX = self.params['holePosX']
        holePosY = self.params['holePosY']
        holeRadius = self.params['holeRadius']

        holeList = []
        self.holePosList = []
        for i in (-1,1):
            for j in (-1,1):
                posX = i*holePosX
                posY = j*holePosY
                hole = (posX, posY, 2*holeRadius)
                holeList.append(hole)
                self.holePosList.append((posX,posY))

        pcbSize = x,y,thickness
        pcb = plate_w_holes(x,y,thickness,holes=holeList)

        standoffHeight = self.params['standoffHeight']
        standoffRadius = self.params['standoffRadius']
        standoff = Cylinder(
                h  = standoffHeight, 
                r1 = standoffRadius, 
                r2 = standoffRadius
                )
        standoffCut = Cylinder(
                h = 2*standoffHeight,
                r1 = holeRadius, 
                r2 = holeRadius,
                )
        standoff = Difference([standoff, standoffCut])

        standoffList = []
        posZ = 0.5*standoffHeight + 0.5*thickness
        for posX, posY in self.holePosList:
            standoffList.append(Translate(standoff,v=(posX,posY,posZ)))

        self.part = Union([pcb] + standoffList)

    def getCutArray(self,panelName,panelThickness):
        if panelName == 'front':
            cutArray = self.getCutArrayFront(panelThickness)
        elif panelName == 'back':
            cutArray = None
        elif panelName == 'bottom':
            cutArray = None
        else:
            raise ValueError, 'unkown panel {0}'.format(panelName)
        return cutArray

    def getCutArrayFront(self,panelThickness):

        cutoutX = self.params['cutoutX']
        cutoutY = self.params['cutoutY']
        thickness = self.params['thickness']
        standoffHeight = self.params['standoffHeight']
        tapHoleRadius = self.params['tapHoleRadius']

        cutoutZ = standoffHeight + 2*panelThickness 
        cutoutSize = cutoutX, cutoutY, cutoutZ
        cutout = Cube(size=cutoutSize)

        cutoutPosZ = 0.5*cutoutZ + 0.5*thickness
        cutout = Translate(cutout, v=[0,0,cutoutPosZ]) 

        tapHole = Cylinder(h=cutoutZ, r1=tapHoleRadius, r2=tapHoleRadius)
        tapHoleList = []
        for posX, posY in self.holePosList:
            tapHoleList.append(Translate(tapHole,v=(posX,posY,cutoutPosZ)))

        cutArray = Union([cutout] + tapHoleList)
        return cutArray 

    def __str__(self):
        return self.part.__str__()


# -----------------------------------------------------------------------------
if __name__ == "__main__":

    panelThickness = 3.0
    pcb = ProgrammerPCB()
    cutArray = pcb.getCutArray('front', panelThickness)
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(pcb)
    prog.add(cutArray)
    prog.write('programmer_pcb.scad')     

