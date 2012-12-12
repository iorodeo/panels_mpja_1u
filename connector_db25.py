"""
Makes a 25-pin connector. 

"""
from py2scad import *

defaultParams = {
    'baseX'           : 53.0,
    'baseY'           : 12.50,
    'baseZ'           : 2.5,
    'connX'           : 41.0,
    'connY'           : 9.3,
    'connZ'           : 5.5,
    'holeOffsetX'     : 23.52,
    'cutoutX'         : 41.0,
    'cutoutY'         : 12.6,
    'screwHoleRadius' : 0.5*3.12,
    }
    

class Connector_db25(object):

    def __init__(self,params=defaultParams):
        self.params = params
        self.make()

    def make(self):
        baseX = self.params['baseX']
        baseY = self.params['baseY']
        baseZ = self.params['baseZ']
        baseSize = baseX, baseY, baseZ
        base = Cube(size=baseSize)

        connX = self.params['connX']
        connY = self.params['connY']
        connZ = self.params['connZ']
        connSize = connX, connY, connZ
        conn = Cube(size=connSize)
        posZ = 0.5*connZ + 0.5*baseZ
        conn = Translate(conn, v=(0,0,posZ))
        self.part = Union([base, conn])

        hole = Cylinder(
                h  = 2*baseZ,
                r1 = self.params['screwHoleRadius'],
                r2 = self.params['screwHoleRadius'] 
                )
        holeList = []
        for i in (-1,1):
            posX = i*self.params['holeOffsetX']
            holeList.append(Translate(hole,v=(posX,0,0)))

        self.part = Difference([self.part] + holeList)

    def getCutArray(self,panelName, panelThickness):
        if panelName == 'back':
            return self.getCutArrayBack(panelThickness)
        else:
            return None

    def getCutArrayBack(self,panelThickness):

        cutoutX = self.params['cutoutX']
        cutoutY = self.params['cutoutY']
        cutoutZ = 3*panelThickness
        cutoutSize = cutoutX, cutoutY, cutoutZ
        cutout = Cube(size=cutoutSize) 
        posZ = -0.5*self.params['baseZ']
        posZ -= 0.5*cutoutZ
        posZ += 0.25*panelThickness
        cutout = Translate(cutout, v=(0,0,posZ))

        hole = Cylinder(
                h  = 3*panelThickness,
                r1 = self.params['screwHoleRadius'],
                r2 = self.params['screwHoleRadius'] 
                )
        holeList = []
        for i in (-1,1):
            posX = i*self.params['holeOffsetX']
            holeList.append(Translate(hole,v=(posX,0,posZ)))

        cutArray = Union([cutout] + holeList)
        return cutArray

    def __str__(self):
        return self.part.__str__()


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    includeCutArray = True 
    cutArrayPanel = 'back'

    conn = Connector_db25()
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(conn)
    if includeCutArray:
        cutArray = conn.getCutArray(cutArrayPanel,3.0)
        if cutArray is not None:
            prog.add(cutArray)
    prog.write('connector_db25.scad')     

