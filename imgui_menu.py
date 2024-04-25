import tkinter.messagebox
from array import array
import imgui
from math import sin, pi
from random import random
from time import time
from vistasset3d import *

histogram_values = None


def init_menu():
    global histogram_values
    histogram_values = array("f", [0 for _ in range(128)])


def draw_menu(Application):
    imgui.new_frame()

    # file open dialog
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_open, selected_open = imgui.menu_item("Open", "Ctrl+O", False, True)
            clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
            if clicked_open:
                Application.request_change_model()
            if clicked_quit:
                Application.quit_application()
            imgui.end_menu()
        if imgui.begin_menu("Help", True):
            clicked_about, selected_about = imgui.menu_item("About", "Ctrl+H", False, True)
            if clicked_about:
                tkinter.messagebox.showinfo("About", "This is a simple 3D model viewer using OpenGL and ImGui\nAuthor: Doyup Kim")
            imgui.end_menu()
        imgui.end_main_menu_bar()

    # Making ImGui tab to stick on the left side
    # its height is screen height - 20
    imgui.set_next_window_position(0, 20)
    imgui.set_next_window_size(200, 400)
    imgui.begin("Control Panel", False, imgui.WINDOW_NO_RESIZE)

    # radio buttens to change rendering mode

    radio_params = (
        ("Default", "DEFAULT"),
        ("Wireframe", "WIREFRAME"),
        ("Normal", "NORMAL"),
        ("UV", "UV")
    )

    imgui.text("View Mode")

    for label, mode in radio_params:
        clicked = imgui.radio_button(label, Application.view_mode == mode)
        if clicked:
            Application.view_mode = mode

    imgui.new_line()
    imgui.separator()

    # color picker to change background color
    Application.model_color = imgui.color_edit3("Model Color", *Application.model_color, imgui.COLOR_EDIT_NO_INPUTS)[1]
    Application.background_color = imgui.color_edit3("Background Color", *Application.background_color, imgui.COLOR_EDIT_NO_INPUTS)[1]

    imgui.end()

    # Making ImGui tab to stick on the right side
    # its height is fixed to 200
    imgui.set_next_window_position(imgui.get_io().display_size.x - 200, 20)
    imgui.set_next_window_size(200, 400)
    imgui.begin("Statistics", False, imgui.WINDOW_NO_RESIZE)

    # Model statistics
    imgui.text("Model Statistics")
    imgui.text("Vertices: %d" % len(Application.loaded_model.vertices))
    imgui.text("Indices: %d" % len(Application.loaded_model.indices))

    imgui.new_line()
    imgui.separator()

    fpms = imgui.get_io().framerate
    ftime = 1000 / fpms

    histogram_values[:-1] = histogram_values[1:]
    histogram_values[-1] = ftime

    # Performance statistics
    imgui.text("Performance")
    imgui.text("FPS: %d" % fpms)
    imgui.text("Frame Time: %.3f ms" % ftime)

    imgui.new_line()
    imgui.separator()

    imgui.plot_lines("", histogram_values, overlay_text="Frame Time Status", graph_size=(200, 200))
    imgui.end()
