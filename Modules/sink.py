from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.image import SolidColorImagePattern
from helpers import OFFSETS, calculate_distance, object_to_screen, TEXT_OFFSET_Y, TEXT_OFFSET_X, main_batch, SOT_WINDOW_H, SOT_WINDOW_W
from Modules.display_object import DisplayObject


class Sink(DisplayObject):

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)

        self.water_info = self._get_sink_info()

        self.sink_percent_string = self.built_text_string()


    def built_text_string(self):
        output = f"{round(self._get_sink_info()*100,1)}%"

        return output

    def _get_sink_info(self):
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
        if self.screen_coords:
            return Label(self.built_text_string(),
                         x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y,
                         batch=main_batch, font_name='Times New Roman')

        return Label(self.built_text_string(), x=0, y=0, batch=main_batch)

    def update(self, my_coords):
        self._abs_update(my_coords)

        self.water_info = self._get_sink_info()
        self.sink_percent_string = self.built_text_string()
