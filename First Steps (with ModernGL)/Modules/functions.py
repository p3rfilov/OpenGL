import os
import sys
from pyrr import Matrix44
import numpy as np

class Math():
    @staticmethod
    def buildTransMatrix(pos=[0,0,0], rot=[0,0,0], scale=[1,1,1]):
        trans = Matrix44.from_translation(pos)
        rotX = Matrix44.from_x_rotation(np.radians(rot[0]))
        rotY = Matrix44.from_y_rotation(np.radians(rot[1]))
        rotZ = Matrix44.from_z_rotation(np.radians(rot[2]))
        scale = Matrix44.from_scale(scale)
        tMatrix = trans * scale * rotX * rotY * rotZ
        return tMatrix
    
class Path():
    @staticmethod
    def local(*path):
        return os.path.join(os.path.dirname(sys.argv[0]), *path)