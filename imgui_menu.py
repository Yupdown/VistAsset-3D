from array import array
import imgui
from math import sin, pi
from random import random
from time import time
from vistasset3d import *

C = 0.01
L = int(pi * 2 * 100)

plot_values = None
histogram_values = None


def init_menu():
    global plot_values, histogram_values

    plot_values = array("f", [sin(x * C) for x in range(L)])
    histogram_values = array("f", [random() for _ in range(20)])


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