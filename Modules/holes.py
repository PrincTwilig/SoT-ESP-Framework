"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import struct, array
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.image import SolidColorImagePattern
from helpers import OFFSETS, calculate_distance, object_to_screen, TEXT_OFFSET_Y, TEXT_OFFSET_X, main_batch, SOT_WINDOW_H, SOT_WINDOW_W
from Modules.display_object import DisplayObject


class Holes(DisplayObject):
    """
    Class to generate information about the crews current on our server
    """

    def __init__(self, memory_reader, actor_id, address, my_cords):
        """
        be located at the screen coordinated + our text_offsets from helpers.py
        The function of this class is to collect all of the data about the crews
        currently on our server. `CrewService` is effectively just a list of
        `Crew` structures in memory, which we will iterating over to collect the
        requisite data.

        Previously, you were able to collect player names from this data but we
        cannot any longer. Instead we will simply use it to get a count of how
        many players are on the server and on each crew.

        :param memory_reader: The SoT MemoryHelper Object we use to read memory
        :param actor_id: The actor ID of our CrewService. Used to validate if
        there is an unexpected change
        :param address: The address in which our CrewService lives
        """
        # Initialize our super-class
        super().__init__(memory_reader)

        self.rm = memory_reader
        self.actor_id = actor_id
        self.address = address
        self.my_coords = my_cords

        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)

        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        # Collect and store information about the crews on the server
        self.hulls_info = self._get_hulls_info()

        # All of our actual display information & rendering
        self.sink_percent = self._built_text_string()

        self.label = self._build_text_render()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _built_text_string(self):
        """
        Generates a string used for rendering. Separate function in the event
        you need to add more data or want to change formatting
        """
        output = f"{self._get_hulls_info()}"

        return output

    def _get_hulls_info(self):
        """
        Generates information about each of the crews on the server
        """




    def is_active_hall(self):
        arr_raw = self.rm.read_bytes(self.address + OFFSETS.get('HullDamage.ActiveHullDamageZones'), 0x10)
        array = struct.unpack("<Qii", arr_raw)

        if self.distance < 15:
            return array[1]
        else:
            return 0




    def _build_text_render(self) -> Label:
        """
        Function to build our actual label which is sent to Pyglet. Sets it to
        be located at the screen coordinated + our text_offsets from helpers.py

        Assigns the object to our batch & group

        :rtype: Label
        :return: What text we want displayed next to the ship
        """
        if self.screen_coords:
            return Label(self._built_text_string(),
                         x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y,
                         batch=main_batch, font_name='Times New Roman')

        return Label(self._built_text_string(), x=0, y=0, batch=main_batch)

    def update(self, my_coords):  # pylint: disable=unused-argument
        """
        A generic method to update all the interesting data about the
        crews on our server. To be called when seeking to perform an update on
        the CrewService actor without reinitializing our class.

        1. Determine if our actor is what we expect it to be
        2. Pull the latest crew information
        3. Update our strings accordingly
        """
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            return

        self.sink_percent = self._built_text_string()

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        new_distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        if self.screen_coords:

            self.label.visible = True
            # Update the position of our circle and text
            self.label.x = self.screen_coords[0] + TEXT_OFFSET_X
            self.label.y = self.screen_coords[1] + TEXT_OFFSET_Y + 280

            # Update our text to reflect out new distance
            self.distance = new_distance
            self.text_str = self._built_text_string()
            self.label.text = self.text_str


        else:
            # if it isn't on our screen, set it to invisible to save resources
            self.label.visible = False


        if self.distance < 15 and self._get_sink_info() < 0.8:
            self.healthbar.visible = True
            self.frame.visible = True

            self.healthbar.scale_x = self._get_sink_info()

            if self._get_sink_info() > 0.6:
                self.healthbar.color = (0, 255, 0)
            elif self._get_sink_info() > 0.2:
                self.healthbar.color = (255, 255, 0)
            else:
                self.healthbar.color = (255, 0, 0)
        else:
            self.healthbar.visible = False
            self.frame.visible = False
