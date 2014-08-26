from __future__ import print_function
import os 
import sys
from py2gcode import gcode_cmd
from py2gcode import cnc_dxf

fileName = 'db25_hole_plate.dxf'

feedrate = 25.0
layerNames = ['hole_thru_4-40']

prog = gcode_cmd.GCodeProg()
prog.add(gcode_cmd.GenericStart())
prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.FeedRate(feedrate))

param = { 
        'fileName'    : fileName,
        'layers'      : layerNames,
        'dxfTypes'    : ['CIRCLE'],
        'startZ'      : 0.00,
        'stopZ'       : -0.12,
        'safeZ'       : 0.3,
        'stepZ'       : 0.03,
        'startDwell'  : 2.0,
        }
drill = cnc_dxf.DxfDrill(param)
prog.add(drill)

prog.add(gcode_cmd.Space())
prog.add(gcode_cmd.End(),comment=True)
baseName, dummy = os.path.splitext(__file__)
fileName = '{0}.ngc'.format(baseName)
print('generating: {0}'.format(fileName))
prog.write(fileName)
