"""
Makes the panels expansion board

"""

from py2scad import *
import connector_bnc
import component_array

standoffPosList = [
        ( 3.2*INCH2MM,  0.9*INCH2MM),
        (-3.2*INCH2MM,  0.9*INCH2MM),
        (-2.6*INCH2MM, -0.3501*INCH2MM),
        ( 3.0*INCH2MM, -0.3501*INCH2MM),
        ]

defaultParams = { 
        'sideX'                : 8.0*INCH2MM,
        'sideY'                : 2.0*INCH2MM,
        'thickness'            : 1.75,
        'standoffHeight'       : 0.375*INCH2MM,
        'standoffRadius'       : 3.23,
        'standoffPosX'         : 3.2*INCH2MM,
        'standoffPosY'         : 0.9*INCH2MM,
        'standoffPosList'      : standoffPosList,
        'standoffScrewRadius'  : 1.39,
        'standoffScrewHeight'  : 15,
        'connector'            : connector_bnc.Connector_BNC(),
        'connectorSpacing'     : 0.8*INCH2MM,
        'numberOfConnector'    : 10,
        'clearance'            :  0.625,
        }


class ExpansionPCB:

    def __init__(self,params=defaultParams):
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
        connector = self.params['connector']

        PCB = Cube( size=[sideX, sideY, thickness])

        arrayParams = self.getConnectorArrayParams()
        connectorArray = component_array.ComponentArray(arrayParams)
        vTrans = self.getConnectorArrayTranslation()
        connectorArray = Translate(connectorArray, v=vTrans)

        standoff = Cylinder(
                h=standoffHeight, 
                r1=standoffRadius,
                r2=standoffRadius
                )
        standoffList = []
        self.standoffTransList = []
        posZ = -(0.5*standoffHeight + 0.5*thickness)
        for posX, posY in self.params['standoffPosList']: 
            v = posX, posY, posZ
            standoffTemp = Translate(standoff, v=v)
            standoffList.append(standoffTemp)
            self.standoffTransList.append(v)

        self.part = Union([PCB,connectorArray]+standoffList)

    def getConnectorArrayParams(self):
        arrayParams = {
                'component' : self.params['connector'],
                'spacing'   : self.params['connectorSpacing'],
                'number'    : self.params['numberOfConnector'],
                }
        return arrayParams

    def getConnectorArrayTranslation(self):
        connector = self.params['connector']
        posY = 0.5*connector.params['baseY'] -0.5*self.params['sideY']
        posZ = 0.5*connector.params['baseZ'] + 0.5*self.params['thickness']
        return 0,posY,posZ

    def getCutArray(self,panelName,panelThickness):
        if panelName == 'front':
            cutArray = self.getCutArrayFront(panelThickness)
        elif panelName == 'back':
            cutArray = None
        elif panelName == 'bottom':
            cutArray = self.getCutArrayBottom(panelThickness)
        else:
            raise ValueError, 'uknown panel {0}'.format(panelName)
        return cutArray

    def getCutArrayFront(self,panelThickness):
        connector= self.params['connector']
        threadRadius = connector.params['threadRadius']
        thruHoleRadius = threadRadius + self.params['clearance']
        threadHeight = connector.params['threadHeight']
        cutCylinderHeight = max([2*panelThickness, 2*threadHeight])

        pcbThickness = self.params['thickness']
        pcbSideY = self.params['sideY']

        # Create cut cylinder for bnc connectors
        cutCylinder = Cylinder(
            h = cutCylinderHeight,
            r1 = thruHoleRadius,
            r2 = thruHoleRadius
            )

        aRot, vRot = connector.getThreadRotation()
        cutCylinder = Rotate(cutCylinder,a=aRot,v=vRot)
        vTrans = connector.getThreadTranslation()
        cutCylinder = Translate(cutCylinder, v=vTrans)

        # Create array of cut cylinders
        arrayParams = self.getConnectorArrayParams()
        arrayParams['component'] = cutCylinder

        cutArray = component_array.ComponentArray(arrayParams)
        vTrans = self.getConnectorArrayTranslation()
        cutArray = Translate(cutArray,v=vTrans)
        return cutArray

    def getCutArrayBottom(self,panelThickness):
        standoffHeight = self.params['standoffHeight']
        standoffScrewRadius = self.params['standoffScrewRadius']
        cutCylinder = Cylinder(
                h  = standoffHeight + 2*panelThickness,
                r1 = standoffScrewRadius,
                r2 = standoffScrewRadius
                )
        cutArray = []
        for v in self.standoffTransList:
            cutArray.append(Translate(cutCylinder,v=v))
        cutArray = Union(cutArray)
        return cutArray


    def __str__(self):
        return self.part.__str__()


#------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    includeCutArray = True
    cutArrayPanel = 'bottom'

    pcb = ExpansionPCB()
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(pcb)
    if includeCutArray:
        cutArray = pcb.getCutArray(cutArrayPanel,3.0)
        if cutArray is not None:
            prog.add(cutArray)
    prog.write('expansion_pcb.scad')     






