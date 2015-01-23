from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

"""
Notes

Onsrud 63-610 (need coolant - denature alcohol) 
feedrate = RPM * (num flute) * (chip load)
cutter diam 1/8" 
num flute = 1
chip load = 0.003
RPM = 25000 (setting 6)
feedrate = 75 "/min

Nigara - terrible gummed up
num flute = 2
sfm = 300
RPM = 9100
feedrate = 36 "/min



"""

feedrate = 75.0
fileName = 'layout.dxf'
#fileName = 'layout_single.dxf'
depth = 0.2
#depth = 0.02
startZ = 0.0
safeZ = 0.5
maxCutDepth = 0.03
toolDiam = 0.125 
#toolDiam = 0.001
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
        'layers'       : ['BNC Hole', 'DC Jack Hole'], 
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
boundary = cnc_dxf.DxfCircPocket(param)
prog.add(boundary)

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
#boundary = cnc_dxf.DxfBoundary(param)
boundary = cnc_dxf.DxfRectPocketFromExtent(param)
prog.add(boundary)


prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
