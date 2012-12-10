"""

Makes and array components spaced a given distance apart

"""
from py2scad import *

class ComponentArray(object):

    def __init__(self,params):
        self.params = params
        self.make()

    def make(self):
        component = self.params['component']
        spacing = self.params['spacing']
        number = self.params['number']
        componentList = []

        for i in range(0,number):
            posX=i*spacing - 0.5*(number-1)*spacing
            componentNew = Translate(component, v=[posX,0,0 ])
            componentList.append(componentNew)
        self.part = Union(componentList)

    def __str__(self):
        return self.part.__str__()


#------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    import connector_bnc

    params = {
            'component'  : connector_bnc.Connector_BNC(),
            'spacing'    : 0.8*INCH2MM,
            'number'     : 10,
            }


    compArray  = ComponentArray(params)
    prog = SCAD_Prog()
    prog.fn=50
    prog.add(compArray)
    prog.write('comp_array.scad')     






