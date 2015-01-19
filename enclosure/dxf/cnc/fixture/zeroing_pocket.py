from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

feedrate = 150.0
fileName = 'layout.dxf'
depth = 0.4
startZ = 0.0
safeZ = 0.5
overlap = 0.5
overlapFinish = 0.5
maxCutDepth = 0.15
toolDiam =  3.0/16.0 
cornerCut = True 
direction = 'ccw'
startDwell = 1.0

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

param = {
        'fileName'       : fileName,
        'layers'         : ['Zeroing Pocket'],
        'components'     : True,
        'depth'          : depth,
        'startZ'         : startZ,
        'safeZ'          : safeZ,
        'overlap'        : overlap,
        'overlapFinish'  : overlapFinish,
        'maxCutDepth'    : maxCutDepth,
        'toolDiam'       : toolDiam,
        'cornerCut'      : cornerCut,
        'direction'      : direction,
        'startDwell'     : startDwell,
        }
pocket = cnc_dxf.DxfRectPocketFromExtent(param)
prog.add(pocket)


prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
