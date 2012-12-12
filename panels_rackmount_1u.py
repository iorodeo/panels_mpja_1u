from __future__ import print_function
from py2scad import *
import rackmount_mpja_1u 
import component_array
import expansion_pcb
import controller_pcb
import programmer_pcb

defaultParamsEnclosure = rackmount_mpja_1u.defaultParamsEnclosure
panelsParamsExtra = { 
        'expansionPCB_PosX'   :  3.77*INCH2MM, 
        'expansionPCB_PosY'   :  4.71*INCH2MM, 
        'controllerPCB_PosX'  : -4.36*INCH2MM,
        'controllerPCB_PosY'  :  3.27*INCH2MM,
        'programmerPCB_PosX'  : -0.71*INCH2MM,
        }
defaultParamsEnclosure.update(panelsParamsExtra)

class PanelsEnclosure(rackmount_mpja_1u.Enclosure):


    def __init__(self,holeDict={},params=defaultParamsEnclosure):
        super(PanelsEnclosure,self).__init__(holeDict={},params=params)
        self.partNameList = ['expansionPCB', 'controllerPCB', 'programmerPCB']
        self.expansionPCB = expansion_pcb.ExpansionPCB()
        self.controllerPCB = controller_pcb.ControllerPCB()
        self.programmerPCB = programmer_pcb.ProgrammerPCB()
        self.makeHoles()

    def makeHoles(self):
        """
        Creates holes in enclosure panels based on cut arrays
        """

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
            part = Rotate(part,a=aRot,v=vRot)
            vTrans = self.getTranslation(partName)
            part = Translate(part,v=vTrans)
            if 'PCB' in partName:
                showKey = 'show{0}PCB'.format(partName[:-3].title())
            else:
                showKey = 'show{0}'.format(partName.title())
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
        part = Rotate(part,a=-aRot,v=vRot)
        return part


# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    enclosure = PanelsEnclosure()
    assembly = enclosure.getAssembly(
            showFront=True,
            showBottom=True,
            showBack=True,
            showExpansionPCB=True,
            showControllerPCB=True,
            showProgrammerPCB=True,
            )

    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(assembly)
    prog.write('panels_assembly.scad')


