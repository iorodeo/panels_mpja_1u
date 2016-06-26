import os
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_laser

dxfFileName = sys.argv[1]
numPass = 12 

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())

# Etching

param = {
        'fileName'    :  dxfFileName,
        'layers'      :  ['Engrave'],
        'dxfTypes'    :  ['LINE','ARC'],
        'laserPower'  :  600,
        'feedRate'    :  30,
        'convertArcs' :  True,
        'startCond'   : 'minX',
        'direction'   : 'ccw',
        'ptEquivTol'  :  0.4e-3,
        'returnHome'  :  False,
        }

vectorEtch = cnc_laser.VectorCut(param)

for i in range(numPass):
    prog.add(vectorEtch)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)

baseName, ext = os.path.splitext(dxfFileName)
ngcFileName = '{0}.ngc'.format(baseName)
prog.write(ngcFileName)
