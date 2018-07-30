# control camera movement through keyboard input
# use W, S, A, D, SPACE & LCTRL keys to move the camera

import moderngl
from OpenGL.GL import *
import pyglet as pg
from pyglet.window import key
import numpy as np
from PIL import Image
from pyrr import Matrix44, Vector4, Vector3
import pyrr
import os
import time

width = 1280
height = 720
window = pg.window.Window(width, height, 'Camera', resizable=False)
window.set_mouse_visible(False)
window.set_exclusive_mouse(False)
# window.push_handlers(pg.window.event.WindowEventLogger())

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader = '''
    # version 330 core
    
    uniform mat4 transform;
    in vec3 in_vert;
    in vec2 in_UVs;
    out vec2 v_UVs;
    
    void main()
    {
        gl_Position = transform * vec4(in_vert, 1.0);
        v_UVs = in_UVs;
    }
    ''',
    fragment_shader = '''
    # version 330 core
    
    uniform sampler2D myTexture1;
    uniform sampler2D myTexture2;
    
    in vec2 v_UVs;
    out vec4 f_colour;
    
    void main()
    {
        f_colour = texture(myTexture1, v_UVs) * texture(myTexture2, v_UVs); // combine 2 textures
    }
    ''',
    )

# building a cube
vertices = np.array([
    # x, y, z, u, v
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,

    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,

     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    ])

cubePositions = [np.random.uniform(-2.0,2.0,size=3) for i in range(1,30)] # scatter 30 boxes with a random coordinate between -2 and 2

vbo = ctx.buffer(vertices.astype('f4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_UVs')
img1 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_{size}x{size}.jpg'.format(size=512))) # texture sizes: 8,16,32,64,128,256,512,1024,2048,4096
img2 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Bulb.jpg'))
tex1 = ctx.texture(img1.size, 3, img1.tobytes()) # 3 for RGB
tex2 = ctx.texture(img2.size, 3, img2.tobytes())
tex1.use(0) # bind texture to 0 texture unit
tex2.use(1) # bind texture to 1 texture unit
# assign texture unit indexes
prog['myTexture1'].value = 0
prog['myTexture2'].value = 1

glEnable(GL_DEPTH_TEST)

cameraSpeed = 0.1
mouseSpeed = 0.3
cameraPos = Vector3([1.0, 1.0, -10.0])
cameraTarget = Vector3([0.0, 0.0, -1.0])
cameraUp = Vector3([0.0, 1.0, 0.0])
yaw = 0.0
pitch = 0.0
movement = Vector3([0, 0, 0])
rotation = (0, 0)

@window.event
def on_key_press(symbol, modifier):
    if symbol == key.W:
        movement[2] += 1
    if symbol == key.S:
        movement[2] -= 1
    if symbol == key.A:
        movement[0] += 1
    if symbol == key.D:
        movement[0] -= 1
    if symbol == key.SPACE:
        movement[1] += 1
    if symbol == key.LCTRL:
        movement[1] -= 1

@window.event        
def on_key_release(symbol, modifiers):
    if symbol == key.W:
        movement[2] -= 1
    if symbol == key.S:
        movement[2] += 1
    if symbol == key.A:
        movement[0] -= 1
    if symbol == key.D:
        movement[0] += 1
    if symbol == key.SPACE:
        movement[1] -= 1
    if symbol == key.LCTRL:
        movement[1] += 1
     
def updateCameraPosition():
    global cameraPos
    global cameraTarget
    cameraPos += movement * cameraSpeed
    cameraTarget += movement * cameraSpeed
     
# @window.event
# def on_mouse_motion(x, y, dx, dy):
#     global cameraTarget, yaw, pitch
#     yaw += dx
#     pitch -= dy
#     if pitch > 89.0: pitch = 89.0
#     if pitch < -89.0: pitch = -89.0
#     front = Vector3()
#     front.x = np.cos(np.radians(yaw)) * np.cos(np.radians(pitch))
#     front.y = np.sin(np.radians(pitch))
#     front.z = np.sin(np.radians(yaw)) * np.cos(np.radians(pitch))
#     cameraTarget = pyrr.vector.normalize(front)

def scatterCubes(vector, projectionMat):
    view = Matrix44.look_at(cameraPos, cameraTarget, cameraUp)
    r = vector[0] * 10.0 # cube rotation offset based on vector's 1st component
    rotX = Matrix44.from_x_rotation(r*time.clock()/10.0) # rotate cubes over time
    rotY = Matrix44.from_y_rotation(r)
    rotZ = Matrix44.from_z_rotation(r)
    trans = Matrix44.from_translation(vector) * Matrix44.from_translation([1.0,1.0,-5.0])
    scale = Matrix44.from_scale([.5,.5,.5]) # uniformly scale by 0.5
    tMatrix = projectionMat * view * trans * scale * rotX * rotY * rotZ
    prog['transform'].write(tMatrix.astype('f4').tobytes())

def update(dt):
    updateCameraPosition()
    proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
    ctx.clear(.1, .1, .1) # also clears depth buffer
    for vec in cubePositions: # render multiple cubes
        scatterCubes(vec, proj)
        vao.render()
    
pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()