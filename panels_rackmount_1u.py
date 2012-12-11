from __future__ import print_function
from py2scad import *
import rackmount_mpja_1u 
import expansion_pcb
import controller_pcb
import component_array

defaultParamsEnclosure = rackmount_mpja_1u.defaultParamsEnclosure
panelsParamsExtra = { 
        'expansionPCB_PosX'   :  3.75*INCH2MM, 
        'expansionPCB_PosY'   :  4.71*INCH2MM, 
        'controllerPCB_PosX'  : -4.35*INCH2MM,
        'controllerPCB_PosY'  :  3.27*INCH2MM,
        'clearanceBNC'        :  0.625,
        'clearanceController' :  1.1,
        }
defaultParamsEnclosure.update(panelsParamsExtra)

class PanelsEnclosure(rackmount_mpja_1u.Enclosure):

    def __init__(self,holeDict={},params=defaultParamsEnclosure):
        super(PanelsEnclosure,self).__init__(holeDict={},params=params)
        self.expansionPCB = expansion_pcb.ExpansionPCB()
        self.controllerPCB = controller_pcb.ControllerPCB()
        self.makeBNCHoles()
        self.makeControllerHoles()

    def makeBNCHoles(self):
        # Get cut array for expansion pcb
        cutArray = self.expansionPCB.getCutArray(
                self.params['clearanceBNC'],
                self.params['front']['thickness'],
                )

        # Move expansion cut array to same position as BNC thread cylinders in assembly
        aRot, vRot = self.getRotation('expansionPCB')
        cutArray = Rotate(cutArray,a=aRot,v=vRot)
        v = self.getTranslation('expansionPCB')
        cutArray = Translate(cutArray,v=v)

        # Translate and rotate cutArray into front panel initial position and cut holes
        vTrans = self.getFrontPanelTranslation()
        vTransInv = [-x for x in vTrans]
        cutArray = Translate(cutArray, v=vTransInv)
        aRot, vRot = self.getFrontPanelRotation()
        cutArray = Rotate(cutArray,a=-aRot,v=vRot)
        self.front = Difference([self.front, cutArray])

    def makeControllerHoles(self):
        # Get cut array for controller
        cutArray = self.controllerPCB.getCutArray(
                self.params['clearanceController'],
                self.params['front']['thickness'],
                )

        # Move cut array to same position as controller Components
        aRot, vRot = self.getRotation('controllerPCB')
        cutArray = Rotate(cutArray,a=aRot,v=vRot)
        v = self.getTranslation('controllerPCB')
        cutArray = Translate(cutArray,v=v)

        self.temp = cutArray

        # Translate and rotate cutArray into front panel initial position and cut holes
        vTrans = self.getFrontPanelTranslation()
        vTransInv = [-x for x in vTrans]
        cutArray = Translate(cutArray, v=vTransInv)
        aRot, vRot = self.getFrontPanelRotation()
        cutArray = Rotate(cutArray,a=-aRot,v=vRot)
        self.front = Difference([self.front, cutArray])


    def getAssembly(self,**kwargs):
        partList = super(PanelsEnclosure,self).getAssembly(**kwargs)
        partNameList = ('expansionPCB', 'controllerPCB')
        for partName in partNameList:
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

            #partList.append(self.temp)

        return partList

    def getRotation(self,partName):
        if partName == 'expansionPCB':
            rotationValues = 180, (0,0,1)
        elif partName == 'controllerPCB':
            rotationValues = 180, (0,0,1)
        else:
            raise ValueError, 'unknown  part name {0}'.format(partName)
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
        return posX, posY, posZ


# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    enclosure = PanelsEnclosure()
    assembly = enclosure.getAssembly(
            showFront=True,
            showBottom=True,
            showBack=True,
            showExpansionPCB=True,
            showControllerPCB=True,
            )

    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(assembly)
    prog.write('panels_assembly.scad')


