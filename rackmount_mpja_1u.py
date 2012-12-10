from __future__ import print_function
from py2scad import *
import expansion_pcb

DEFAULT_PARAMS_FRONT =  {
        'width'             :  19.0*INCH2MM,
        'height'            :  1.74*INCH2MM,
        'thickness'         :  0.1230*INCH2MM,
        'mountSlotWidth'  :  0.39*INCH2MM,
        'mountSlotHeight' :  0.24*INCH2MM,
        'mountSlotRadius' :  0.5*0.24*INCH2MM,
        'mountSlotInset'  :  (0.345*INCH2MM, 0.2525*INCH2MM),
        'shelfWidth'       :  15.62*INCH2MM,
        'shelfDepth'       :  0.4315*INCH2MM,
        'shelfThickness'   :  0.0830*INCH2MM,
        'shelfInset'       :  0.1635*INCH2MM,
        }

DEFAULT_PARAMS_BOTTOM = {
        'width'     : 16.5*INCH2MM,
        'height'    : 11.625*INCH2MM,
        'thickness' : 0.04*INCH2MM,
        }

DEFAULT_PARAMS_BACK = {
        'width'     :  16.875*INCH2MM,
        'height'    :  1.46*INCH2MM,
        'thickness' :  0.08*INCH2MM,
        }

DEFAULT_PARAMS_ENCLOSURE = {
        'front'  : DEFAULT_PARAMS_FRONT,
        'bottom' : DEFAULT_PARAMS_BOTTOM,
        'back'   : DEFAULT_PARAMS_BACK,
        }

DEFAULT_PARAMS_PANELS_ENCLOSURE = DEFAULT_PARAMS_ENCLOSURE
PANELS_PARAMS_EXTRA = { 
        'expansionPCB_PosX'   : 3.75*INCH2MM, 
        'expansionPCB_PosY'   : 4.7*INCH2MM, 
        }
DEFAULT_PARAMS_PANELS_ENCLOSURE.update(PANELS_PARAMS_EXTRA)


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

    def __init__(self, holeList = [], params=DEFAULT_PARAMS_FRONT):
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


    def addHoles(self):
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
        super(PanelFront,self).addHoles()



class PanelBottom(Panel):

    def __init__(self,holeList=[],params=DEFAULT_PARAMS_BOTTOM):
        super(PanelBottom,self).__init__(holeList=holeList,params=params)


class PanelBack(Panel):

    def __init__(self,holeList=[],params=DEFAULT_PARAMS_BACK): 
        super(PanelBack,self).__init__(holeList=holeList,params=params)


class Enclosure(object):

    def __init__(self,holeDict={},params=DEFAULT_PARAMS_ENCLOSURE):
        self.holeDict = {'front': [], 'bottom': [], 'back': []}
        self.holeDict.update(holeDict)
        self.params = params
        self.makePanels()
        self.makeExpansionPCB()

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

    def getAssembly(self,**kwargs):

        front = self.front
        front = Rotate(front, a=90, v=(1,0,0))
        posY = 0.5*self.params['bottom']['height'] + 0.5*self.params['front']['thickness']  
        front = Translate(front,v=(0,posY,0))

        bottom = self.bottom
        posZ = -0.5*self.params['front']['height'] - 0.5*self.params['bottom']['thickness']
        posZ += self.params['front']['shelfInset']
        posZ -= 0.5*self.params['front']['shelfThickness'] 
        bottom = Translate(bottom, v=(0,0,posZ))

        back = self.back
        back = Rotate(back,a=90,v=(1,0,0))

        posY = -0.5*self.params['bottom']['height']
        posY -= 0.5*self.params['back']['thickness']
        posZ = 0.5*self.params['back']['height']
        posZ -= 0.5*self.params['front']['height']
        posZ += self.params['front']['shelfInset']
        posZ -= 0.5*self.params['front']['shelfThickness']
        posZ -= self.params['bottom']['thickness']
        back = Translate(back,v=(0,posY,posZ))
        
        partList = []
        try:
            showFront = kwargs['showFront']
        except KeyError:
            showFront = True
        if showFront:
            partList.append(front)
        
        try:
            showBottom = kwargs['showBottom']
        except KeyError:
            showBottom = True
        if showBottom:
            partList.append(bottom)

        try:
            showBack = kwargs['showBack']
        except KeyError:
            showBack = True
        if showBack:
            partList.append(back)

        return partList 


class PanelsEnclosure(Enclosure):

    def __init__(self,holeDict={},params=DEFAULT_PARAMS_PANELS_ENCLOSURE):
        super(PanelsEnclosure,self).__init__(holeDict={},params=params)
        self.makeExpansionPCB()

    def createHoleDict(self):
        return {}

    def makeExpansionPCB(self):
        self.expansionPCB = expansion_pcb.ExpansionPCB()

    def getAssembly(self,**kwargs):
        partList = super(PanelsEnclosure,self).getAssembly(**kwargs)

        expansionPCB = self.expansionPCB
        expansionPCB = Rotate(expansionPCB,a=180,v=(0,0,1))
        posX = self.params['expansionPCB_PosX']
        posY = self.params['expansionPCB_PosY']
        posZ = 0.5*self.expansionPCB.params['thickness'] + self.expansionPCB.params['standoffHeight']
        posZ -= 0.5*self.params['front']['height'] 
        posZ += self.params['front']['shelfInset']
        posZ -= 0.5*self.params['front']['shelfThickness']
        expansionPCB = Translate(expansionPCB,v=(posX,posY,posZ))
        try:
            showExpansionPCB = kwargs['showExpansionPCB']
        except KeyError:
            showExpansionPCB = True
        if showExpansionPCB:
            partList.append(expansionPCB)

        return partList



# ---------------------------------------------------------------------------------------
if __name__ == '__main__':


    enclosure = PanelsEnclosure()
    assembly = enclosure.getAssembly(
            showFront=True,
            showBottom=True,
            showBack=True,
            )

    prog = SCAD_Prog()
    prog.fn = 50
    prog.add(assembly)
    prog.write('assembly.scad')


