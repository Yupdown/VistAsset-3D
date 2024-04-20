#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
from imgui.integrations.glfw import GlfwRenderer
from math import sin, pi
from random import random
from time import time
from OpenGL.GL import *
import glm
import numpy as np
import glfw
import imgui
import sys
import ctypes
import pyassimp as assimp

C = 0.01
L = int(pi * 2 * 100)


def gen_buffer():
    vertices = []
    colors = []
    normals = []
    uvs = []
    indices = []

    with assimp.load("Resources/yup.obj") as scene:
        mesh = scene.meshes[0]

    colors.extend((1.0, 0.0, 0.0))

    for i in range(len(mesh.vertices)):
        vertices.extend(mesh.vertices[i])
        colors.extend(mesh.normals[i])
        normals.extend(mesh.normals[i])
        uvs.extend(mesh.texturecoords[0][i])

    for i in range(len(mesh.faces)):
        indices.extend(mesh.faces[i])

    vertices = np.array(vertices, dtype=np.float32)
    colors = np.array(colors, dtype=np.float32)
    normals = np.array(normals, dtype=np.float32)
    uvs = np.array(uvs, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(4)
    ebo = glGenBuffers(1)
    glBindVertexArray(vao)

    # position
    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # color
    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    # normals
    glBindBuffer(GL_ARRAY_BUFFER, vbo[2])
    glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(24))
    glEnableVertexAttribArray(2)

    # uv
    glBindBuffer(GL_ARRAY_BUFFER, vbo[3])
    glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)
    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(36))
    glEnableVertexAttribArray(3)

    # indices
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return vao, len(mesh.faces) * 3


def gen_global_vbo():
    guid = glGenBuffers(1)
    glBindBuffer(GL_UNIFORM_BUFFER, guid)
    glBufferData(GL_UNIFORM_BUFFER, 128, None, GL_STATIC_DRAW)
    glBindBuffer(GL_UNIFORM_BUFFER, 0)
    glBindBufferBase(GL_UNIFORM_BUFFER, 0, guid)

    return guid


def gen_shader():
    # load glsl from file
    vertex_shader = open("Resources/vertex.glsl").read()
    fragment_shader = open("Resources/fragment.glsl").read()

    vertex = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex, vertex_shader)
    glCompileShader(vertex)

    fragment = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment, fragment_shader)
    glCompileShader(fragment)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex)
    glAttachShader(shader_program, fragment)
    glLinkProgram(shader_program)

    glDeleteShader(vertex)
    glDeleteShader(fragment)

    return shader_program


def destroy_buffer():
    glDeleteBuffers(1)
    glDeleteVertexArrays(1)


def main():
    window = impl_glfw_init()
    imgui.create_context()
    impl = GlfwRenderer(window)

    vao, num_indices = gen_buffer()
    shader_program = gen_shader()
    guid = gen_global_vbo()

    plot_values = array("f", [sin(x * C) for x in range(L)])
    histogram_values = array("f", [random() for _ in range(20)])

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        imgui.begin("Plot example")
        imgui.plot_lines(
            "Sin(t)",
            plot_values,
            overlay_text="SIN() over time",
            # offset by one item every milisecond, plot values
            # buffer its end wraps around
            values_offset=int(time() * 100) % L,
            # 0=autoscale => (0, 50) = (autoscale width, 50px height)
            graph_size=(0, 50),
        )

        imgui.plot_histogram(
            "histogram(random())",
            histogram_values,
            overlay_text="random histogram",
            # offset by one item every milisecond, plot values
            # buffer its end wraps around
            graph_size=(0, 50),
        )

        imgui.end()

        screen_size = imgui.get_io().display_size
        aspect_ratio = screen_size.x / screen_size.y

        glClearColor(1.0, 1.0, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, int(screen_size.x), int(screen_size.y))

        glUseProgram(shader_program)

        worldMatrix = glm.mat4(1.0)
        worldMatrix = glm.rotate(worldMatrix, glfw.get_time(), glm.vec3(0, 1, 0))

        viewMatrix = glm.lookAt(glm.vec3(0, 10, 10), glm.vec3(0, 4, 0), glm.vec3(0, 1, 0))
        projectionMatrix = glm.perspective(glm.radians(45), aspect_ratio, 0.1, 100.0)

        # update global uniform buffer
        glBindBuffer(GL_UNIFORM_BUFFER, guid)
        glBufferSubData(GL_UNIFORM_BUFFER, 0, 64, glm.value_ptr(viewMatrix))
        glBufferSubData(GL_UNIFORM_BUFFER, 64, 64, glm.value_ptr(projectionMatrix))
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

        modelLocation = glGetUniformLocation(shader_program, "model_Transform")
        glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm.value_ptr(worldMatrix))

        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, None)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    # Enable Multi Sample Anti Aliasing
    glfw.window_hint(glfw.SAMPLES, 8)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


if __name__ == "__main__":
    main()