"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import struct
from helpers import OFFSETS, calculate_distance, object_to_screen
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
        self.hulls_count = self._get_hulls_info()

        # All of our actual display information & rendering

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _get_hulls_info(self):
        """
        Generates information about each of the crews on the server
        """
        arr_raw = self.rm.read_bytes(self.address + OFFSETS.get('HullDamage.ActiveHullDamageZones'), 0x10)
        array = struct.unpack("<Qii", arr_raw)

        return array[1]


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

        self.hulls_count = self._get_hulls_info()

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)