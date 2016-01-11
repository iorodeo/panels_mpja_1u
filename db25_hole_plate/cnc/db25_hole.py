from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

fileName = sys.argv[1]

feedrate = 120.0

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

layerNames = ['db25_hole']
param = {
        'fileName'    : fileName,
        'layers'      : layerNames,
        'depth'       : 0.09,
        'startZ'      : 0.0,
        'safeZ'       : 0.3,
        'toolDiam'    : 0.125,
        'direction'   : 'ccw', 
        'cutterComp'  : 'inside',
        'maxCutDepth' : 0.12,
        'startDwell'  : 2.0,
        'startCond'   : 'minX',
        'maxArcLen'   : 1.0e-2, 
        'ptEquivTol'  : 1.0e-5,
        }
boundary = cnc_dxf.DxfBoundary(param)
prog.add(boundary)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
