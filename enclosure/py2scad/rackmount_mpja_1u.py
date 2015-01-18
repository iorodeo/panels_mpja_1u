from __future__ import print_function
from py2scad import *
import expansion_pcb

defaultParamsFront =  {
        'width'             :  19.0*INCH2MM,
        'height'            :  1.74*INCH2MM,
        'thickness'         :  0.1230*INCH2MM,
        'mountSlotWidth'  :  0.39*INCH2MM,
        'mountSlotHeight' :  0.24*INCH2MM,
        'mountSlotRadius' :  0.5*0.24*INCH2MM,
        'mountSlotInset'  :  (0.345*INCH2MM, 0.2525*INCH2MM),
        'shelfWidth'       :  15.625*INCH2MM,
        'shelfDepth'       :  0.4315*INCH2MM,
        'shelfThickness'   :  0.0830*INCH2MM,
        'shelfInset'       :  0.1635*INCH2MM,
        }

defaultParamsBottom = {
        'width'     : 16.5*INCH2MM,
        'height'    : 11.625*INCH2MM,
        'thickness' : 0.04*INCH2MM,
        }

defaultParamsBack = {
        'width'     :  16.875*INCH2MM,
        'height'    :  1.46*INCH2MM,
        'thickness' :  0.08*INCH2MM,
        }

defaultParamsEnclosure = {
        'front'  : defaultParamsFront,
        'bottom' : defaultParamsBottom,
        'back'   : defaultParamsBack,
        }

class Panel(object):
    """
    Base class for enclosure panels
    """

    def __init__(self, holeList=[], params={}):
        self.params = params
        self.holeList = holeList
        self.makePanel()
        self.addHoles()


    def makePanel(self):
        size = (
                self.params['width'],
                self.params['height'],
                self.params['thickness']
                )
        self.part = Cube(size=size)


    def addHoles(self,holeList=None):

        if holeList is None:
            holeList = self.holeList

        for hole in self.holeList:
            # Get cutting depth
            try:
                cutDepth = hole['cut_depth']
            except KeyError:
                cutDepth = 2*self.params['thickness']

            # Create cutting cylinder
            if hole['type'] == 'round':
                radius = 0.5*hole['size']
                holeCyl = Cylinder(r1=radius, r2=radius, h=cutDepth)
            elif hole['type'] == 'square':
                x,y = hole['size']
                holeCyl = Cube(size=(x,y,cutDepth))
            elif hole['type'] == 'rounded_square':
                x, y, radius = hole['size']
                holeCyl = rounded_box(x, y, cutDepth, radius, round_z=False)
            else:
                raise ValueError, 'unkown hole type {0}'.format(hole['type'])

            # Translate cylinder into position and cut hole
            x,y = hole['location']
            holeCyl = Translate(holeCyl, v = (x,y,0))
            self.part = Difference([self.part, holeCyl])

    def __str__(self):
        return self.part.__str__()


class PanelFront(Panel):

    def __init__(self, holeList = [], params=defaultParamsFront):
        super(PanelFront,self).__init__(holeList,params)
        self.makeShelves()

    def makeShelves(self):
        size = ( 
                self.params['shelfWidth'],
                self.params['shelfDepth'],
                self.params['shelfThickness']
                )
        shelf = Cube(size=size)
        shelf = Rotate(shelf,a=90.0,v=(1,0,0))
        insetY = self.params['shelfInset']
        for i in (-1,1):
            posY = i*(0.5*self.params['height'] - insetY)
            posZ = 0.5*(self.params['shelfDepth'] + self.params['thickness']) 
            shelfTrans = Translate(shelf,v=(0,posY,posZ))
            self.part = Union([self.part,shelfTrans])


    def addHoles(self, holeList=None):
        if holeList is None:
            # Add mount holes to hole list
            holeType = 'rounded_square'
            insetX, insetY = self.params['mountSlotInset']
            size = (
                    self.params['mountSlotWidth'],
                    self.params['mountSlotHeight'],
                    self.params['mountSlotRadius'],
                    )
            for i in (-1,1):
                for j in (-1,1):
                    posX = i*(0.5*self.params['width'] - insetX)
                    posY = j*(0.5*self.params['height'] - insetY)
                    location = (posX,posY)
                    hole = {'type': holeType, 'size': size, 'location': location}
                    self.holeList.append(hole)
            holeList = self.holeList
        super(PanelFront,self).addHoles(holeList)



class PanelBottom(Panel):

    def __init__(self,holeList=[],params=defaultParamsBottom):
        super(PanelBottom,self).__init__(holeList=holeList,params=params)


class PanelBack(Panel):

    def __init__(self,holeList=[],params=defaultParamsBack): 
        super(PanelBack,self).__init__(holeList=holeList,params=params)


class Enclosure(object):

    def __init__(self,holeDict={},params=defaultParamsEnclosure):
        self.panelNameList = ['front', 'bottom', 'back']
        self.holeDict = dict(zip(self.panelNameList, [[] for x in self.panelNameList]))
        self.panelNameList = self.holeDict.keys()
        self.holeDict.update(holeDict)
        self.params = params
        self.makePanels()

    def makePanels(self):
        self.front = PanelFront(
                holeList = self.holeDict['front'],
                params = self.params['front']
                )
        self.bottom = PanelBottom(
                holeList = self.holeDict['bottom'],
                params = self.params['bottom']
                )
        self.back = PanelBack(
                holeList = self.holeDict['back'],
                params = self.params['back']
                )

    def addHoles(self, holeDict=None):
        if holeDict is None:
            holeDict = self.holeDict
        for panelName, holeList in  holeDict.iteritems():
            panel = getattr(self,panelName)
            panel.addHoles(holeList)

    def getAssembly(self,**kwargs):
        partList = []
        for panelName in self.panelNameList:
            part = getattr(self,panelName)
            aRot, vRot = self.getRotation(panelName)
            if aRot != 0:
                part = Rotate(part, a=aRot, v=vRot)
            vTrans = self.getTranslation(panelName)
            part = Translate(part,v=vTrans)
            showKey = 'show{0}'.format(panelName.title())
            try:
                showVal = kwargs[showKey]
            except KeyError:
                showVal = True
            if showVal:
                partList.append(part)
        return partList 

    def getRotation(self,panelName):
        if panelName == 'front':
            return 90, (1,0,0)
        elif panelName == 'back':
            return 90, (1,0,0)
        elif panelName == 'bottom':
            return 0, (0,0,0)
        else:
            raise ValueError, 'unknown panel {0}'.format(panelName)

    def getTranslation(self,panelName):
        if panelName == 'front':
            posX = 0
            posY = 0.5*self.params['bottom']['height'] 
            posY += 0.5*self.params['front']['thickness']  
            posZ = 0
        elif panelName == 'back':
            posX = 0
            posY = -0.5*self.params['bottom']['height']
            posY -= 0.5*self.params['back']['thickness']
            posZ = 0.5*self.params['back']['height']
            posZ -= 0.5*self.params['front']['height']
            posZ += self.params['front']['shelfInset']
            posZ -= 0.5*self.params['front']['shelfThickness']
            posZ -= self.params['bottom']['thickness']
        elif panelName == 'bottom':
            posX = 0
            posY = 0
            posZ = -0.5*self.params['front']['height'] 
            posZ -= 0.5*self.params['bottom']['thickness']
            posZ += self.params['front']['shelfInset']
            posZ -= 0.5*self.params['front']['shelfThickness'] 
        else:
            raise ValueError, 'unknown panel {0}'.format(panelName)
        return posX, posY, posZ

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':

    enclosure = Enclosure()
    assembly = enclosure.getAssembly(
            showFront=True,
            showBottom=True,
            showBack=True,
            )

    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(assembly)
    prog.write('mpja_assembly.scad')


