from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

feedrate = 100.0
fileName = 'layout.dxf'
depth = 0.74
startZ = 0.0
safeZ = 0.5
overlap = 0.5
maxCutDepth = 0.15
toolDiam = 3/16.0 
direction = 'ccw'
startDwell = 1.0

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

param = {
        'fileName'       : fileName,
        'layers'         : ['Fixture Hole 1/4-20 Insert'],
        'depth'          : depth,
        'startZ'         : startZ,
        'safeZ'          : safeZ,
        'overlap'        : overlap,
        'overlapFinish'  : overlap,
        'maxCutDepth'    : maxCutDepth,
        'toolDiam'       : toolDiam,
        'direction'      : direction,
        'startDwell'     : startDwell,
        }
pocket = cnc_dxf.DxfCircPocket(param)
prog.add(pocket)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
