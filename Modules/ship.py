from pyglet.text import Label
import pyglet
import time
import math
from helpers import calculate_distance, object_to_screen, main_batch, \
     TEXT_OFFSET_X, TEXT_OFFSET_Y
from mapping import ships
from Modules.display_object import DisplayObject


class Ship(DisplayObject):
    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)

        self.name = ships.get(self.raw_name).get("Name")

        self.is_bot = True if "AI" in self.raw_name else False

        self.img_path = ships.get(self.raw_name).get('Icon')
        self.image = pyglet.image.load(self.img_path)
        self.text_str = self.built_text_string()

        self.sink_data = False
        self.halls = False


        self.speed = 0
        self.speed_x = 0
        self.speed_y = 0
        self.last_check = [time.monotonic()]
        self.last_coords = [self.coords]


        

    def build_icon_render(self) -> pyglet.sprite.Sprite:

        if self.screen_coords:
            icon = pyglet.sprite.Sprite(self.image, batch=main_batch)

            icon.x = self.screen_coords[0] + TEXT_OFFSET_X
            icon.y = self.screen_coords[1] + TEXT_OFFSET_X
            return icon

        return pyglet.sprite.Sprite(self.image, batch=main_batch)


    def add_sink_data(self, sink_data):
        self.sink_data = sink_data

    def add_halls_data(self, halls):
        self.halls = halls

    def built_text_string(self) -> str:
        if "AI" in self.raw_name:
            return f"AI - {self.distance}m"
        else:
            return f" - {self.distance}m"
        

    def _get_speed(self, now):
        distance = math.sqrt((self.coords['x']-self.last_coords[0]['x'])**2 + (self.coords['y']-self.last_coords[0]['y'])**2)
        speed = distance / (now - self.last_check[0])

        return speed
    
    def _get_directional_speed(self, now):
        self.speed_x = (self.coords['x'] - self.last_coords[0]['x']) / (now - self.last_check[0])
        self.speed_y = (self.coords['y'] - self.last_coords[0]['y']) / (now - self.last_check[0])

    def predict_coords(self, time_interval):
        predicted_x = self.coords['x'] + self.speed_x * (time_interval)
        predicted_y = self.coords['y'] + self.speed_y * (time_interval)

        return {'x': predicted_x, 'y': predicted_y, 'z': self.coords['z']}

    def build_text_render(self) -> Label:
        if self.screen_coords:
            return Label(self.text_str,
                         x=self.screen_coords[0] + TEXT_OFFSET_X + 40,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y + 30,
                         batch=main_batch, font_name='Times New Roman', multiline=True, width=100, font_size=14)

        return Label(self.text_str, x=0, y=0, batch=main_batch)

    def update(self, my_coords: dict):
        if self._abs_update(my_coords):
            return
        if "Proxy" not in self.raw_name and self.distance > 1750:
            self.to_delete = True
            return
        if "Proxy" in self.raw_name and self.distance < 1750:
            self.to_delete = True
            return

        now = time.monotonic()
        if now - self.last_check[-1] >= 0.5:
            if len(self.last_coords) >= 2 or len(self.last_check) >= 2:
                self.last_coords.pop(0)
                self.last_check.pop(0)

            self.speed = self._get_speed(now)
            self._get_directional_speed(now)

            self.last_check.append(now)
            self.last_coords.append(self.coords)


