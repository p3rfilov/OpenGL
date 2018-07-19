# working with colours and applying basic lighting

import moderngl
import numpy as np
import pyglet as pg
from pyglet.gl import *
from pyrr import Matrix44, Vector3

width = 1280
height = 720
window = pg.window.Window(width, height, 'Basic Lighting', resizable=False)

ctx = moderngl.create_context()

vs = '''
    # version 330 core
    
    in vec3 in_vert;
    uniform mat4 transform;
    
    void main()
    {
        gl_Position = transform * vec4(in_vert, 1.0);
    }
    '''

fs = '''
    # version 330 core
    
    out vec4 fragColour;
    uniform vec3 objectColour;
    uniform vec3 lightColour;
    
    void main()
    {
        fragColour = vec4(objectColour * lightColour, 1.0);
    }
    '''

prog = ctx.program(vertex_shader=vs, fragment_shader=fs)

vertices = np.array([
    # cube (x, y, z)
    -0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5,  0.5, -0.5,
     0.5,  0.5, -0.5,
    -0.5,  0.5, -0.5,
    -0.5, -0.5, -0.5,

    -0.5, -0.5,  0.5,
     0.5, -0.5,  0.5,
     0.5,  0.5,  0.5,
     0.5,  0.5,  0.5,
    -0.5,  0.5,  0.5,
    -0.5, -0.5,  0.5,

    -0.5,  0.5,  0.5,
    -0.5,  0.5, -0.5,
    -0.5, -0.5, -0.5,
    -0.5, -0.5, -0.5,
    -0.5, -0.5,  0.5,
    -0.5,  0.5,  0.5,

     0.5,  0.5,  0.5,
     0.5,  0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5, -0.5,  0.5,
     0.5,  0.5,  0.5,

    -0.5, -0.5, -0.5,
     0.5, -0.5, -0.5,
     0.5, -0.5,  0.5,
     0.5, -0.5,  0.5,
    -0.5, -0.5,  0.5,
    -0.5, -0.5, -0.5,

    -0.5,  0.5, -0.5,
     0.5,  0.5, -0.5,
     0.5,  0.5,  0.5,
     0.5,  0.5,  0.5,
    -0.5,  0.5,  0.5,
    -0.5,  0.5, -0.5,
    ])

glEnable(GL_DEPTH_TEST)

cameraPos = [1.0, 1.0, -3.0]
cameraFront = [0.0, 0.0, -1.0]
cameraUp = [0.0, 1.0, 0.0]
view = Matrix44.look_at(cameraPos, cameraFront, cameraUp)
proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)

lightCol = Vector3([1.0, 0.5, 0.0])

def buildTransMatrix(pos=[0,0,0], rot=[0,0,0], scale=[1,1,1]):
    trans = Matrix44.from_translation(pos)
    rotX = Matrix44.from_x_rotation(np.radians(rot[0]))
    rotY = Matrix44.from_y_rotation(np.radians(rot[1]))
    rotZ = Matrix44.from_z_rotation(np.radians(rot[2]))
    scale = Matrix44.from_scale(scale)
    tMatrix = trans * scale * rotX * rotY * rotZ
    return tMatrix

def drawBox():
    vbo = ctx.buffer(vertices.astype('f4').tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')
    tMatrix = proj * view * buildTransMatrix()
    prog['transform'].write(tMatrix.astype('f4').tobytes())
    objCol = Vector3([0.1, 0.5, 0.3])
    prog['objectColour'].write(objCol.astype('f4').tobytes())
    prog['lightColour'].write(lightCol.astype('f4').tobytes())
    vao.render()
    
def drawLight():
    vbo = ctx.buffer(vertices.astype('f4').tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')
    tMatrix = proj * view * buildTransMatrix(pos=[-1.7,0,-1], scale=[0.2, 0.2, 0.2])
    prog['transform'].write(tMatrix.astype('f4').tobytes())
    objCol = Vector3([1.0, 1.0, 1.0])
    prog['objectColour'].write(objCol.astype('f4').tobytes())
    prog['lightColour'].write(lightCol.astype('f4').tobytes())
    vao.render()

def update(dt):
    ctx.clear(.1, .1, .1)
    drawBox()
    drawLight()

pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()