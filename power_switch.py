from py2scad import *

defaultParams = { 
        'outerX'  : 10.0,
        'outerY'  : 15.0,
        'outerZ'  : 1.52,
        'innerX'  : 8.0,
        'innerY'  : 11.0,
        'innerZ'  : 9.0, 
        'cutoutX' : 9.2,
        'cutoutY' : 13.8, 
        }

class PowerSwitch(object):

    def __init__(self,params=defaultParams):
        self.params = params
        self.make()

    def make(self):
        outerSize = (
                self.params['outerX'],
                self.params['outerY'],
                self.params['outerZ'],
                )
        outer = Cube(size=outerSize)
        posZ = -0.5*self.params['outerZ']
        outer = Translate(outer,v=(0,0,posZ))

        innerSize = (
                self.params['innerX'],
                self.params['innerY'],
                self.params['innerZ'],
                )
        inner = Cube(size=innerSize)
        posZ = 0.5*self.params['innerZ']
        inner = Translate(inner,v=(0,0,posZ))

        self.part = Union([outer,inner])

    def getCutArray(self, panelName, panelThickness):
        if panelName == 'front':
            return self.getCutArrayFront(panelThickness)
        else:
            return None

    def getCutArrayFront(self,panelThickness):
        cutoutZ = 4*panelThickness
        cutoutSize = (
                self.params['cutoutX'],
                self.params['cutoutY'],
                cutoutZ,
                )
        cutout = Cube(size=cutoutSize)
        posZ = 0.25*cutoutZ
        cutout = Translate(cutout, v=(0,0,posZ))
        return cutout

    def __str__(self):
        return self.part.__str__()

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    includeCutArray = True
    cutArrayPanel = 'front'

    switch = PowerSwitch()
    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(switch)
    if includeCutArray:
        cutArray = switch.getCutArray(cutArrayPanel, 3.0)
        if cutArray is not None:
            prog.add(cutArray)
    prog.write('power_switch.scad')



