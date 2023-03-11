from pyglet.text import Label
import pyglet
import time
import struct
import math
from helpers import calculate_distance, object_to_screen, main_batch, \
     TEXT_OFFSET_X, TEXT_OFFSET_Y, OFFSETS
from mapping import ships
from Modules.display_object import DisplayObject



class Seagull(DisplayObject):


    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)


    def update(self, my_coords: dict):
        self._abs_update(my_coords)
