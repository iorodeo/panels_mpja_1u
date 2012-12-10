"""
Makes the panels expansion board

"""

from py2scad import *
import connector_bnc
import component_array

DEFAULT_PARAMS = { 
        'sideX'                : 8.0*INCH2MM,
        'sideY'                : 2*INCH2MM,
        'thickness'            : 1.75,
        'standoffHeight'       : 0.375*INCH2MM,
        'standoffRadius'       : 3.23,
        'standoffPosX'         : 3.2*INCH2MM,
        'standoffPosY'         : 0.9*INCH2MM,
        'standoffScrewRadius'  : 1.39,
        'standoffScrewHeight'  : 15,
        'connector'            : connector_bnc.Connector_BNC(),
        'connectorSpacing'     : 0.8*INCH2MM,
        'numberOfConnector'    : 10,
        }


class ExpansionPCB:

    def __init__(self,params=DEFAULT_PARAMS):
        self.params=params
        self.make()

    def make(self):
        sideX = self.params['sideX']
        sideY = self.params['sideY']
        thickness = self.params['thickness']
        standoffHeight = self.params['standoffHeight']
        standoffRadius = self.params['standoffRadius']
        standoffPosX = self.params['standoffPosX']
        standoffPosY = self.params['standoffPosY']
        standoffScrewHeight = self.params['standoffScrewHeight']
        standoffScrewRadius = self.params['standoffScrewRadius']
        numberOfConnector = self.params['numberOfConnector']
        connectorSpacing = self.params['connectorSpacing']
        connector = self.params['connector']

        PCB = Cube( size=[sideX, sideY, thickness])

        arrayParams = {
                'component' : connector,
                'spacing'   : connectorSpacing,
                'number'    : numberOfConnector,
                }

        connectorGroup = component_array.ComponentArray(arrayParams)
        posZ = 0.5*connector.params['baseZ'] + 0.5*thickness
        posY = 0.5*connector.params['baseY'] -0.5*sideY
        connectorGroup = Translate(connectorGroup, v=(0,posY,posZ))

        standoff = Cylinder(
                h=standoffHeight, 
                r1=standoffRadius,
                r2=standoffRadius
                )
        standoffList = []

        for i in (-1,1):
            for j in (-1,1):
                posZ = -(0.5*standoffHeight + 0.5*thickness)
                posX = i*standoffPosX
                posY = j*standoffPosY
                standoffTemp = Translate(standoff, v=[posX,posY,posZ])
                standoffList.append(standoffTemp)

        self.part = Union([PCB,connectorGroup]+standoffList)

    def __str__(self):
        return self.part.__str__()


#------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    pcb = ExpansionPCB()
    prog = SCAD_Prog()
    prog.fn=10
    prog.add(pcb)
    prog.write('expansion_pcb.scad')     






