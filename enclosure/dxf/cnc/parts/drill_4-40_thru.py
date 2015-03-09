from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

"""
Notes

* drill 1/8" (0.125")
* SFM 270
* IPR 0.003
* feedrate = 24 "/min
* RPM = 8000 (bosch setting ~1)

"""

testCut = False 

feedrate = 24.0
fileName = 'layout.dxf'
#fileName = 'layout_single_1.dxf'
startZ = 0.01
if testCut:
    stopZ = startZ - 0.05
else:
    stopZ = -0.25
safeZ = 0.75
stepZ = 0.03
startDwell = 0.5

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

param = { 
        'fileName'    : fileName,
        'layers'      : ['4-40 Through Hole'],
        'dxfTypes'    : ['CIRCLE'],
        'startZ'      : startZ,
        'stopZ'       : stopZ,
        'safeZ'       : safeZ,
        'stepZ'       : stepZ,
        'startDwell'  : startDwell,
        }
drill = cnc_dxf.DxfDrill(param)
prog.add(drill)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
