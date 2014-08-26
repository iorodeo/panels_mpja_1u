from py2scad import *

defaultParams = { 
        'outerShaftDiameter'  :  0.6*INCH2MM,
        'innerShaftDiameter'  :  0.4*INCH2MM,
        'outerShaftLength'    :  0.25*INCH2MM,
        'innerShaftLength'    :  0.25*INCH2MM,
        'mountHoleDiameter'   : 0.437*INCH2MM,
        }

class DCJack(object):

    def __init__(self,params=defaultParams):
        self.params = params
        self.make()

    def make(self):
        outerShaft = Cylinder(
                h  = self.params['outerShaftLength'],
                r1 = 0.5*self.params['outerShaftDiameter'],
                r2 = 0.5*self.params['outerShaftDiameter']
                )
        innerShaft = Cylinder(
                h  = self.params['innerShaftLength'],
                r1 = 0.5*self.params['innerShaftDiameter'],
                r2 = 0.5*self.params['innerShaftDiameter']
                )
        posZ = -0.5*self.params['outerShaftLength']
        outerShaft = Translate(outerShaft,v=(0,0,posZ))
        posZ = 0.5*self.params['innerShaftLength']
        innerShaft = Translate(innerShaft,v=(0,0,posZ))
        self.part = Union([outerShaft, innerShaft])

    def getCutArray(self,panelName, panelThickness):
        if panelName == 'back':
            return self.getCutArrayBack(panelThickness)
        else:
            return None

    def getCutArrayBack(self,panelThickness):
        cutHeight = 4*panelThickness 
        cutCylinder = Cylinder(
                h  = cutHeight,
                r1 = 0.5*self.params['mountHoleDiameter'],
                r2 = 0.5*self.params['mountHoleDiameter']
                )
        posZ = 0.25*cutHeight
        cutCylinder = Translate(cutCylinder,v=(0,0,posZ))
        return cutCylinder

    def __str__(self):
        return self.part.__str__()

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    includeCutArray = True
    cutArrayPanel = 'back'

    jack = DCJack()
    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(jack)
    if includeCutArray:
        cutArray = jack.getCutArray(cutArrayPanel,3.0)
        if cutArray is not None:
            prog.add(cutArray)
    prog.write('dc_jack.scad')
