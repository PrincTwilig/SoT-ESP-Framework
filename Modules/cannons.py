from pyglet.text import Label
import pyglet
import time
import struct
import math
from helpers import calculate_distance, object_to_screen, main_batch, \
     TEXT_OFFSET_X, TEXT_OFFSET_Y, OFFSETS
from mapping import ships
from Modules.display_object import DisplayObject


class Cannons(DisplayObject):


    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        super().__init__(memory_reader, actor_id, address, my_coords, raw_name)

        self.is_on_cannon = self._is_on_cannon()

        self.shot_distance = self._get_shot_distance()

        self.loaded_projectile = self._get_loaded_projectile()
        self.projectile_speed = self._get_projectile_speed()
        self.projectile_gravity = self._get_projectile_gravity()
        



    def _is_on_cannon(self):
        return True if self.distance == 1 else False
    
    def _get_shot_distance(self):
        v0 = self._get_projectile_speed()
        g = self._get_projectile_gravity() 

        return ((v0**2 * math.sin(2*math.radians(self.my_coords['cam_x']) if 2*math.radians(self.my_coords['cam_x']) > 0 else 0.01)) / g)
    
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
        if self._abs_update(my_coords):
            return
        


        self.is_on_cannon = self._is_on_cannon()
        self.shot_distance = self._get_shot_distance()

        self.loaded_projectile = self._get_loaded_projectile()
        self.projectile_speed = self._get_projectile_speed()
        self.projectile_gravity = self._get_projectile_gravity()

