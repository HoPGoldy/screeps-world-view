import json
from os import path, makedirs
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
# 放大倍数，因为默认情况下一个房间只有 20 像素，会影响显示效果，但是该值太大会导致地图显示模糊
ZOOM = 2

class ScreepsWorldView:
    background = None
    cache_path = None

    def __init__(self, shard=3):
        if not path.exists('.screeps_cache'):
            self.init_cache_folder()

        self.cache_path = f'.screeps_cache/{shard}'
        if path.exists(f'{self.cache_path}/background.png'):
            self.background = Image.open(f'{self.cache_path}/background.png')
        else:
            self.background = self.draw_background()
        

    def init_cache_folder(self):
        for shard_name in [ '0', '1', '2', '3']:
            for type_name in [ 'room', 'avatar' ]:
                makedirs(f'.screeps_cache/{shard_name}/{type_name}')
        print('缓存目录创建成功')


    def draw_background(self):
        background = Image.new('RGBA', (WORLD_SIZE * ROOM_PIXEL,) * 2, (0xff,) * 4)

        xRoomName = ["W69", "W59", "W49", "W39", "W29", "W19", "W9", "E0", "E10", "E20", "E30", "E40", "E50", "E60"]
        yRoomName = ["N69", "N59", "N49", "N39", "N29", "N19", "N9", "S0", "S10", "S20", "S30", "S40", "S50", "S60"]

        for x in range(len(xRoomName)):
            for y in range(len(yRoomName)):
                roomName = xRoomName[x] + yRoomName[y]
                room_img_path = f'{self.cache_path}/room/{roomName}.png'
                if path.exists(room_img_path):
                    img = Image.open(room_img_path)
                else:
                    print(f'下载房间 - {roomName}')
                    img = Image.open(BytesIO(requests.get(f'https://d3os7yery2usni.cloudfront.net/map/shard3/zoom1/{roomName}.png').content))
                    img.save(room_img_path)
                background.paste(img, (x * ROOM_PIXEL, y * ROOM_PIXEL))

        background.save(f'{self.cache_path}/background.png')
        print('房间下载完成')

        return background


def get_room_name(world_size=70):
    name_x = [f'W{i}' for i in range(0, world_size)] + [f'E{i}' for i in range(0, world_size)]
    name_y = [f'S{i}' for i in range(0, world_size)] + [f'N{i}' for i in range(0, world_size)]
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
            
            # 尚不清楚新手区和重生区的渲染规则
            # if 'respawnArea' in ret["stats"][room_name] and 'novice' not in ret["stats"][room_name]:
            #     rooms[room_name]["status"] = 'respawn'
            # elif 'novice' in ret["stats"][room_name] and 'openTime' in ret["stats"][room_name]:
            #     rooms[room_name]["status"] = 'novice'

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
        code = quadrant_size - axis / 40
        # 根据 code 的正负判断其所在象限
        room += f'{pos_direction[i][0]}{math.floor(-code)}' if code <= 0 else f'{pos_direction[i][1]}{math.floor(code - 1)}'

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
    
    mask = Image.new('RGBA', (40, 40), colors[mask_type])
    # 取出指定位置的房间
    room = background.crop((x, y, x + 40, y + 40))
    # 将取出的位置和蒙版贴在一起然后粘回去
    background.paste(Image.blend(room, mask, 0.5), (x, y))

    return background