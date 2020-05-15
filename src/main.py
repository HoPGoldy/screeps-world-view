from screeps_world_view import ScreepsWorldView

if __name__ == "__main__":
    view = ScreepsWorldView()
    # # draw_background()
    # # get_world_stats()
    # rooms, users = format_room()
    # bg = Image.open('background.png').resize((200 * 14 * 2,) * 2)
    # # get_avatar(users)

    # for x in range(0, 140 * 20 * 4, 40):
    #     for y in range(0, 140 * 20 * 4, 40):
    #         room_name = pixel2room((x, y))
    #         if room_name not in rooms:
    #             continue
            
    #         room = rooms[room_name]
    #         if room['status'] == 'out of borders':
    #             add_inactivated_mask(bg, x, y, 'inactivated')
    #         elif room['status'] == 'respawn':
    #             add_inactivated_mask(bg, x, y, 'respawn')
    #         elif room['status'] == 'novice':
    #             add_inactivated_mask(bg, x, y, 'novice')
            
    #         if 'owner' in room:
    #             avatar_path = f'./.avatar/{room["owner"]}.png'
    #             if os.path.exists(avatar_path):
    #                 correct_size = (12, 12) if room['rcl'] == 0 else (20, 20)
    #                 try:
    #                     avatar = Image.open(f'./.avatar/{room["owner"]}.png').resize(correct_size)
    #                 except UnidentifiedImageError:
    #                     # print(f'头像失效 - {avatar_path}')
    #                     pass
                    
    #                 if room['rcl'] == 0:
    #                     mask = Image.new('RGBA', correct_size)
    #                     avatar = Image.blend(avatar, mask, 0.3)
    #                 # print((x + (20 - correct_size[0]) / 2, y + (20 - correct_size[1]) / 2))
    #                 bg.paste(avatar, (x + int((40 - correct_size[0]) / 2), y + int((40 - correct_size[1]) / 2)), mask=avatar)
    #             else:
    #                 # print(f'未找到头像 - {avatar_path}')
    #                 pass
    # bg.show()
    # bg.save('result.png')

    # # x = 1380
    # # y = 1380

    # # print(pixel2room((x, y)))
    # # add_inactivated_mask(Image.open('background.png'), x, y, 'respawn').show()