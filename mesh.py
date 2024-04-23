from OpenGL.GL import *
import ctypes
import pyassimp as assimp
import numpy as np

class Mesh:
    def __init__(self, path=None):
        self.vao = None
        self.vbo = None
        self.ebo = None

        self.vertices = []
        self.colors = []
        self.normals = []
        self.uvs = []
        self.indices = []

        if path:
            self.load_data(path)
            self.gen_buffer()

    def __del__(self):
        # if self.vao:
        #     glDeleteVertexArrays(1, self.vao)
        # if self.vbo:
        #     glDeleteBuffers(4, self.vbo)
        # if self.ebo:
        #     glDeleteBuffers(1, self.ebo)
        pass

    def load_data(self, path):
        with assimp.load(path) as scene:
            if not scene:
                raise Exception("No mesh in file")
            mesh = scene.meshes[0]

        self.colors.extend((1.0, 0.0, 0.0))
        for i in range(len(mesh.vertices)):
            self.vertices.extend(mesh.vertices[i])
            self.colors.extend(mesh.normals[i])
            self.normals.extend(mesh.normals[i])
            if mesh.texturecoords.any():
                self.uvs.extend(mesh.texturecoords[0][i])
            else:
                self.uvs.extend((0.0, 0.0))

        for i in range(len(mesh.faces)):
            self.indices.extend(mesh.faces[i])

    def gen_buffer(self):
        np_vertices = np.array(self.vertices, dtype=np.float32)
        np_colors = np.array(self.colors, dtype=np.float32)
        np_normals = np.array(self.normals, dtype=np.float32)
        np_uvs = np.array(self.uvs, dtype=np.float32)
        np_indices = np.array(self.indices, dtype=np.uint32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(4)
        self.ebo = glGenBuffers(1)
        glBindVertexArray(self.vao)

        # position
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, np_vertices.nbytes, np_vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # color
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[1])
        glBufferData(GL_ARRAY_BUFFER, np_colors.nbytes, np_colors, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        # normals
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[2])
        glBufferData(GL_ARRAY_BUFFER, np_normals.nbytes, np_normals, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        # uv
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[3])
        glBufferData(GL_ARRAY_BUFFER, np_uvs.nbytes, np_uvs, GL_STATIC_DRAW)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(36))
        glEnableVertexAttribArray(3)

        # indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np_indices.nbytes, np_indices, GL_STATIC_DRAW)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)