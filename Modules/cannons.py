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


class Cannons(DisplayObject):
    """
    Class to generate information for a ship object in memory
    """

    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name, player_controller):
        """
        Upon initialization of this class, we immediately initialize the
        DisplayObject parent class as well (to utilize common methods)

        We then set our class variables and perform all of our info collecting
        functions, like finding the actors base address and converting the
        "raw" name to a more readable name per our Mappings. We also create
        a circle and label and add it to our batch for display to the screen.

        All of this data represents a "Ship". If you want to add more, you will
        need to add another class variable under __init__ and in the update()
        function

        :param memory_reader: The SoT MemoryHelper Object we use to read memory
        :param address: The address in which the AActor begins
        :param my_coords: a dictionary of the local players coordinates
        :param raw_name: The raw actor name used to translate w/ mapping.py
        """
        # Initialize our super-class
        super().__init__(memory_reader)

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name
        self.player_controller = player_controller

        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        self.is_on_cannon = self._is_on_cannon()

        self.shot_distance = self._get_shot_distance()

        self.loaded_projectile = self._get_loaded_projectile()
        self.projectile_speed = self._get_projectile_speed()
        self.projectile_gravity = self._get_projectile_gravity()
        


        # Used to track if the display object needs to be removed
        self.to_delete = False


    def _is_on_cannon(self):
        return True if self.distance == 1 else False
    
    def _get_shot_distance(self):
        manager = self.rm.read_ptr(
            self.player_controller + OFFSETS.get('PlayerController.CameraManager')
        )
        actor_bytes = self.rm.read_bytes(manager + OFFSETS.get('PlayerCameraManager.CameraCache') + OFFSETS.get('CameraCacheEntry.MinimalViewInfo'), 44)
        unpacked = struct.unpack("<ffffff16pf", actor_bytes)

        v0 = self._get_projectile_speed()
        g = self._get_projectile_gravity()

        return ((v0**2 * math.sin(2*math.radians(unpacked[3]) if 2*math.radians(unpacked[3]) > 0 else 0.01)) / g)
    
    def _get_projectile_gravity(self):
        if self._get_loaded_projectile() == 'BP_cmn_cannonball_chain_shot_01_a_ItemInfo_C':
            return 9.81
        else:
            gravity_scale = self.rm.read_float(self.address + OFFSETS.get('ACannon.ProjectileGravityScale'))
            return gravity_scale*9.81

    def _get_projectile_speed(self):
        projectile_speed = self.rm.read_float(self.address + OFFSETS.get('ACannon.ProjectileSpeed'))
        return projectile_speed/100

    def _get_loaded_projectile(self):
        item_address = self.rm.read_ptr(self.address + 1904)
        item_actor_id = self._get_actor_id(item_address)
        item_name = self.rm.read_gname(item_actor_id)
        return item_name
    
    def get_angle(self, distance):
        g = self._get_projectile_gravity()
        v0 = self._get_projectile_speed()
        
        numerator = g * distance
        denominator = v0 ** 2
        
        arcsine_argument = numerator / denominator
        theta = 0.5 * math.asin(arcsine_argument)
        
        return theta * 180/3.14
    
    def get_time_to_hit(self, distance):
        angle = self.get_angle(distance)

        g = self._get_projectile_gravity()
        v0 = self._get_projectile_speed()
        
        t = (2 * v0 * math.sin((3.14/180)*angle)) / g
        
        return t




    def update(self, my_coords: dict):
        if abs(self._get_actor_id(self.address) - self.actor_id) > 20:
            self.to_delete = True
            return


        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.is_on_cannon = self._is_on_cannon()
        self.shot_distance = self._get_shot_distance()

        self.loaded_projectile = self._get_loaded_projectile()
        self.projectile_speed = self._get_projectile_speed()
        self.projectile_gravity = self._get_projectile_gravity()


        self.screen_coords = object_to_screen(self.my_coords, self.coords)