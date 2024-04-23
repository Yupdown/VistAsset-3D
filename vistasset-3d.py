#!/usr/bin/env python
# -*- coding: utf-8 -*-

from array import array
from imgui.integrations.glfw import GlfwRenderer
from math import sin, pi
from random import random
from time import time
from OpenGL.GL import *
import glm
import glfw
import imgui
import sys
import mesh
from tkinter import filedialog
import logging

C = 0.01
L = int(pi * 2 * 100)
logging.basicConfig(level=logging.INFO)


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


def open_file():
    # open 'extensions.txt' file and read all extensions

    with open("extensions.txt", "r") as file:
        extensions_str = file.read()

    extensions = [("Assimp Assets", extensions_str), ("All Files", ".*")]
    file_path = filedialog.askopenfilename(title="Open Model File", filetypes=extensions)
    return file_path


def main():
    window = impl_glfw_init()
    imgui.create_context()
    impl = GlfwRenderer(window)

    model = mesh.Mesh("Resources/mesh/yup.obj")
    shader_program = gen_shader()
    guid = gen_global_vbo()

    plot_values = array("f", [sin(x * C) for x in range(L)])
    histogram_values = array("f", [random() for _ in range(20)])

    glEnable(GL_MULTISAMPLE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    mouse_pos_current = (0, 0)
    mouse_pos_last = (0, 0)
    mouse_pos_drag = (0, 0)
    mouse_scroll_integral = 0

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        io = imgui.get_io()
        mouse_pos_last = mouse_pos_current
        mouse_pos_current = io.mouse_pos.x, io.mouse_pos.y

        # if mouse is not captured by imgui, we can drag the model.
        if not io.want_capture_mouse:
            if io.mouse_down[0]:
                mouse_pos_drag = (
                    mouse_pos_drag[0] + mouse_pos_current[0] - mouse_pos_last[0],
                    mouse_pos_drag[1] + mouse_pos_current[1] - mouse_pos_last[1])
            mouse_scroll_integral += io.mouse_wheel
        imgui.new_frame()

        # file open dialog
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_open, selected_open = imgui.menu_item("Open", "Ctrl+O", False, True)
                clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
                if clicked_open:
                    file_path = open_file()
                    if file_path:
                        model.delete_buffers()
                        model = mesh.Mesh(file_path)
                if clicked_quit:
                    glfw.set_window_should_close(window, True)
                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.begin("Plot example")
        imgui.plot_lines(
            "Sin(t)",
            plot_values,
            overlay_text="SIN() over time",
            # offset by one item every milisecond, plot values
            # buffer its end wraps around
            values_offset=int(time() * 1000) % L,
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

        screen_size = io.display_size
        aspect_ratio = screen_size.x / screen_size.y if screen_size.y != 0.0 else 1.0

        glClearColor(1.0, 1.0, 1.0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, int(screen_size.x), int(screen_size.y))

        glUseProgram(shader_program)


        worldMatrix = glm.scale(glm.mat4(1), glm.vec3(0.5 / model.radius))
        worldMatrix = glm.rotate(worldMatrix, mouse_pos_drag[1] * 0.01, glm.vec3(1, 0, 0))
        worldMatrix = glm.rotate(worldMatrix, mouse_pos_drag[0] * 0.01, glm.vec3(0, 1, 0))
        worldMatrix = glm.translate(worldMatrix, -glm.vec3(model.center))

        viewMatrix = glm.lookAt(glm.vec3(0, 1, 1), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        projectionMatrix = glm.perspective(glm.radians(45), aspect_ratio, 0.1, 100.0)

        # update global uniform buffer
        glBindBuffer(GL_UNIFORM_BUFFER, guid)
        glBufferSubData(GL_UNIFORM_BUFFER, 0, 64, glm.value_ptr(viewMatrix))
        glBufferSubData(GL_UNIFORM_BUFFER, 64, 64, glm.value_ptr(projectionMatrix))
        glBindBuffer(GL_UNIFORM_BUFFER, 0)

        modelLocation = glGetUniformLocation(shader_program, "model_Transform")
        glUniformMatrix4fv(modelLocation, 1, GL_FALSE, glm.value_ptr(worldMatrix))

        glBindVertexArray(model.vao)
        glDrawElements(GL_TRIANGLES, len(model.indices), GL_UNSIGNED_INT, None)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "VistAsset 3D"

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