# "rotating" rectangle with a repeating texture (2 image composite)

from OpenGL.GL import *
import moderngl
import pyglet as pg
import numpy as np
from PIL import Image
import os
import time

window = pg.window.Window(1000, 1000, 'Textures', resizable=False)

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader = '''
    # version 330 core
    
    uniform float scale;
    in vec2 in_vert;
    in vec2 in_UVs;
    out vec2 v_UVs;
    
    void main()
    {
        gl_Position = vec4(in_vert.x * scale, in_vert.y, 0.0, 1.0);
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
        // f_colour = vec4(texture2D(myTexture1, v_UVs).rgb, 1.0); // modernGL example (?)
        // f_colour = texture(myTexture1, v_UVs); // using GLSL's built-in "texture" function
        
        f_colour = texture(myTexture1, v_UVs) * texture(myTexture2, v_UVs); // combine 2 textures
    }
    ''',
    )

vertices = np.array([
    # x, y, u, v
    -0.8, -0.8, 0.0, 0.0,
    -0.8, 0.8, 0.0, 1.5,
    0.8, 0.8, 1.5, 1.5,
    0.8, -0.8, 1.5, 0.0,
    ])

indices = np.array([0, 1, 2, 0, 2, 3])

vbo = ctx.buffer(vertices.astype('f4').tobytes())
ibo = ctx.buffer(indices.astype('i4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_UVs', index_buffer=ibo)

img1 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_{size}x{size}.jpg'.format(size=512))) # texture sizes: 8,16,32,64,128,256,512,1024,2048,4096
img2 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Bulb.jpg')).transpose(Image.FLIP_TOP_BOTTOM) # PNG with Alpha didn't work - displays a black box

tex1 = ctx.texture(img1.size, 3, img1.tobytes()) # 3 for RGB
tex2 = ctx.texture(img2.size, 3, img2.tobytes())

tex1.use(0) # bind texture to 0 texture unit

# set texture wrapping
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
# set texture filtering
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # test for artifacts with low resolution textures

tex2.use(1) # bind texture to 1 texture unit

# assign texture unit indexes
prog['myTexture1'].value = 0
prog['myTexture2'].value = 1

def update(dt):
    prog['scale'].value = np.sin(time.clock())
    ctx.clear(.1, .1, .1)
    vao.render()
    
pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()