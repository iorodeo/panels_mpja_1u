"""
Makes the main panel controller board 

"""
from __future__ import print_function
from py2scad import *
import led
import copy


standoffPosList = [ 
        (-3.302*INCH2MM,  2.362*INCH2MM),
        ( 3.293*INCH2MM,  2.372*INCH2MM),
        (-3.302*INCH2MM, -1.565*INCH2MM),
        ( 3.293*INCH2MM, -1.565*INCH2MM),
        ]

defaultParamsControllerPCB = {
        'pcbX'                 : 6.8*INCH2MM,
        'pcbY'                 : 5*INCH2MM,
        'thickness'            : 1.65,
        'usbX'                 : 12.0, 
        'usbY'                 : 16.5,
        'usbZ'                 : 11.0,
        'sdX'                  : 28.0,
        'sdY'                  : 30.5,
        'sdZ'                  : 3.1,
        'db9X'                 : 31.0,
        'db9Y'                 : 12.6,
        'db9Z'                 : 12.5,
        'standoffHeight'       : 0.375*INCH2MM,
        'standoffRadius'       : 3.23,
        'standoffScrewHeight'  : 15,
        'standoffScrewRadius'  : 1.39,
        'led4PosX'             : 2.71*INCH2MM,
        'led2PosX'             : -2.21*INCH2MM,       
        'led1PosX'             : -3.01*INCH2MM,       
        'usbPosX'              : -1.55*INCH2MM,
        'sdPosX'               :  1.51*INCH2MM,      
        'db9PosX'              : -0.251*INCH2MM, 
        'standoffPosList'      : standoffPosList,
        'clearance'            :  1.1,
        }


class ControllerPCB:

    def __init__(self,params=defaultParamsControllerPCB):
        self.params = params
        self.make()

    def make(self):

        # Base parts
        pcbSize = self.params['pcbX'], self.params['pcbY'], self.params['thickness']
        pcb = Cube(size=pcbSize)

        ledParams = copy.deepcopy(led.defaultParamsLedArray)
        ledParams['number'] = 4
        led4 = led.LedArray(ledParams)

        ledParams['number'] = 2
        led2 = led.LedArray(ledParams)

        ledParams['number'] = 1
        led1 = led.LedArray(ledParams)

        usbSize = self.params['usbX'], self.params['usbY'], self.params['usbZ']
        usb = Cube(size=usbSize)

        sdSize = self.params['sdX'], self.params['sdY'], self.params['sdZ']
        sd= Cube(size=sdSize)

        db9Size = self.params['db9X'], self.params['db9Y'], self.params['db9Z']
        db9 = Cube(size=db9Size)

        self.componentDict = {
                'led4' : led4,
                'led2' : led2,
                'led1' : led1,
                'usb'  : usb,
                'sd'   : sd,
                'db9'  : db9,
                }

        for compName, comp in self.componentDict.items():
            v = self.getTranslation(compName)
            self.componentDict[compName] = Translate(comp,v=v)

        standoff = Cylinder(
                h  = self.params['standoffHeight'], 
                r1 = self.params['standoffRadius'], 
                r2 = self.params['standoffRadius'],
                )

        self.standoffDict = {}
        for i in range(len(self.params['standoffPosList'])):
            standoffName = 'standoff_{0}'.format(i)
            v = self.getTranslation(standoffName)
            self.standoffDict[standoffName] = Translate(standoff,v=v)

        self.part = Union([pcb] + self.componentDict.values() + self.standoffDict.values())

    def getCutArray(self,panelName,panelThickness):
        if panelName == 'front':
            cutArray = self.getCutArrayFront(panelThickness)
        elif panelName == 'back':
            cutArray = None
        elif panelName == 'bottom':
            cutArray = self.getCutArrayBottom(panelThickness) 
        else:
            raise ValueError, 'unknown panel {0}'.format(panelName)
        return cutArray

    def getCutArrayFront(self,panelThickness):
        ledParams = copy.deepcopy(led.defaultParamsLedArray)
        baseSize = ledParams['led']['baseSize']
        baseSize = (baseSize[0], 2*(baseSize[1]+panelThickness), baseSize[2])
        ledParams['led']['baseSize'] = baseSize
        ledParams['space'] = -0.01
        ledParams['number'] = 4
        led4Cut = led.LedArray(ledParams)

        ledParams['number'] = 2
        led2Cut = led.LedArray(ledParams)

        ledParams['number'] = 1
        led1Cut = led.LedArray(ledParams)

        usbX = self.params['usbX'] + 2*self.params['clearance']
        usbY = 2*(self.params['usbY'] + panelThickness)
        usbZ = self.params['usbZ'] + 2*self.params['clearance']
        usbSize = usbX, usbY, usbZ
        usbCut = Cube(size=usbSize)

        sdX = self.params['sdX'] + 2*self.params['clearance']
        sdY = 2*(self.params['sdY'] + panelThickness)
        sdZ = self.params['sdZ'] + 2*self.params['clearance']
        sdSize = sdX, sdY, sdZ
        sdCut = Cube(size=sdSize)

        db9X = self.params['db9X'] + 2*self.params['clearance']
        db9Y = 2*(self.params['db9Y'] + panelThickness)
        db9Z = self.params['db9Z'] + 2*self.params['clearance']
        db9Size = db9X, db9Y, db9Z
        db9Cut = Cube(size=db9Size)

        self.cutDict = {
                'led4' : led4Cut,
                'led2' : led2Cut,
                'led1' : led1Cut,
                'usb'  : usbCut,
                'sd'   : sdCut,
                'db9'  : db9Cut,
                }

        for compName, cut in self.cutDict.items():
            v = self.getTranslation(compName)
            self.cutDict[compName] = Translate(cut,v=v)
        cutArray = Union(self.cutDict.values())

        return cutArray

    def getCutArrayBottom(self,panelThickness):
        standoffScrewRadius = self.params['standoffScrewRadius']
        standoffHeight = self.params['standoffHeight']
        cutCyl = Cylinder(
                h  = standoffHeight + 2*panelThickness,
                r1 = standoffScrewRadius,
                r2 = standoffScrewRadius
                )
        cutArray = []
        for standoffName in self.standoffDict:
            v = self.getTranslation(standoffName)
            cutArray.append(Translate(cutCyl,v=v))
        cutArray = Union(cutArray)
        return cutArray 

    def getTranslation(self,partName): 
        pcbX = self.params['pcbX']
        pcbY = self.params['pcbY']
        thickness = self.params['thickness']
        ledY = led.defaultParamsLedArray['led']['baseSize'][1]
        ledZ = led.defaultParamsLedArray['led']['baseSize'][2]
        usbY = self.params['usbY']
        usbZ = self.params['usbZ']
        sdY = self.params['sdY']
        sdZ = self.params['sdZ']
        db9Y = self.params['db9Y']
        db9Z = self.params['db9Z']
        standoffHeight = self.params['standoffHeight']

        ledPosY = -0.5*pcbY + 0.5*ledY
        ledPosZ = 0.5*ledZ + 0.5*thickness
        
        if partName == 'led4': 
            posX = self.params['led4PosX'] 
            posY = ledPosY 
            posZ = ledPosZ

        elif partName == 'led2':
            posX = self.params['led2PosX']
            posY = ledPosY 
            posZ = ledPosZ

        elif partName == 'led1':
            posX = self.params['led1PosX']
            posY = ledPosY 
            posZ = ledPosZ

        elif partName == 'usb':
            posX = self.params['usbPosX']
            posY = -0.5*pcbY + 0.5*usbY
            posZ = 0.5*usbZ + 0.5*thickness

        elif partName == 'sd':
            posX = self.params['sdPosX']
            posY = -0.5*pcbY + 0.5*sdY
            posZ = 0.5*sdZ + 0.5*thickness

        elif partName == 'db9':
            posX = self.params['db9PosX']
            posY = -0.5*pcbY + 0.5*db9Y
            posZ = 0.5*db9Z + 0.5*thickness

        elif 'standoff' in partName:
            num = int(partName.split('_')[1])
            posX, posY = self.params['standoffPosList'][num]
            posZ = -(0.5*standoffHeight+0.5*thickness)
        else: 
            raise ValueError, 'unknown part name {0}'.format(partName) 
        return  posX, posY, posZ


    def __str__(self):
        return self.part.__str__()


# -----------------------------------------------------------------------------
if __name__ == "__main__":

    includeCutArray = True 
    cutArrayPanel = 'bottom'

    pcb = ControllerPCB()
    prog = SCAD_Prog()
    prog.fn=10
    prog.add(pcb)

    if includeCutArray:
        cutArray = pcb.getCutArray(cutArrayPanel, 3.0)
        prog.add(cutArray)
    prog.write('controller_pcb.scad')     

