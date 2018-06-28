# change triangle's colour over time by passing data
# to a uniform variable in the fragment shader

import moderngl
import numpy as np
import pyglet as pg
import time

window = pg.window.Window(640, 480, 'Shaders', resizable=False)

ctx = moderngl.create_context()
prog = ctx.program(
    vertex_shader = '''
    # version 330 core
    
    in vec2 in_vert;
    
    void main()
    {
        gl_Position = vec4(in_vert, 0.0, 1.0);
    }
    ''',
    fragment_shader = '''
    # version 330 core
    
    uniform vec4 ourColour;
    out vec4 fragColour;
    
    void main()
    {
        fragColour = ourColour;
    }
    ''',
    )

vertices = np.array([
    0.0, 0.5,
    -0.5, -0.5,
    0.5, -0.5,
    ])

vbo = ctx.buffer(vertices.astype('f4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

def changeColour(prog):
    col = np.sin(time.clock())
    prog['ourColour'].value = (.9, col, .1, 1.0)

def update(dt):
    changeColour(prog)
    ctx.clear(.1, .1, .1)
    vao.render()
    
pg.clock.schedule_interval(update, 0.05)
pg.app.run()