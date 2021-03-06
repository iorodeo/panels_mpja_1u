from __future__ import print_function
import sys
import os
from py2gcode import gcode_cmd
from py2gcode import cnc_laser

material = '3mm'
if material == '6mm':
    feedRate = 10
elif material == '3mm':
    feedRate = 25
else:
    print('uknown material selection: {0}'.format(material))
    sys.exit(1)
    

dxfFileName = sys.argv[1]

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())

param = {
        'fileName'    :  dxfFileName,
        'layers'      :  ['Laser Fixture Pocket'],
        'dxfTypes'    :  ['LINE','ARC'],
        'laserPower'  :  600,
        'feedRate'    :  feedRate,
        'convertArcs' :  True,
        'startCond'   : 'minX',
        'direction'   : 'ccw',
        'ptEquivTol'  :  0.4e-3,
        }

vectorCut = cnc_laser.VectorCut(param)
prog.add(vectorCut)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)

baseName, ext = os.path.splitext(dxfFileName)
ngcFileName = '{0}.ngc'.format(baseName)
prog.write(ngcFileName)
