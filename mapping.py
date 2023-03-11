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

waters = {
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

water_keys = set(waters.keys())


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