from screeps_world_view import draw_background, get_world_stats, format_room, get_avatar, add_inactivated_mask, pixel2room, get_room_name

from PIL import Image

if __name__ == "__main__":
    draw_background()
    # get_world_stats()
    rooms, users = format_room()
    bg = Image.open('background.png')
    # get_avatar(users)

    for x in range(0, 140 * 20, 20):
        for y in range(0, 140 * 20, 20):
            room_name = pixel2room((x, y))
            if room_name not in rooms:
                continue
            
            room = rooms[room_name]
            if room['status'] == 'out of borders':
                print('未激活')
                add_inactivated_mask(bg, x, y, 'inactivated')
            elif room['status'] == 'respawn':
                print('重生区')
                add_inactivated_mask(bg, x, y, 'respawn')
            elif room['status'] == 'novice':
                print('新手区')
                add_inactivated_mask(bg, x, y, 'novice')
            else:
                print('正常')
    bg.show()


    # x = 0
    # y = 0

    # print(pixel2room((x, y)))
    # add_inactivated_mask(Image.open('background.png'), x, y, 'respawn').show()