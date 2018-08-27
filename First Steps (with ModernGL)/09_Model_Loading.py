'''
Loading OBJ models
'''

import os
import time
import moderngl
import numpy as np
import pyglet as pg
from pyglet.gl import *
from PIL import Image
from pyrr import Matrix33, Matrix44, Vector3
from objloader import Obj
from Modules.ViewportFP import ViewportFP
from Modules.functions import Math, Path

# light parameters 
lightPos = Vector3([5.0, 4.0, -5.0])
lightCol = Vector3([1.0, 1.0, 1.0])

window = ViewportFP()
ctx = moderngl.create_context()

vs = '''
    # version 330 core
    
    uniform mat4 MVP;
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
        vec3 normal = mat3(transpose(inverse(model))) * in_norm;
        fragNorm = normal;
        texCoords = in_UVs;
        gl_Position = MVP * vec4(in_vert, 1.0);
    }
    '''
    
fs = '''
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
        // ambient
        vec3 ambient = light.ambient * vec3(texture(material.diffuse, texCoords));
        
        // diffuse
        vec3 norm = normalize(fragNorm);
        vec3 lightDir = normalize(light.position - fragPos);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, texCoords));
        
        // specular
        vec3 viewDir = normalize(viewPos - fragPos);
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        vec3 specular = light.specular * spec * vec3(texture(material.specular, texCoords));
        
        vec3 result = ambient + diffuse + specular;
        fragColour = vec4(result, 1.0);
    }
    '''

prog = ctx.program(vertex_shader=vs, fragment_shader=fs)
glShadeModel(GL_SMOOTH)
glEnable(GL_DEPTH_TEST)

obj = Obj.open(Path.local('models', 'teapot.obj'))
vbo = ctx.buffer(obj.pack('vx vy vz nx ny nz tx ty'))
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_norm', 'in_UVs')

# light properties
pos = lightPos
amb = Vector3([0.2, 0.2, 0.2])
diff = Vector3([0.7, 0.7, 0.7])
spec = lightCol
prog['light.position'].write(pos.astype('f4').tobytes())
prog['light.ambient'].write(amb.astype('f4').tobytes())
prog['light.diffuse'].write(diff.astype('f4').tobytes())
prog['light.specular'].write(spec.astype('f4').tobytes())

# material properties
img1 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_{size}x{size}.jpg'.format(size=2048))) # texture sizes: 8,16,32,64,128,256,512,1024,2048,4096
tex1 = ctx.texture(img1.size, 3, img1.tobytes()) # 3 for RGB
tex1.build_mipmaps()
tex1.use(0) # bind texture to 0 texture unit
img2 = Image.open(os.path.join(os.path.dirname(__file__), 'images', 'Brick_Spec.jpg'))
tex2 = ctx.texture(img2.size, 3, img2.tobytes()) # 3 for RGB
tex2.build_mipmaps()
tex2.use(1) # bind texture to 1 texture unit
diff = Vector3([1.0, 0.5, 0.31])
spec = Vector3([0.5, 0.5, 0.5])
shine = 32.0
prog['material.diffuse'].value = 0 # texture unit 0
prog['material.specular'].value = 1 # texture unit 1
prog['material.shininess'].value = shine

def updateMesh():
    model = Math.buildTransMatrix(pos=[0, -1.0, -4.0], rot=[0, time.clock() * 25, 0], scale=[0.01, 0.01, 0.01]) # slowly rotate the model
    prog['model'].write(model.astype('f4').tobytes())
    mvp = window.getProjectionMatrix() * window.getViewMatrix() * model
    prog['MVP'].write(mvp.astype('f4').tobytes())
    camPos = window.getCameraPosition()
    prog['viewPos'].write(camPos.astype('f4').tobytes())
    vao.render()

def update(dt):
    window.update()
    ctx.clear(.1, .1, .1)
    updateMesh()

pg.clock.schedule_interval(update, 1.0 / 60.0)
pg.app.run()