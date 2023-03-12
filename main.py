import pyglet, subprocess, time
from threading import Thread
from pyglet.text import Label
from pyglet.sprite import Sprite
from pyglet.image import SolidColorImagePattern
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, main_batch, \
    version, logger, object_to_screen, is_game_focused, calculate_distance
from visual_helper import get_ship_list_string
from sot_hack import SoTMemoryReader


# The FPS __Target__ for the program.
FPS_TARGET = 60

# See explanation in Main, toggle for a non-graphical debug
DEBUG = False
SEAGULLS = True

# Pyglet clock used to track time via FPS
clock = pyglet.clock.Clock()


def generate_all(_):
    thread = Thread(target=smr.read_actors)
    thread.start()

def run_subprocess():
    subprocess.run('SotExternalESPv3.5.2.exe')


def update_graphics(_):

    smr.update_my_coords()

    to_remove = []

    for actor in smr.display_objects:
        actor.update(smr.my_coords)

        if actor.to_delete:
            to_remove.append(actor)

    for removable in to_remove:
        if removable in smr.data.ships:
            smr.data.ships.remove(removable)
        elif removable in smr.sink_data:
            smr.sink_data.remove(removable)
        elif removable in smr.halls_data:
            smr.halls_data.remove(removable)
        elif removable in smr.data.players:
            smr.data.players.remove(removable)
        elif removable in smr.data.cannons:
            smr.data.cannons.remove(removable)
        elif removable in smr.data.seagulls:
            smr.data.seagulls.remove(removable)



if __name__ == '__main__':
    logger.info(
        "SOTESP Started"
    )
    logger.info(f"Hack Version: {version}")

    smr = SoTMemoryReader()

    config = Config(double_buffer=True, depth_size=24, alpha_size=8)


    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                  vsync=False, style='overlay', config=config,
                                  caption="Vlads hack")

    sunken_ships = {}
    seagull_sprites = {}


    window.set_location(SOT_WINDOW[0], SOT_WINDOW[1])

    @window.event
    def on_draw():
        window.clear()


        smr.local_ship = False
        for ship in smr.data.ships:
            if ship.distance < 20:
                smr.local_ship = ship
                break

        # ships around data
        if smr.data.ships:
            ships_list.text = get_ship_list_string(smr.data.ships)
        
        # local ship health
        if smr.local_ship:
            # health bar
            if smr.local_ship.sink_data:
                health_bar.scale_x = smr.local_ship.sink_data.water_info

                health_bar_frame.visible = True
                health_bar.visible = True

                if smr.local_ship.sink_data.water_info > 0.85:
                    health_bar_frame.visible = False
                    health_bar.visible = False
                elif smr.local_ship.sink_data.water_info > 0.6:
                    health_bar.color = (0, 255, 0)
                elif smr.local_ship.sink_data.water_info > 0.3:
                    health_bar.color = (255, 255, 0)
                else:
                    health_bar.color = (255, 0, 0)

            else:
                health_bar_frame.visible = False
                health_bar.visible = False
            
            # halls count
            if smr.local_ship.halls:
                current_ship_halls.text = str(smr.local_ship.halls.hulls_count if smr.local_ship.halls.hulls_count else "")
            else:
                current_ship_halls.text = ''
        else:
            health_bar_frame.visible = False
            health_bar.visible = False
            current_ship_halls.text = ''


        # cannon prediction system
        for cannon in smr.data.cannons:
            if cannon.is_on_cannon and smr.local_ship and len(smr.data.ships) > 1:
                
                ships = [ship for ship in smr.data.ships if ship != smr.local_ship]
                closest_ship = min(ships, key=lambda obj: obj.distance)


                if closest_ship.distance < 450:
                    try:
                        time_to_hit = cannon.get_time_to_hit(calculate_distance(smr.my_coords, closest_ship.coords))
                        predicted_coords = closest_ship.predict_coords(time_to_hit)
                    except:
                        continue

                    # try find predict coords position as close as possible by calculating distance
                    for _ in range(5):
                        try:
                            time_to_hit = cannon.get_time_to_hit(calculate_distance(smr.my_coords, predicted_coords))
                            predicted_coords = closest_ship.predict_coords(time_to_hit)
                        except:
                            continue

                    cannon_ball_travel_x = smr.local_ship.speed_x * time_to_hit
                    cannon_ball_travel_y = smr.local_ship.speed_y * time_to_hit

                    shoot_coords = {'x': predicted_coords['x'] - cannon_ball_travel_x, 'y': predicted_coords['y'] - cannon_ball_travel_y, 'z': predicted_coords['z']}
                    screen_coords = object_to_screen(smr.my_coords, shoot_coords)
                    
                    if screen_coords:
                        shot_line.visible = True
                        shot_line.y = ((SOT_WINDOW_H / 2) - (shot_line.height / 2)) + (calculate_distance(smr.my_coords, shoot_coords) - cannon.shot_distance) - 20
                        shot_line.x = screen_coords[0] - (shot_line.width / 2)

                else:
                    shot_line.visible = False

                break
            else:
                shot_line.visible = False


        # seagulls manager
        for seagull in smr.data.seagulls:
            # Check if seagull already has a sprite
            if seagull.address in seagull_sprites and SEAGULLS:
                # Update the sprite's coordinates
                if seagull.screen_coords:
                    seagull_sprites[seagull.address].x = seagull.screen_coords[0]
                    seagull_sprites[seagull.address].y = seagull.screen_coords[1]
                    seagull_sprites[seagull.address].text = f"[{seagull.distance}]"
                    seagull_sprites[seagull.address].visible = True
                    if seagull.raw_name == "BP_Seagull01_32POI_Circling_Shipwreck_C":
                        seagull_sprites[seagull.address].color = (0,0,255,255)
                    elif seagull.raw_name == "BP_Seagulls_Barrels_BarrelsOfPlenty_C":
                        seagull_sprites[seagull.address].color = (255,255,0,255)
                    else:
                        seagull_sprites[seagull.address].color = (255,255,255,255)
                else:
                    seagull_sprites[seagull.address].visible = False
            else:
                seagull_sprite = Label(f"[{seagull.distance}]", x=-200, y=-200,
                    batch=main_batch, font_size=10, color=(255,255,255,255))
                seagull_sprite.visible = False
                seagull_sprites[seagull.address] = seagull_sprite

        for address in list(seagull_sprites.keys()):
            if address not in [actor.address for actor in smr.data.seagulls]:
                seagull_sprites.pop(address)



        # check for sunken ships and add them to list
        for ship in smr.data.ships:

            if ship.sink_data and ship.sink_data.water_info == 0 and ship.address not in [act for act in sunken_ships.keys()]:
                ship_sprite = Label(f"[{ship.distance}]", x=0, y=0,
                        batch=main_batch, font_size=10, color=(255,0,0,255))
                ship_sprite.visible = False
                sunken_ships[ship.address] = {'coords': ship.coords, 'sprite': ship_sprite, 'Dtime': time.monotonic()}

        # update sunken ships position or delete
        for address, ship in list(sunken_ships.items()):
            distance = calculate_distance(smr.my_coords, ship['coords'])

            if (time.monotonic() - ship['Dtime'] >= 60 and distance < 90) or time.monotonic() - ship['Dtime'] >= 360:
                sunken_ships.pop(address)
                continue

            screen_coords = object_to_screen(smr.my_coords, ship['coords'])

            if screen_coords:
                ship['sprite'].x = screen_coords[0]
                ship['sprite'].y = screen_coords[1]
                ship['sprite'].text = f"[{distance}]"
                ship['sprite'].visible = True
            else:
                ship['sprite'].visible = False



        if DEBUG:
            debug_list.text = ""
            for actor in smr.display_objects:
                if actor.debug_data:
                    debug_list.text += f"{actor.__class__.__name__}:\n"
                    for data in actor.debug_data:
                        debug_list.text += f"{data}\n"
                


        if is_game_focused():
            main_batch.draw()



    pyglet.clock.schedule_interval(generate_all, 5)
    pyglet.clock.schedule_interval(smr.rm.check_process_is_active, 3)
    pyglet.clock.schedule(update_graphics)

    debug_list = Label("", x=SOT_WINDOW_W * 0.85, y=SOT_WINDOW_H * 0.7,
                       batch=main_batch, width=300,
                       multiline=True, font_name='Times New Roman')

    ships_list = Label("", x=SOT_WINDOW_W * 0.91, y=SOT_WINDOW_H * 0.97,
                       batch=main_batch, width=150,
                       multiline=True, font_name='Times New Roman')



    current_ship_halls = Label("", x=SOT_WINDOW_W * 0.492, y=SOT_WINDOW_H * 0.008,
                    batch=main_batch, font_size=40, color=(255,0,0,255))

    health_bar_frame = Sprite(SolidColorImagePattern((0, 0, 0, 255)).create_image(500, 30), batch=main_batch,
                              x=SOT_WINDOW_W / 3,
                              y=SOT_WINDOW_H / 22)
    health_bar_frame.visible = False

    health_bar = Sprite(SolidColorImagePattern((255, 255, 255, 255)).create_image(500, 30), batch=main_batch,
                        x=SOT_WINDOW_W / 3, y=SOT_WINDOW_H / 22, z=1)
    health_bar.visible = False

    
    image = pyglet.image.load('./icons/scope.png')
    shot_line = Sprite(image, batch=main_batch,
                        x=SOT_WINDOW_W / 2, y=SOT_WINDOW_H / 2)
    shot_line.scale = 0.17
    shot_line.visible = False



    Thread(target=run_subprocess).start()
    pyglet.app.run(interval=1/FPS_TARGET)



