import struct
import logging
from memory_helper import ReadMemory
from mapping import ship_keys, sink_keys, hull_keys, cannons_keys, seagulls_keys, players_keys
from helpers import OFFSETS, logger, calculate_distance, GameData
from Modules.ship import Ship
from Modules.sink import Sink
from Modules.holes import Holes
from Modules.players import Player
from Modules.cannons import Cannons
from Modules.seagull import Seagull


ACTOR_CLASSES = {
    **({raw_name: Cannons for raw_name in cannons_keys}),
    **({raw_name: Seagull for raw_name in seagulls_keys}),
    **({raw_name: Ship for raw_name in ship_keys}),
    **({raw_name: Sink for raw_name in sink_keys}),
    **({raw_name: Holes for raw_name in hull_keys}),
    **({raw_name: Player for raw_name in players_keys})
}


class SoTMemoryReader:

    def __init__(self):
        self.rm = ReadMemory("SoTGame.exe")
        base_address = self.rm.base_address
        logging.info(f"Process ID: {self.rm.pid}")

        u_world_offset = self.rm.read_ulong(
            base_address + self.rm.u_world_base + 3
        )
        u_world = base_address + self.rm.u_world_base + u_world_offset + 7
        self.world_address = self.rm.read_ptr(u_world)

        g_name_offset = self.rm.read_ulong(
            base_address + self.rm.g_name_base + 3
        )
        g_name = base_address + self.rm.g_name_base + g_name_offset + 7
        logging.info(f"SoT gName Address: {hex(g_name)}")
        self.g_name = self.rm.read_ptr(g_name)

        g_objects_offset = self.rm.read_ulong(
            base_address + self.rm.g_object_base + 2
        )
        g_objects = base_address + self.rm.g_object_base + g_objects_offset + 22
        logging.info(f"SoT gObject Address: {hex(g_objects)}")
        self.g_objects = self.rm.read_ptr(g_objects)

        self.u_level = self.rm.read_ptr(self.world_address +
                                        OFFSETS.get('World.PersistentLevel'))

        self.u_local_player = self._load_local_player()
        self.player_controller = self.rm.read_ptr(
            self.u_local_player + OFFSETS.get('LocalPlayer.PlayerController')
        )

        self.my_coords = self._coord_builder(self.u_local_player)
        self.my_coords['fov'] = 90

        self.actor_name_map = {}
        self.server_players = []
        self.local_ship = False
        self.display_objects = []

        self.data = GameData()


    def _load_local_player(self) -> int:
        game_instance = self.rm.read_ptr(
            self.world_address + OFFSETS.get('World.OwningGameInstance')
        )
        local_player = self.rm.read_ptr(
            game_instance + OFFSETS.get('GameInstance.LocalPlayers')
        )
        return self.rm.read_ptr(local_player)

    def update_my_coords(self):
        manager = self.rm.read_ptr(
            self.player_controller + OFFSETS.get('PlayerController.CameraManager')
        )
        self.my_coords = self._coord_builder(
            manager,
            OFFSETS.get('PlayerCameraManager.CameraCache')
            + OFFSETS.get('CameraCacheEntry.MinimalViewInfo'),
            fov=True)

    def _coord_builder(self, actor_address: int, offset=0x78, camera=True,
                       fov=False) -> dict:

        if fov:
            actor_bytes = self.rm.read_bytes(actor_address + offset, 44)
            unpacked = struct.unpack("<ffffff16pf", actor_bytes)
        else:
            actor_bytes = self.rm.read_bytes(actor_address + offset, 24)
            unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0]/100, "y": unpacked[1]/100,
                           "z": unpacked[2]/100}
        if camera:
            coordinate_dict["cam_x"] = unpacked[3]
            coordinate_dict["cam_y"] = unpacked[4]
            coordinate_dict["cam_z"] = unpacked[5]
        if fov:
            coordinate_dict['fov'] = unpacked[7]

        return coordinate_dict
    
    def actor_info_generator(self, actor_data, level_actors_raw):
        for x in range(0, actor_data[1]):
            raw_name = ""
            actor_address = int.from_bytes(level_actors_raw[(x*8):(x*8+8)], byteorder='little', signed=False)
            actor_id = self.rm.read_int(
                actor_address + OFFSETS.get('Actor.actorId')
            )

            # We save a mapping of actor id to actor name for the sake of
            # saving memory calls
            if actor_id not in self.actor_name_map and actor_id != 0:
                try:
                    raw_name = self.rm.read_gname(actor_id)
                    self.actor_name_map[actor_id] = raw_name
                except Exception as e:
                    logger.error(f"Unable to find actor name: {e}")
            elif actor_id in self.actor_name_map:
                raw_name = self.actor_name_map.get(actor_id)

            # Ignore anything we cannot find a name for
            if not raw_name:
                continue

            yield raw_name, actor_address, actor_id



    def read_actors(self):
        """
        Represents a full scan of every actor within our render distance.
        Will create an object for each type of object we are interested in,
        and store it in a class variable (display_objects).
        Then our main game loop updates those objects
        """

        self.halls_data = []
        self.sink_data = []

        self.update_my_coords()

        actor_raw = self.rm.read_bytes(self.u_level + 0xa0, 0xC)
        actor_data = struct.unpack("<Qi", actor_raw)

        level_actors_raw = self.rm.read_bytes(actor_data[0], actor_data[1] * 8)

        # search all interesting actors
        for raw_name, actor_address, actor_id in self.actor_info_generator(actor_data, level_actors_raw):
            actor_class = ACTOR_CLASSES.get(raw_name, False)
            if actor_class and actor_address not in [act.address for act in self.display_objects]:
                actor = actor_class(self.rm, actor_id, actor_address, self.my_coords, raw_name)
                while actor.actor_id in [act.actor_id for act in self.display_objects]:
                    actor.actor_id += 1
                self.display_objects.append(actor)


        # put data into dataclass for easear access
        for actor in self.display_objects:
            if isinstance(actor, Ship) and actor.address not in [act.address for act in self.data.ships]:
                self.data.ships.append(actor)
            elif isinstance(actor, Sink) and actor.actor_id not in [act.actor_id for act in self.sink_data]:
                self.sink_data.append(actor)
            elif isinstance(actor, Holes) and actor.actor_id not in [act.actor_id for act in self.halls_data]:
                self.halls_data.append(actor)
            elif isinstance(actor, Player) and actor.actor_id not in [act.actor_id for act in self.data.players]:
                self.data.players.append(actor)
            elif isinstance(actor, Cannons) and actor.address not in [act.address for act in self.data.cannons]:
                self.data.cannons.append(actor)
            elif isinstance(actor, Seagull) and actor.address not in [act.address for act in self.data.seagulls]:
                self.data.seagulls.append(actor)


        # add sink manager and halls manager to its ship
        for ship in self.data.ships:
            for sink in self.sink_data:
                if calculate_distance(ship.coords, sink.coords) <= 10:
                    ship.add_sink_data(sink)
            for hall in self.halls_data:
                if calculate_distance(ship.coords, hall.coords) <= 10:
                    ship.add_halls_data(hall)



