"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

from pyglet.text import Label
from pyglet.shapes import Circle
import pyglet
from helpers import calculate_distance, object_to_screen, main_batch, \
     TEXT_OFFSET_X, TEXT_OFFSET_Y
from mapping import ships
from Modules.display_object import DisplayObject
from helpers import OFFSETS

SHIP_COLOR = (100, 0, 0)  # The color we want the indicator circle to be
CIRCLE_SIZE = 10  # The size of the indicator circle we want


class Player(DisplayObject):
    """
    Class to generate information for a ship object in memory
    """

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        # Initialize our super-class
        super().__init__(memory_reader)

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name

        # Generate our Ship's info
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        # All of our actual display information & rendering
        self.text_str = self._get_text_str()
        self.text_render = self._build_text_render()
        self.icon_render = self._build_icon_render()


        # Used to track if the display object needs to be removed
        self.to_delete = False



    def _get_text_str(self):
        return f""

    def _build_icon_render(self):
        if self.screen_coords:
            frame = pyglet.shapes.Rectangle(x=self.screen_coords[0] + TEXT_OFFSET_X, y=self.screen_coords[1] + TEXT_OFFSET_Y, width=10, height=20,
                                        color=(255, 0, 0), batch=main_batch)
            return frame

        return pyglet.shapes.Rectangle(x=0, y=0, width=10, height=20,
                                        color=(255, 0, 0), batch=main_batch)




    def _build_text_render(self) -> Label:
        if self.screen_coords:
            return Label(self.text_str,
                         x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y,
                         batch=main_batch, font_name='Times New Roman')

        return Label(self.text_str, x=0, y=0, batch=main_batch)

    def update(self, my_coords: dict):
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            self.text_render.delete()
            return

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        new_distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)


        if self.screen_coords:

            self.text_render.visible = True
            self.icon_render.visible = True

            self.text_render.x = self.screen_coords[0] + TEXT_OFFSET_X
            self.text_render.y = self.screen_coords[1] + TEXT_OFFSET_Y

            self.icon_render.y = self.screen_coords[1] + TEXT_OFFSET_Y
            self.icon_render.x = self.screen_coords[0] + TEXT_OFFSET_X

            self.distance = new_distance
            self.text_render.text = self.text_str

        else:
            self.text_render.visible = False
            self.icon_render.visible = False

