"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


ships = {
    # ------------ SHIPS / AI SHIPS ------------
    "BP_SmallShipTemplate_C": {
        "Name": "Sloop",
        "Icon": "icons/Sloop_icon.webp"
    },
    "BP_SmallShipNetProxy_C": {
        "Name": "Sloop",
        "Icon": "icons/Sloop_icon.webp"
    },

    "BP_MediumShipTemplate_C": {
        "Name": "Brig",
        "Icon": "icons/Brigantine_icon.webp"
    },
    "BP_MediumShipNetProxy_C": {
        "Name": "Brig",
        "Icon": "icons/Brigantine_icon.webp"
    },

    "BP_LargeShipTemplate_C": {
        "Name": "Galleon",
        "Icon": "icons/Galleon_icon.webp"
    },
    "BP_LargeShipNetProxy_C": {
        "Name": "Galleon",
        "Icon": "icons/Galleon_icon.webp"
    },

    "BP_AISmallShipTemplate_C": {
        "Name": "Skeleton Sloop",
        "Icon": "icons/Sloop_icon.webp"
    },
    "BP_AISmallShipNetProxy_C": {
        "Name": "Skeleton Sloop",
        "Icon": "icons/Sloop_icon.webp"
    },
    "BP_AILargeShipTemplate_C": {
        "Name": "Skeleton Galleon",
        "Icon": "icons/Galleon_icon.webp"
    },
    "BP_AILargeShipNetProxy_C": {
        "Name": "Skeleton Galleon",
        "Icon": "icons/Galleon_icon.webp"
    }
}

ship_keys = set(ships.keys())

sink = {
    "BP_SmallShip_StandardHull_InternalShipWater_C": {
        "name": "Small Ship Water",
    },
    "BP_MediumShip_StandardHull_InternalShipWater_C": {
        "name": "Medium Ship Water",
    },
    "BP_LargeShip_StandardHull_InternalShipWater_C": {
        "name": "Large Ship Water",
    },
}

sink_keys = set(sink.keys())


hulls = {
    # ------------ HULLS ------------
    "BP_SmallShip_StandardHull_Damage_C": {
        "Name": "Small Ship Hull",
    },
    "BP_MediumShip_StandardHull_Damage_C": {
        "Name": "Medium Ship Hull",
    },
    "BP_LargeShip_StandardHull_Damage_C": {
        "Name": "Large Ship Hull",
    }
}

hull_keys = set(hulls.keys())

cannons = {
    "BP_Cannon_ShipPartMMC_C": {
        "Name": "Onboard Cannon"
    }
}

cannons_keys = set(cannons.keys())

seagulls = {
    "BP_Seagull01_8POI_C": {
        "Name": "Regular seagulls"
    },
    "BP_Seagull01_32POI_Circling_Shipwreck_C": {
        "Name": "Shipwreck seagulls"
    },
    "BP_Seagull01_8POI_LostShipments_C": {
        "Name": "LostShipment seagulls"
    },
    "BP_Seagulls_Barrels_BarrelsOfPlenty_C": {
        "Name": "Regular seagulls"
    },
    "BP_BuoyantCannonballBarrel_LockedToWater_C": {
        "Name": "Cannon barrels"
    },
    "BP_Seagulls_Barrels_C": {
        "Name": "Regular seagulls"
    }
}

seagulls_keys = set(seagulls.keys())

players = {
    "BP_PlayerPirate_C": {
        "Name": "Player"
    }
}

players_keys = set(players.keys())