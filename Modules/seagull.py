"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

from pyglet.text import Label
import pyglet
import time
import struct
import math
from helpers import calculate_distance, object_to_screen, main_batch, \
     TEXT_OFFSET_X, TEXT_OFFSET_Y, OFFSETS
from mapping import ships
from Modules.display_object import DisplayObject

SHIP_COLOR = (100, 0, 0)  # The color we want the indicator circle to be
CIRCLE_SIZE = 10  # The size of the indicator circle we want


class Seagull(DisplayObject):
    """
    Class to generate information for a ship object in memory
    """

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader)

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name

        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)


        # Used to track if the display object needs to be removed
        self.to_delete = False



    def update(self, my_coords: dict):
        if abs(self._get_actor_id(self.address) - self.actor_id) > 20:
            self.to_delete = True
            return


        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)
