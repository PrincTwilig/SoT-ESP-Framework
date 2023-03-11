import pyglet
from helpers import calculate_distance, object_to_screen, TEXT_OFFSET_Y, TEXT_OFFSET_X, main_batch
from Modules.display_object import DisplayObject

class Player(DisplayObject):

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)

        self.image = 'icons/player_frame.png'



    def build_frame_render(self):
        if self.screen_coords:
            image = pyglet.image.load(self.image)
            icon = pyglet.sprite.Sprite(image, batch=main_batch, x=self.screen_coords[0] + TEXT_OFFSET_X,y=self.screen_coords[1] + TEXT_OFFSET_Y)

            return icon

    def update(self, my_coords: dict):
        self._abs_update(my_coords)
