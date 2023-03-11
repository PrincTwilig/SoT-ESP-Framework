import math
import struct
import logging
from memory_helper import ReadMemory
from mapping import ship_keys, waters, hull_keys, cannons_keys
from helpers import OFFSETS, CONFIG, logger, calculate_distance
from Modules.ship import Ship
from Modules.crews import Crews
from Modules.sink import Sink
from Modules.holes import Holes
from Modules.players import Player
from Modules.cannons import Cannons
from Modules.seagull import Seagull


class SoTMemoryReader:
    """
    Wrapper class to handle reading data from the game, parsing what is
    important, and returning it to be shown by pyglet
    """

    def __init__(self):
        """
        Upon initialization of this object, we want to find the base address
        for the SoTGame.exe, then begin to load in the static addresses for the
        uWorld, gName, gObject, and uLevel objects.

        We also poll the local_player object to get a first round of coords.
        When running read_actors, we update the local players coordinates
        using the camera-manager object

        Also initialize a number of class variables which help us cache some
        basic information
        """
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
        self.ships = []
        self.cannons = []
        self.seagulls = []
        self.halls_data = []
        self.sink_data = []
        self.players = []
        self.display_objects = []
        self.crew_data = None
        self.local_ship = False

    def _load_local_player(self) -> int:
        """
        Returns the local player object out of uWorld.UGameInstance.
        Used to get the players coordinates before reading any actors
        :rtype: int
        :return: Memory address of the local player object
        """
        game_instance = self.rm.read_ptr(
            self.world_address + OFFSETS.get('World.OwningGameInstance')
        )
        local_player = self.rm.read_ptr(
            game_instance + OFFSETS.get('GameInstance.LocalPlayers')
        )
        return self.rm.read_ptr(local_player)

    def update_my_coords(self):
        """
        Function to update the players coordinates and camera information
        storing that new info back into the my_coords field. Necessary as
        we dont always run a full scan and we need a way to update ourselves
        """
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
        """
        Given a specific actor, loads the coordinates for that actor given
        a number of parameters to define the output
        :param int actor_address: Actors base memory address
        :param int offset: Offset from actor address to beginning of coords
        :param bool camera: If you want the camera info as well
        :param bool fov: If you want the FoV info as well
        :rtype: dict
        :return: A dictionary containing the coordinate information
        for a specific actor
        """
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

        self.update_my_coords()

        actor_raw = self.rm.read_bytes(self.u_level + 0xa0, 0xC)
        actor_data = struct.unpack("<Qi", actor_raw)

        level_actors_raw = self.rm.read_bytes(actor_data[0], actor_data[1] * 8)

        self.server_players = []
        self.local_ship = None
        self.display_objects = []

        for raw_name, actor_address, actor_id in self.actor_info_generator(actor_data, level_actors_raw):

            if raw_name == "BP_Cannon_ShipPartMMC_C":
                cannon = Cannons(self.rm, actor_id, actor_address, self.my_coords, raw_name, self.player_controller)
                if cannon.address not in [actor.address for actor in self.cannons]:
                    existing_actor_ids = [c.actor_id for c in self.cannons]
                    while cannon.actor_id in existing_actor_ids:
                        cannon.actor_id += 1
                    self.cannons.append(cannon)


            elif raw_name == "BP_Seagull01_8POI_C" or raw_name == "BP_Seagull01_32POI_Circling_Shipwreck_C" or raw_name == "BP_Seagull01_8POI_LostShipments_C" or raw_name == "BP_Seagulls_Barrels_BarrelsOfPlenty_C" or raw_name == "BP_BuoyantCannonballBarrel_LockedToWater_C" or raw_name == "BP_Seagulls_Barrels_C":
                seagull = Seagull(self.rm, actor_id, actor_address, self.my_coords, raw_name)
                if seagull.address not in[actor.address for actor in self.seagulls]:
                    existing_actor_ids = [c.actor_id for c in self.seagulls]
                    while seagull.actor_id in existing_actor_ids:
                        seagull.actor_id += 1
                    self.seagulls.append(seagull)

                    


            elif CONFIG.get('SHIPS_ENABLED') and raw_name in ship_keys:
                ship = Ship(self.rm, actor_id, actor_address, self.my_coords, raw_name)
                if ship.address not in [actor.address for actor in self.ships]:
                    existing_actor_ids = [s.actor_id for s in self.ships]
                    while ship.actor_id in existing_actor_ids:
                        ship.actor_id += 1
                    self.ships.append(ship)

            elif CONFIG.get('CREWS_ENABLED') and raw_name == "CrewService":
                self.crew_data = Crews(self.rm, actor_id, actor_address)

            elif CONFIG.get('WATER_PERCENTAGE') and raw_name in waters:
                sink = Sink(self.rm, actor_id, actor_address, self.my_coords)
                if sink.actor_id not in [actor.actor_id for actor in self.sink_data]:
                    self.sink_data.append(sink)

            elif CONFIG.get('HULLS_COUNT') and raw_name in hull_keys:
                holes = Holes(self.rm, actor_id, actor_address, self.my_coords)
                if holes.actor_id not in [actor.actor_id for actor in self.halls_data]:
                    self.halls_data.append(holes)

            elif CONFIG.get('PLAYER_CHARACTER') and raw_name == "BP_PlayerPirate_C":
                player = Player(self.rm, actor_id, actor_address, self.my_coords, raw_name)
                if player.actor_id not in [actor.actor_id for actor in self.players]:
                    self.players.append(player)

            else:
                continue

            for ship in self.ships:
                if ship.distance < 20:
                    self.local_ship = ship
                for sink in self.sink_data:
                    if calculate_distance(ship.coords, sink.coords) <= 10:
                        ship.add_sink_data(sink)
                for hall in self.halls_data:
                    if calculate_distance(ship.coords, hall.coords) <= 10:
                        ship.add_halls_data(hall)


            for actor in self.ships + self.sink_data + self.halls_data + self.players + self.cannons + self.seagulls:
                if actor.actor_id not in [actorr.actor_id for actorr in self.display_objects]:
                    self.display_objects.append(actor)
