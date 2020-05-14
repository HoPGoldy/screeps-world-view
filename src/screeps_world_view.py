import json
import os
import math
from io import BytesIO
from pathlib import Path

from PIL import Image
# import cairosvg
import requests

# 每个区块的边长像素值
ROOM_PIXEL = 200
# 整个世界的区块数量
WORLD_SIZE = 14


def draw_background():
    background = Image.new('RGBA', (WORLD_SIZE * ROOM_PIXEL,) * 2, (0xff,) * 4)

    xRoomName = ["W69", "W59", "W49", "W39", "W29", "W19", "W9", "E0", "E10", "E20", "E30", "E40", "E50", "E60"]
    yRoomName = ["N69", "N59", "N49", "N39", "N29", "N19", "N9", "S0", "S10", "S20", "S30", "S40", "S50", "S60"]

    Path("./.rooms").mkdir(parents=True, exist_ok=True)

    for x in range(len(xRoomName)):
        for y in range(len(yRoomName)):
            roomName = xRoomName[x] + yRoomName[y]
            if os.path.exists(f'./.rooms/{roomName}.png'):
                img = Image.open(f'./.rooms/{roomName}.png')
            else:
                print(f'getting {roomName}')
                img = Image.open(BytesIO(requests.get(f'https://d3os7yery2usni.cloudfront.net/map/shard3/zoom1/{roomName}.png'.content)))
                img.save(f'./.rooms/{roomName}.png')
            background.paste(img, (x * ROOM_PIXEL, y * ROOM_PIXEL))

    background.save('background.png')


def get_room_name(world_size=70, step=1):
    name_x = [f'W{i}' for i in range(0, world_size, step)] + [f'E{i}' for i in range(0, world_size, step)]
    name_y = [f'S{i}' for i in range(0, world_size, step)] + [f'N{i}' for i in range(0, world_size, step)]
    return [x + y for x in name_x for y in name_y]


def get_world_stats():
    with open("config.JSON") as auth:
        d = json.load(auth)
        username = d["username"]
        password = d["password"]
    auth_path = 'https://screeps.com/api/auth/signin'
    r = requests.post(auth_path, json={'email': username, 'password': password})
    r.raise_for_status()
    token = json.loads(r.text)["token"]
    path = 'https://screeps.com/api/game/map-stats'

    rooms = get_room_name()

    params = {'rooms': rooms, 'shard': 'shard3', 'statName': 'owner0'}
    r = requests.post(path, json=params, headers={ 'X-Token': token, 'X-Username': token }, timeout=120)
    token = r.headers["X-Token"]
    
    with open("world_stats.json", mode='a', encoding='utf-8') as stats_file:
        stats_file.write(r.text)


def format_room():
    rooms = {}
    users = []

    with open("world_stats.json", mode='r', encoding='utf-8') as stats_file:
        ret = json.loads(stats_file.read())

        for room_name in ret["stats"]:
            # print(ret["stats"][room_name])
            rooms[room_name] = {
                "status": ret["stats"][room_name]["status"]
            }
            if ("own" in ret["stats"][room_name]):
                rooms[room_name]["owner"] = ret["users"][ret["stats"][room_name]["own"]["user"]]["username"]
                rooms[room_name]["rcl"] = ret["stats"][room_name]["own"]["level"]

                if (rooms[room_name]["owner"] not in users):
                    users.append(rooms[room_name]["owner"])
            
            if 'respawnArea' in ret["stats"][room_name]:
                rooms[room_name]["status"] = 'respawn'
            elif 'novice' in ret["stats"][room_name]:
                rooms[room_name]["status"] = 'novice'

        # print(rooms)
        # print(users)
        return rooms, users


def get_avatar(users):
    Path(".avatar").mkdir(parents=True, exist_ok=True)

    for username in users:
        print(f'下载头像 - {username}')
        svg = requests.get(f'https://screeps.com/api/user/badge-svg?username={username}').content
        cairosvg.svg2png(bytestring=svg, write_to=f'.avatar/{username}.png')


def pixel2room(pos):
    """将像素位置转换为房间名

    Args:
        pos: tuple, 包含位置的 x y 值，如 (1400, 1400)
    
    Returns:
        string, 该位置所在的房间名称
    """
    room = ''
    quadrant_size = 70
    pos_direction = ( ('E', 'W'), ('S', 'N'))
    
    for i, axis in enumerate(pos):
        code = quadrant_size - axis / 20
        # 根据 code 的正负判断其所在象限
        room += f'{pos_direction[i][0]}{math.floor(-code)}' if code <= 0 else f'{pos_direction[i][1]}{math.floor(code)}'

    return room


def add_inactivated_mask(background, x, y, mask_type='inactivated'):
    """在指定位置添加未开放房间蒙版
    
    Args:
        background: Image Object，要添加未开放房间的底图
        x: 要添加到的房间左上角的 x 轴像素位置
        y: 要添加到的房间左上角的 y 轴像素位置
        mask_type: 蒙版类型, inactivated respawn novice 三者之一

    Returns:
        Image Object，添加好蒙版的地图
    """

    colors = {
        "inactivated": '#000000',
        "respawn": '#006bff',
        "novice": '#7cff7c'
    }
    
    mask = Image.new('RGBA', (20, 20), colors[mask_type])
    # 取出指定位置的房间
    room = background.crop((x, y, x + 20, y + 20))
    # 将取出的位置和蒙版贴在一起然后粘回去
    background.paste(Image.blend(room, mask, 0.5), (x, y))

    return background