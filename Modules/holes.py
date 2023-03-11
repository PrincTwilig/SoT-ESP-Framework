import struct
from helpers import OFFSETS, calculate_distance, object_to_screen
from Modules.display_object import DisplayObject


class Holes(DisplayObject):

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)

        self.hulls_count = self._get_hulls_info()


    def _get_hulls_info(self):
        arr_raw = self.rm.read_bytes(self.address + OFFSETS.get('HullDamage.ActiveHullDamageZones'), 0x10)
        array = struct.unpack("<Qii", arr_raw)

        return array[1]


    def update(self, my_coords):
        if self._abs_update(my_coords):
            return

        self.hulls_count = self._get_hulls_info()
