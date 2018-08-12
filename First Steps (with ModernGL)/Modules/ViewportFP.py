from pyglet.window import Window
from pyglet.window import key
import numpy as np
import pyrr
from pyrr import Matrix44, Vector3

class ViewportFP(Window):
    '''
    Convenience class for creating a OpenGL window.
    Creates a First-person-type camera.
    Generates a perspective and look_at (view) matrices.
    Includes camera controls (W, S, A, D, SPACE, LCTRL & mouse)
    '''
    def __init__(self, width=1280, height=720, name='OpenGL Window', cameraSpeed=0.1, mouseSpeed=0.3, invertMouse=False, resizable=False, vsync=False):
        super().__init__(width, height, name, resizable=resizable, vsync=vsync)
        self.cameraSpeed = cameraSpeed
        self.mouseSpeed = mouseSpeed
        self.invertMouse = invertMouse
        self.cameraPos = Vector3([0.0, 0.0, 0.0])
        self.cameraTarget = Vector3([0.0, 0.0, -1.0])
        self.cameraUp = Vector3([0.0, 1.0, 0.0])
        self.worldUp = Vector3([0.0, 1.0, 0.0])
        self.yaw = -90.0
        self.pitch = 0.0
        self.pressedKeys = []
        
        self.set_mouse_visible(False)
        self.set_exclusive_mouse(True)
        
        # Matrices
        self.projection = Matrix44.perspective_projection(45.0, width / height, 0.1, 1000.0)
        self.view = Matrix44.look_at(self.cameraPos, self.cameraTarget, self.cameraUp)
    
    def getProjectionMatrix(self):
        return self.projection
    
    def getViewMatrix(self):
        return self.view
    
    def getCameraPosition(self):
        return self.cameraPos
    
    def on_key_press(self, symbol, modifier):
        '''Add the pressed key to the list to be later used in updateCameraPosition'''
        if symbol not in self.pressedKeys:
            self.pressedKeys.append(symbol)
        if symbol == key.ESCAPE: # EXIT APPLICATION
            from pyglet import app
            app.exit()
            
    def on_key_release(self, symbol, modifiers):
        if symbol in self.pressedKeys:
            self.pressedKeys.remove(symbol)
            
    def on_mouse_motion(self, x, y, dx, dy):
        '''Update camera target'''
        self.yaw += dx * self.mouseSpeed
        
        if self.invertMouse:
            self.pitch -= dy * self.mouseSpeed
        else:
            self.pitch += dy * self.mouseSpeed
        
        if self.pitch > 89.0: self.pitch = 89.0
        if self.pitch < -89.0: self.pitch = -89.0
        frontVec = Vector3()
        frontVec.x = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        frontVec.y = np.sin(np.radians(self.pitch))
        frontVec.z = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.cameraTarget = self.cameraPos + pyrr.vector.normalize(frontVec)
        
    def updateCameraPosition(self):
        '''Check pressed keys and update camera position accordingly'''
        if self.pressedKeys:
            frontVec = pyrr.vector.normalize(self.cameraTarget - self.cameraPos)
            sideVec = pyrr.vector.normalize(np.cross(frontVec, self.worldUp))
            if key.W in self.pressedKeys:
                self.cameraPos += frontVec * self.cameraSpeed
                self.cameraTarget += frontVec * self.cameraSpeed
            if key.S in self.pressedKeys:
                self.cameraPos -= frontVec * self.cameraSpeed
                self.cameraTarget -= frontVec * self.cameraSpeed
            if key.A in self.pressedKeys:
                self.cameraPos -= sideVec * self.cameraSpeed
                self.cameraTarget -= sideVec * self.cameraSpeed
            if key.D in self.pressedKeys:
                self.cameraPos += sideVec * self.cameraSpeed
                self.cameraTarget += sideVec * self.cameraSpeed
            if key.SPACE in self.pressedKeys:
                self.cameraPos += self.worldUp * self.cameraSpeed
                self.cameraTarget += self.worldUp * self.cameraSpeed
            if key.LCTRL in self.pressedKeys:
                self.cameraPos -= self.worldUp * self.cameraSpeed
                self.cameraTarget -= self.worldUp * self.cameraSpeed
                          
    def update(self):
        '''Call this method in the main loop'''
        self.updateCameraPosition()
        self.view = Matrix44.look_at(self.cameraPos, self.cameraTarget, self.cameraUp)

if __name__ == '__main__':
    from pyglet import app
    
    window = ViewportFP()
    app.run()
