# working with colours and applying basic lighting
# use W, S, A, D, SPACE & LCTRL keys or the mouse (click and drag) to move the light

import moderngl
import numpy as np
import pyglet as pg
from pyglet.gl import *
from pyglet.window import key, mouse
import pyrr
from pyrr import Matrix44, Vector3

width = 1280
height = 720
window = pg.window.Window(width, height, 'Basic Lighting', resizable=False)

ctx = moderngl.create_context()

vs_box = '''
    # version 330 core
    
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    layout (location = 0) in vec3 in_vert;
    layout (location = 1) in vec3 in_norm;
    out vec3 fragPos;
    out vec3 fragNorm;
    
    void main()
    {
        fragPos = vec3(model * vec4(in_vert, 1.0));
        fragNorm = in_norm;
        gl_Position = projection * view * model * vec4(in_vert, 1.0);
    }
    '''
    
fs_box = '''
    # version 330 core
    
    uniform vec3 objectColour;
    uniform vec3 lightColour;
    uniform vec3 lightPos;
    uniform vec3 viewPos;
    in vec3 fragPos;
    in vec3 fragNorm;
    out vec4 fragColour;
    
    void main()
    {
        float ambientStrength = 0.1;
        vec3 ambient = ambientStrength * lightColour;
        
        vec3 norm = normalize(fragNorm);
        vec3 lightDir = normalize(lightPos - fragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = diff * lightColour;
        
        float specularStrength = 0.5;
        vec3 viewDir = normalize(viewPos - fragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
        vec3 specular = specularStrength * spec * lightColour;
        
        vec3 result = (ambient + diffuse + specular) * objectColour;
        fragColour = vec4(result, 1.0);
    }
    '''
    
vs_light = '''
    # version 330 core
    
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    layout (location = 0) in vec3 in_vert;
    
    void main()
    {
        gl_Position = projection * view * model * vec4(in_vert, 1.0);
    }
    '''
    
fs_light = '''
    # version 330 core
    
    uniform vec3 lightColour;
    out vec4 fragColour;
    
    void main()
    {
        fragColour = vec4(lightColour, 1.0);
    }
    '''

box_prog = ctx.program(vertex_shader=vs_box, fragment_shader=fs_box)
light_prog = ctx.program(vertex_shader=vs_light, fragment_shader=fs_light)

vertices = np.array([
    # cube (x, y, z, Nx, Ny, Nz)
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0, 
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0, 

    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
     0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
     0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
    ])

glEnable(GL_DEPTH_TEST)

cameraSpeed = 0.2
cameraPos = Vector3([1.0, 2.0, -3.0])
cameraTarget = Vector3([0.5, 0.5, -1.0])
cameraUp = Vector3([0.0, 1.0, 0.0])
view = Matrix44.look_at(cameraPos, cameraTarget, cameraUp)
proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)

# light parameters 
lightPos = Vector3([1.0, 0.8,-1.8])
lightCol = Vector3([1.0, 1.0, 1.0])

@window.event
def on_key_press(symbol, modifier):
    global lightPos
    if symbol == key.W:
        lightPos.z += cameraSpeed
    if symbol == key.S:
        lightPos.z -= cameraSpeed
    if symbol == key.A:
        lightPos.x += cameraSpeed
    if symbol == key.D:
        lightPos.x -= cameraSpeed
    if symbol == key.SPACE:
        lightPos.y += cameraSpeed
    if symbol == key.LCTRL:
        lightPos.y -= cameraSpeed
        
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global lightPos
    if buttons & mouse.LEFT:
        lightPos.z += dy / 200
        lightPos.x -= dx / 200

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
    vao = ctx.simple_vertex_array(box_prog, vbo, 'in_vert', 'in_norm')
    model = buildTransMatrix()
    box_prog['projection'].write(proj.astype('f4').tobytes())
    box_prog['view'].write(view.astype('f4').tobytes())
    box_prog['model'].write(model.astype('f4').tobytes())
    objCol = Vector3([1.0, 0.5, 0.31])
    box_prog['objectColour'].write(objCol.astype('f4').tobytes())
    box_prog['lightColour'].write(lightCol.astype('f4').tobytes())
    box_prog['lightPos'].write(lightPos.astype('f4').tobytes())
    box_prog['viewPos'].write(cameraPos.astype('f4').tobytes())
    vao.render()
    
def drawLight():
    vbo = ctx.buffer(vertices.astype('f4').tobytes())
    vao = ctx.simple_vertex_array(light_prog, vbo, 'in_vert')
    # skip normal vector data by providing a stride value
    # each position value is a 32-bit float (4 bytes)
    # 6 data values per vertex
    # 4 * 6 = 24
    vao.bind(0, 'f', vbo, '4f', stride=24)
    model = buildTransMatrix(pos=lightPos, scale=[0.1, 0.1, 0.1])
    light_prog['projection'].write(proj.astype('f4').tobytes())
    light_prog['view'].write(view.astype('f4').tobytes())
    light_prog['model'].write(model.astype('f4').tobytes())
    objCol = Vector3([1.0, 1.0, 1.0])
    light_prog['lightColour'].write(lightCol.astype('f4').tobytes())
    vao.render()

def update(dt):
    ctx.clear(.1, .1, .1)
    drawBox()
    drawLight()

pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()