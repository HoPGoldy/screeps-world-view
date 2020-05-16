import json
from os import path, makedirs
import time
import math
from io import BytesIO
from pathlib import Path

from PIL import Image
import cairosvg
import requests

# 每个房间的边长像素值
ROOM_PIXEL = 20
# 区块由几乘几的房间组成
ROOM_PRE_SECTOR = 10
# 整个世界的区块数量
WORLD_SIZE = 14
# 放大倍数，因为默认情况下一个房间只有 20 像素，会影响显示效果，但是该值太大会导致地图显示模糊
ZOOM = 2
# 地图指定区域的颜色
COLORS = {
    # 未激活区域
    "inactivated": '#000000',
    # 重生区
    "respawn": '#006bff',
    # 新手保护区
    "novice": '#7cff7c'
}

class ScreepsWorldView:
    background = None
    cache_path = None
    dist_path = None

    rooms = {}
    users = {}

    def __init__(self, shard=3):
        if not path.exists('.screeps_cache'):
            self.init_cache_folder()

        self.cache_path = f'.screeps_cache/{shard}'
        self.dist_path = f'dist/{shard}'
        if path.exists(f'{self.cache_path}/background.png'):
            self.background = Image.open(f'{self.cache_path}/background.png')
        else:
            self.background = self.draw_background()


    def draw(self):
        self.draw_background()
        self.get_world_stats()
        self.get_avatar()
        self.draw_world()


    def init_cache_folder(self):
        for shard_name in [ '0', '1', '2', '3']:
            for type_name in [ 'room', 'avatar' ]:
                makedirs(f'.screeps_cache/{shard_name}/{type_name}')
            makedirs(f'dist/{shard_name}')
        print('缓存目录创建成功')


    def draw_background(self):
        background = Image.new('RGBA', (WORLD_SIZE * ROOM_PIXEL * ROOM_PRE_SECTOR,) * 2, (0xff,) * 4)

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
                background.paste(img, (x * ROOM_PIXEL * ROOM_PRE_SECTOR, y * ROOM_PIXEL * ROOM_PRE_SECTOR))

        background.save(f'{self.cache_path}/background.png')
        print('房间下载完成')

        return background


    def draw_world(self):
        for x in range(0, WORLD_SIZE * ROOM_PRE_SECTOR * ROOM_PIXEL * ZOOM * 2, ROOM_PIXEL * ZOOM):
            for y in range(0, WORLD_SIZE * ROOM_PRE_SECTOR * ROOM_PIXEL * ZOOM * 2, ROOM_PIXEL * ZOOM):
                room_name = self._pixel2room((x, y))
                if room_name not in self.rooms:
                    continue
                
                room = self.rooms[room_name]
                if room['status'] == 'out of borders':
                    add_inactivated_mask(x, y, 'inactivated')
                elif room['status'] == 'respawn':
                    add_inactivated_mask(x, y, 'respawn')
                elif room['status'] == 'novice':
                    add_inactivated_mask(x, y, 'novice')
                
                if 'owner' in room:
                    avatar_path = f'{self.cache_path}/avatar/{room["owner"]}.png'
                    if os.path.exists(avatar_path):
                        correct_size = (6 * ZOOM, 6 * ZOOM) if room['rcl'] == 0 else (10 * ZOOM, 10 * ZOOM)
                        try:
                            avatar = Image.open(avatar_path).resize(correct_size)

                            if room['rcl'] == 0:
                                mask = Image.new('RGBA', correct_size)
                                avatar = Image.blend(avatar, mask, 0.3)

                            bg.paste(avatar, (x + int((ROOM_PIXEL * ZOOM - correct_size[0]) / 2), y + int((ROOM_PIXEL * ZOOM - correct_size[1]) / 2)), mask=avatar)
                        except UnidentifiedImageError:
                            print(f'头像失效 - {avatar_path}')                        
                    else:
                        print(f'未找到头像 - {avatar_path}')

        print('绘制完成')
        result_name = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.background.save(f'{self.dist_path}/{result_name}.png')


    def get_room_name(self, world_size=70):
        name_x = [f'W{i}' for i in range(0, world_size)] + [f'E{i}' for i in range(0, world_size)]
        name_y = [f'S{i}' for i in range(0, world_size)] + [f'N{i}' for i in range(0, world_size)]
        return [x + y for x in name_x for y in name_y]


    def get_world_stats(self):
        with open("config.json") as auth:
            d = json.load(auth)
            username = d["username"]
            password = d["password"]
        
        r = requests.post('https://screeps.com/api/auth/signin', json={'email': username, 'password': password})
        r.raise_for_status()
        # token = json.loads(r.text)["token"]

        params = {'rooms': get_room_name(), 'shard': 'shard3', 'statName': 'owner0'}
        r = requests.post('https://screeps.com/api/game/map-stats', json=params, headers={ 'X-Token': token, 'X-Username': token }, timeout=120)
        # token = r.headers["X-Token"]
        
        self._format_room(json.loads(r.text))
        return self


    def _format_room(self, world_stats):
        for room_name in world_stats["stats"]:
            self.rooms[room_name] = {
                "status": world_stats["stats"][room_name]["status"]
            }
            if ("own" in world_stats["stats"][room_name]):
                self.rooms[room_name]["owner"] = world_stats["users"][world_stats["stats"][room_name]["own"]["user"]]["username"]
                self.rooms[room_name]["rcl"] = world_stats["stats"][room_name]["own"]["level"]

                if (self.rooms[room_name]["owner"] not in self.users):
                    self.users.append(self.rooms[room_name]["owner"])
            
            # 尚不清楚新手区和重生区的渲染规则
            # if 'respawnArea' in world_stats["stats"][room_name] and 'novice' not in world_stats["stats"][room_name]:
            #     self.rooms[room_name]["status"] = 'respawn'
            # elif 'novice' in world_stats["stats"][room_name] and 'openTime' in world_stats["stats"][room_name]:
            #     self.rooms[room_name]["status"] = 'novice'

        return self


    def get_avatar(self, users):
        for username in users:
            print(f'下载头像 - {username}')
            svg = requests.get(f'https://screeps.com/api/user/badge-svg?username={username}').content
            cairosvg.svg2png(bytestring=svg, write_to=f'{self.cache_path}/avatar/{username}.png')

        print('头像下载完成')
        return self


    def _pixel2room(self, pos):
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
            code = quadrant_size - axis / ROOM_PIXEL * ZOOM
            # 根据 code 的正负判断其所在象限
            room += f'{pos_direction[i][0]}{math.floor(-code)}' if code <= 0 else f'{pos_direction[i][1]}{math.floor(code - 1)}'

        return room


    def add_inactivated_mask(self, x, y, mask_type='inactivated'):
        """在指定位置添加未开放房间蒙版
        
        Args:
            x: 要添加到的房间左上角的 x 轴像素位置
            y: 要添加到的房间左上角的 y 轴像素位置
            mask_type: 蒙版类型, inactivated respawn novice 三者之一

        Returns:
            self 自身
        """
        size = ROOM_PIXEL * ZOOM
        mask = Image.new('RGBA', (size, size), COLORS[mask_type])
        # 取出指定位置的房间
        room = self.background.crop((x, y, x + size, y + size))
        # 将取出的位置和蒙版贴在一起然后粘回去
        self.background.paste(Image.blend(room, mask, 0.5), (x, y))

        return self