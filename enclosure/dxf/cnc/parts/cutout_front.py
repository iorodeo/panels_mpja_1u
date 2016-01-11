from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

"""
Notes

Onsrud 63-620 (need coolant - denature alcohol) 
feedrate = 45
chipload = 0.003
rpm = 16000 (setting 3.4).




"""
testCut = False 

#feedrate = 80.0
feedrate = 45.0
#fileName = 'layout.dxf'
fileName = 'layout_single_0.dxf'

if testCut:
    depth = 0.02
    toolDiam = 0.001
else:
    depth = 0.2
    #toolDiam = 0.125 
    toolDiam = 0.25 

startZ = 0.0
safeZ = 0.75
maxCutDepth = 0.05
#maxCutDepth = 0.03
direction = 'ccw'
cutterComp = 'inside'
overlap = 0.4
startDwell = 1.0
startCond = 'minX'

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

param = {
        'fileName'     : fileName,
        'layers'       : ['BNC Hole'], 
        'depth'        : depth,
        'startZ'       : startZ,
        'safeZ'        : safeZ,
        'toolDiam'     : toolDiam,
        'cutterComp'   : cutterComp,
        'direction'    : direction,
        'maxCutDepth'  : maxCutDepth,
        'overlap'      : overlap,
        'startDwell'   : startDwell,
        }
if testCut:
    cut = cnc_dxf.DxfCircBoundary(param)
else:
    cut = cnc_dxf.DxfCircPocket(param)
prog.add(cut)

param = {
        'fileName'    : fileName,
        'layers'      : ['Cutout'],
        'depth'       : depth,
        'startZ'      : startZ,
        'safeZ'       : safeZ,
        'toolDiam'    : toolDiam,
        'direction'   : direction,
        'cutterComp'  : cutterComp,
        'maxCutDepth' : maxCutDepth,
        'startDwell'  : startDwell, 
        'overlap'     : overlap,
        'cornerCut'   : False,
        'startCond'   : startCond,
        }
if testCut:
    cut = cnc_dxf.DxfBoundary(param)
else:
    cut = cnc_dxf.DxfRectPocketFromExtent(param)
prog.add(cut)


prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
