# building and applying transformation matrices 

import moderngl
import pyglet as pg
import numpy as np
from PIL import Image
from pyrr import Matrix44, Vector4
import os
import time

width = 640
height = 640
window = pg.window.Window(width, height, 'Transformations', resizable=False)

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader = '''
    # version 330 core
    
    uniform mat4 transform;
    in vec2 in_vert;
    in vec2 in_UVs;
    out vec2 v_UVs;
    
    void main()
    {
        gl_Position = transform * vec4(in_vert, 0.0, 1.0);
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

vertices = np.array([
    # x, y, u, v
    -0.5, -0.5, 0.0, 0.0,
    -0.5, 0.5, 0.0, 1.0,
    0.5, 0.5, 1.0, 1.0,
    0.5, -0.5, 1.0, 0.0,
    ])

indices = np.array([0, 1, 2, 0, 2, 3])

vbo = ctx.buffer(vertices.astype('f4').tobytes())
ibo = ctx.buffer(indices.astype('i4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_UVs', index_buffer=ibo)

img1 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_{size}x{size}.jpg'.format(size=512))) # texture sizes: 8,16,32,64,128,256,512,1024,2048,4096
img2 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Bulb.jpg'))

tex1 = ctx.texture(img1.size, 3, img1.tobytes()) # 3 for RGB
tex2 = ctx.texture(img2.size, 3, img2.tobytes())

tex1.use(0) # bind texture to 0 texture unit
tex2.use(1) # bind texture to 1 texture unit

# assign texture unit indexes
prog['myTexture1'].value = 0
prog['myTexture2'].value = 1


def update(dt):
    proj = Matrix44.perspective_projection(50, width / height, 0.1, 1000.0)
    rotX = Matrix44.from_x_rotation(0)
    rotY = Matrix44.from_y_rotation(time.clock()*1.5)
    rotZ = Matrix44.from_z_rotation(180 * np.pi / 180) # rotate 180 degrees. Convert degrees to radians
    trans = Matrix44.from_translation( [ np.sin(time.clock())/4, np.sin(time.clock())/4, -1.3 ] ) # bounce diagonally from corner to corner, move back by -1.3
    scale = Matrix44.from_scale([.5,.5,.5]) # uniformly scale by 0.5
    tMatrix = proj * trans * scale * rotX * rotY * rotZ
    prog['transform'].write(tMatrix.astype('f4').tobytes())
    ctx.clear(.1, .1, .1)
    vao.render()
    
pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()