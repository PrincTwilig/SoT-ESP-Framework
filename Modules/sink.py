"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.image import SolidColorImagePattern
from helpers import OFFSETS, calculate_distance, object_to_screen, TEXT_OFFSET_Y, TEXT_OFFSET_X, main_batch, SOT_WINDOW_H, SOT_WINDOW_W
from Modules.display_object import DisplayObject


class Sink(DisplayObject):
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
        self.water_info = self._get_sink_info()

        # All of our actual display information & rendering
        self.sink_percent_string = self.built_text_string()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def built_text_string(self):
        """
        Generates a string used for rendering. Separate function in the event
        you need to add more data or want to change formatting
        """
        output = f"{round(self._get_sink_info()*100,1)}%"

        return output

    def _get_sink_info(self):
        """
        Generates information about each of the crews on the server
        """
        water_amount = self.rm.read_float(self.address + OFFSETS.get('ShipInternalWater.WaterAmount'))
        max_water_amount = self.rm.read_float(self.address + OFFSETS.get('ShipInternalWater.InternalWaterParams') + OFFSETS.get('ShipInternalWaterParams.MaxWaterAmount'))

        water_percent = water_amount/max_water_amount

        return 1-water_percent

    def _build_healthbar_render(self):
        health_bar = Sprite(SolidColorImagePattern((255, 255, 255, 255)).create_image(500, 30), batch=main_batch, x=SOT_WINDOW_W/3, y=SOT_WINDOW_H/10, z=1)
        health_bar.x = SOT_WINDOW_W/3
        health_bar.y = SOT_WINDOW_H/10
        health_bar.z = 1
        return health_bar

    def _build_frame_render(self):
        frame = Sprite(SolidColorImagePattern((0, 0, 0, 255)).create_image(500, 30), batch=main_batch, x=SOT_WINDOW_W/3, y=SOT_WINDOW_H/10)
        frame.x = SOT_WINDOW_W/3
        frame.y = SOT_WINDOW_H/10
        return frame




    def _build_text_render(self) -> Label:
        """
        Function to build our actual label which is sent to Pyglet. Sets it to
        be located at the screen coordinated + our text_offsets from helpers.py

        Assigns the object to our batch & group

        :rtype: Label
        :return: What text we want displayed next to the ship
        """
        if self.screen_coords:
            return Label(self.built_text_string(),
                         x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y,
                         batch=main_batch, font_name='Times New Roman')

        return Label(self.built_text_string(), x=0, y=0, batch=main_batch)

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

        self.water_info = self._get_sink_info()
        self.sink_percent_string = self.built_text_string()

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)