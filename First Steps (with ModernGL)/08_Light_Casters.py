# lighting textured primitives
# apply diffuse and specular maps
# move the mouse while holding LEFT or RIGHT button to control the light

import os
import moderngl
import numpy as np
import pyglet as pg
from pyglet.gl import *
from pyglet.window import key, mouse
import pyrr
from pyrr import Matrix44, Vector3
from PIL import Image
import time

width = 1280
height = 720
window = pg.window.Window(width, height, 'Light Casters', resizable=False)

ctx = moderngl.create_context()

vs_box = '''
    # version 330 core
    
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    
    layout (location = 0) in vec3 in_vert;
    layout (location = 1) in vec3 in_norm;
    layout (location = 2) in vec2 in_UVs;
    
    out vec3 fragPos;
    out vec3 fragNorm;
    out vec2 texCoords;
    
    void main()
    {
        fragPos = vec3(model * vec4(in_vert, 1.0));
        vec3 normal = mat3(transpose(inverse(model))) * in_norm; // due to cube's rotation, we need to transform the normal
        fragNorm = normal;
        texCoords = in_UVs;
        gl_Position = projection * view * model * vec4(in_vert, 1.0);
    }
    '''
    
fs_box = '''
    # version 330 core
    
    struct Material
    {
        sampler2D diffuse; // unit 0
        sampler2D specular; // unit 1
        float shininess;
    };
    
    struct Light
    {
        vec3 position;
        
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    };
    
    uniform Material material;
    uniform Light light;
    uniform vec3 viewPos;
    
    in vec3 fragPos;
    in vec3 fragNorm;
    in vec2 texCoords;
    out vec4 fragColour;
    
    void main()
    {
        // light attenuation
        float constant = 1.0;
        float linear = 0.35;
        float quadratic = 0.44;
        float distance = length(light.position - fragPos);
        float attenuation = 1.0 / (constant + linear * distance + quadratic * (distance * distance));
        
        // ambient
        vec3 ambient = light.ambient * vec3(texture(material.diffuse, texCoords));
        ambient *= attenuation;
        
        // diffuse
        vec3 norm = normalize(fragNorm);
        vec3 lightDir = normalize(light.position - fragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, texCoords));
        diffuse *= attenuation;
        
        // specular
        vec3 viewDir = normalize(viewPos - fragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        vec3 specular = light.specular * spec * vec3(texture(material.specular, texCoords));
        specular *= attenuation;
        
        vec3 result = ambient + diffuse + specular;
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
    # positions        # normals         # texture coords
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,
     0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
     0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,
     0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 0.0,
     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0,  0.0, 1.0,   0.0, 0.0,

    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,
    -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0, 1.0,
    -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0, 0.0,
    -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0, 0.0,

     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0, 1.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0, 1.0,
     0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0, 1.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
     0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0,
     0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0, 1.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
     0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0, 1.0
    ])

glEnable(GL_DEPTH_TEST)

cameraSpeed = 0.2
cameraPos = Vector3([1.0, 2.0, -3.0])
cameraTarget = Vector3([0.5, 0.5, -1.0])
cameraUp = Vector3([0.0, 1.0, 0.0])
view = Matrix44.look_at(cameraPos, cameraTarget, cameraUp)
proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)

# light parameters 
lightPos = Vector3([-0.8, -0.4, -0.3])
lightCol = Vector3([1.0, 1.0, 1.0])
        
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global lightPos
    if buttons & mouse.LEFT:
        lightPos.z += dy / 200
        lightPos.x -= dx / 200
    if buttons & mouse.RIGHT:
        lightPos.y += dy / 200

def buildTransMatrix(pos=[0,0,0], rot=[0,0,0], scale=[1,1,1]):
    trans = Matrix44.from_translation(pos)
    rotX = Matrix44.from_x_rotation(np.radians(rot[0]))
    rotY = Matrix44.from_y_rotation(np.radians(rot[1]))
    rotZ = Matrix44.from_z_rotation(np.radians(rot[2]))
    scale = Matrix44.from_scale(scale)
    tMatrix = trans * scale * rotX * rotY * rotZ
    return tMatrix

def loadTextures():
    img1 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_{size}x{size}.jpg'.format(size=512))) # texture sizes: 8,16,32,64,128,256,512,1024,2048,4096
    tex1 = ctx.texture(img1.size, 3, img1.tobytes()) # 3 for RGB
    tex1.use(0) # bind texture to 0 texture unit
    img2 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_Spec.jpg'))
    tex2 = ctx.texture(img2.size, 3, img2.tobytes()) # 3 for RGB
    tex2.use(1) # bind texture to 1 texture unit

def drawBox():
    vbo = ctx.buffer(vertices.astype('f4').tobytes())
    vao = ctx.simple_vertex_array(box_prog, vbo, 'in_vert', 'in_norm', 'in_UVs')
    
    model = buildTransMatrix(rot=[0, time.clock() * 25, 0]) # slowly rotate the cube
    box_prog['projection'].write(proj.astype('f4').tobytes())
    box_prog['view'].write(view.astype('f4').tobytes())
    box_prog['model'].write(model.astype('f4').tobytes())
    box_prog['viewPos'].write(cameraPos.astype('f4').tobytes())
    
    # light properties
    pos = lightPos
    amb = Vector3([0.2, 0.2, 0.2])
    diff = Vector3([0.7, 0.7, 0.7])
    spec = lightCol
    box_prog['light.position'].write(pos.astype('f4').tobytes())
    box_prog['light.ambient'].write(amb.astype('f4').tobytes())
    box_prog['light.diffuse'].write(diff.astype('f4').tobytes())
    box_prog['light.specular'].write(spec.astype('f4').tobytes())
    
    # material properties
    diff = Vector3([1.0, 0.5, 0.31])
    spec = Vector3([0.5, 0.5, 0.5])
    shine = 32.0
    box_prog['material.diffuse'].value = 0 # texture unit 0
    box_prog['material.specular'].value = 1 # texture unit 1
    box_prog['material.shininess'].value = shine
    
    vao.render()
    
def drawLight():
    vbo = ctx.buffer(vertices.astype('f4').tobytes())
    vao = ctx.simple_vertex_array(light_prog, vbo, 'in_vert')
    # skip normal vector and texture coordinates data
    # each position value is a 32-bit float (4 bytes)
    # 8 data values per vertex
    vao.bind(0, 'f', vbo, '4f', stride = 4*8)
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

loadTextures()
pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()