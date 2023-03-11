def get_ship_list_string(ships):
    ships_string = ''
    for ship in ships:
        if ship.distance > 100 and not ship.is_bot:
            ships_string += f"{'S ' if 'Sloop' in ship.img_path else 'B ' if 'Brigantine' in ship.img_path else 'G '}Ship - {ship.distance}m \n"

    return ships_string

