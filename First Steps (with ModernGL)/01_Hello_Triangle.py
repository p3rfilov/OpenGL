# draw 2 triangles using indexed drawing

import moderngl
import pyglet as pg
import numpy as np

window = pg.window.Window(640, 480, 'Hello Triangle', resizable=False)

ctx = moderngl.create_context()
prog = ctx.program(
        vertex_shader='''
            #version 330 core

            in vec3 in_vert;     // x, y, z
            in vec3 in_color;    // r, g, b
            out vec3 v_color;    // Passed on to the fragment shader

            void main() {
                gl_Position = vec4(in_vert, 1.0); // added 4-th alpha component
                v_color = in_color;
            }
        ''',
        fragment_shader='''
            #version 330 core

            in vec3 v_color;
            out vec4 f_color;

            void main() {
                f_color = vec4(v_color, 1.0);
            }
        ''',
    )

vertices = np.array([
    # x, y, z, r, g, b
    0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
    -0.9, -0.9, 0.0, 0.0, 1.0, 0.0,
    0.9, -0.9, 0.0, 0.0, 0.0, 1.0,
    
    0.9, 0.9, 0.0, 1.0, 1.0, 1.0,
    -0.9, 0.9, 0.0, 0.5, 0.5, 0.5,
    ])
indices = np.array([0, 1, 2, 0, 3, 4])

vbo = ctx.buffer(vertices.astype('f4').tobytes())
ibo = ctx.buffer(indices.astype('i4').tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_color', index_buffer=ibo)

ctx.clear(.1, .1, .1)
vao.render()

pg.app.run()