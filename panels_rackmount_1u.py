from __future__ import print_function
from py2scad import *
import os
import subprocess
import rackmount_mpja_1u 
import component_array
import expansion_pcb
import controller_pcb
import programmer_pcb
import connector_db25
import dc_jack
import power_switch

defaultParamsEnclosure = rackmount_mpja_1u.defaultParamsEnclosure
panelsParamsExtra = { 
        'expansionPCB_PosX'   :  3.77*INCH2MM, 
        'expansionPCB_PosY'   :  4.71*INCH2MM, 
        'controllerPCB_PosX'  : -4.36*INCH2MM,
        'controllerPCB_PosY'  :  3.27*INCH2MM,
        'programmerPCB_PosX'  : -0.71*INCH2MM,
        'connectorDB25_PosX'  :  3.77*INCH2MM,
        'dcJack_PosX'         : -4.36*INCH2MM,
        'powerSwitch_PosX'    :  -7.95*INCH2MM, 
        }
defaultParamsEnclosure.update(panelsParamsExtra)

class PanelsEnclosure(rackmount_mpja_1u.Enclosure):


    def __init__(self,holeDict={},params=defaultParamsEnclosure):
        super(PanelsEnclosure,self).__init__(holeDict={},params=params)
        self.partNameList = [
                'expansionPCB', 
                'controllerPCB', 
                'programmerPCB',
                'connectorDB25',
                'dcJack',
                'powerSwitch',
                ]
        self.expansionPCB = expansion_pcb.ExpansionPCB()
        self.controllerPCB = controller_pcb.ControllerPCB()
        self.programmerPCB = programmer_pcb.ProgrammerPCB()
        self.connectorDB25 = connector_db25.Connector_db25() 
        self.dcJack = dc_jack.DCJack()
        self.powerSwitch = power_switch.PowerSwitch()
        self.makeHoles()

    def makeHoles(self):
        """
        Creates holes in enclosure panels based on cut arrays
        """

        # Add pcb, connectot component holes
        for panelName in self.panelNameList:
            # Get panel object and thickness
            thickness = self.params[panelName]['thickness']
            panel = getattr(self,panelName)

            for partName in self.partNameList:
                # Get cut array for given panel and part
                part = getattr(self,partName)
                cutArray = part.getCutArray(panelName,thickness)
                if cutArray is None:
                    continue

                # Move cut array into part positoin
                aRot, vRot = self.getRotation(partName)
                if aRot != 0:
                    cutArray = Rotate(cutArray,a=aRot,v=vRot)
                v = self.getTranslation(partName)
                cutArray = Translate(cutArray,v=v)

                # Move to panel initial position and cut holes
                cutArray = self.applyInvPanelTransform(panelName,cutArray)
                panel = Difference([panel, cutArray])

            setattr(self,panelName,panel)

    def getAssembly(self,**kwargs):
        """
        Creates enclosure assembly
        """
        partList = super(PanelsEnclosure,self).getAssembly(**kwargs)
        for partName in self.partNameList:
            part = getattr(self, partName)
            aRot, vRot = self.getRotation(partName)
            if aRot != 0:
                part = Rotate(part,a=aRot,v=vRot)
            vTrans = self.getTranslation(partName)
            part = Translate(part,v=vTrans)
            showKey = 'show{0}{1}'.format(partName[0].upper(), partName[1:])
            try:
                showValue = kwargs[showKey]
            except KeyError:
                showValue = True
            if showValue:
                partList.append(part)
        return partList


    def getRotation(self,partName):
        if partName == 'expansionPCB':
            rotationValues = 180, (0,0,1)
        elif partName == 'controllerPCB':
            rotationValues = 180, (0,0,1)
        elif partName == 'programmerPCB':
            rotationValues = 90, (1,0,0)
        elif partName == 'connectorDB25':
            rotationValues = 90, (1,0,0)
        elif partName == 'dcJack':
            rotationValues = -90, (1,0,0)
        elif partName == 'powerSwitch':
            rotationValues = 90, (1,0,0)
        else:
            rotationValues = super(PanelsEnclosure,self).getRotation(partName)
        return rotationValues


    def getTranslation(self,partName):
        if partName == 'expansionPCB':
            posX = self.params['expansionPCB_PosX']
            posY = self.params['expansionPCB_PosY']
            posZ = 0.5*self.expansionPCB.params['thickness'] 
            posZ += self.expansionPCB.params['standoffHeight']
            posZ -= 0.5*self.params['front']['height'] 
            posZ += self.params['front']['shelfInset']
            posZ -= 0.5*self.params['front']['shelfThickness']
        elif partName == 'controllerPCB':
            posX = self.params['controllerPCB_PosX']
            posY = self.params['controllerPCB_PosY']
            posZ = 0.5*self.controllerPCB.params['thickness'] 
            posZ += self.controllerPCB.params['standoffHeight']
            posZ -= 0.5*self.params['front']['height'] 
            posZ += self.params['front']['shelfInset']
            posZ -= 0.5*self.params['front']['shelfThickness']
        elif partName == 'programmerPCB':
            posX = self.params['programmerPCB_PosX'] 
            posY = 0.5*self.programmerPCB.params['thickness']
            posY += self.programmerPCB.params['standoffHeight'] 
            posY += 0.5*self.params['bottom']['height']
            posY += self.params['front']['thickness']
            posZ = 0
        elif partName == 'connectorDB25':
            posX = self.params['connectorDB25_PosX'] 
            posY = -0.5*self.connectorDB25.params['baseZ']
            posY -= 0.5*self.params['bottom']['height'] 
            posY -= self.params['back']['thickness']
            posZ = 0
        elif partName == 'dcJack':
            posX = self.params['dcJack_PosX'] 
            posY = -0.5*self.params['bottom']['height']
            posY -= self.params['back']['thickness']
            posZ = 0
        elif partName == 'powerSwitch':
            posX = self.params['powerSwitch_PosX'] 
            posY = 0.5*self.params['bottom']['height'] 
            posY += self.params['front']['thickness']
            posZ = 0
        else:
            posX, posY, posZ = super(PanelsEnclosure,self).getTranslation(partName)
        return posX, posY, posZ


    def applyInvPanelTransform(self,panelName,part):
        """
        Apply the inverse of the transformation which puts
        the given panel into the assembly position.
        """
        vTrans = self.getTranslation(panelName)
        vTransInv = [-x for x in vTrans]
        part = Translate(part, v=vTransInv)
        aRot, vRot = self.getRotation(panelName)
        if aRot != 0:
            part = Rotate(part,a=-aRot,v=vRot)
        return part

    def getPanelProjectionRotation(self,panelName):
        if panelName == 'front':
            return 180, (0,1,0)
        else:
            return 0, (0,0,0)

    def getPanelProjections(self,pretend=False):
        """
        Returns a dictionary of projections of the enclosure panels
        """
        projDict = {}
        for panelName in self.panelNameList:
            panel = getattr(self, panelName)
            a,v = self.getPanelProjectionRotation(panelName)
            if a != 0:
                panel = Rotate(panel,a=a,v=v)
            if pretend:
                panelProj = panel
            else:
                panelProj = Projection(panel)
            projDict[panelName] = panelProj
        return projDict

    def writePanelProjectionSCAD(self,fn=50,pretend=False):
        projDict = self.getPanelProjections(pretend=pretend)
        fileNameList = []
        for name, projection in projDict.iteritems():
            prog = SCAD_Prog()
            prog.fn = fn
            prog.add(projection)
            fileName = '{0}.scad'.format(name)
            prog.write(fileName)
            fileNameList.append(fileName)
        return fileNameList

    def writePanelProjectionDXF(self,fn=50):
        scadFileList = self.writePanelProjectionSCAD()
        for scadFile in scadFileList:
            baseName, extName = os.path.splitext(scadFile)
            dxfFile = '{0}.dxf'.format(baseName)
            cmdList = ['openscad', '-x', dxfFile, scadFile]
            print('creating: {0}'.format(dxfFile))
            subprocess.call(cmdList)

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    createDXF = True

    enclosure = PanelsEnclosure()
    assembly = enclosure.getAssembly(
            showFront=True,
            showBottom=True,
            showBack=True,
            showExpansionPCB=True,
            showControllerPCB=True,
            showProgrammerPCB=True,
            showConnectorDB25=True,
            showDcJack=True,
            )

    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(assembly)
    prog.write('panels_assembly.scad')

    enclosure.writePanelProjectionSCAD()
    if createDXF:
        enclosure.writePanelProjectionDXF()


