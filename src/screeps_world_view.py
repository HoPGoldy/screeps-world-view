import json
import os
from io import BytesIO
from pathlib import Path

from PIL import Image
import cairosvg
import requests

# 每个区块的边长像素值
ROOM_PIXEL = 200
# 整个世界的区块数量
WORLD_SIZE = 14

def draw_background():
    background = Image.new('RGBA', (WORLD_SIZE * ROOM_PIXEL,) * 2, (0xff,) * 4)

    xRoomName = ["W69", "W59", "W49", "W39", "W29", "W19", "W9",
                "E0", "E10", "E20", "E30", "E40", "E50", "E60"]

    yRoomName = ["N69", "N59", "N49", "N39", "N29", "N19", "N9",
                "S0", "S10", "S20", "S30", "S40", "S50", "S60"]

    Path("./.rooms").mkdir(parents=True, exist_ok=True)

    for x in range(len(xRoomName)):
        for y in range(len(yRoomName)):
            roomName = xRoomName[x] + yRoomName[y]
            if os.path.exists("./.rooms/{}.png".format(roomName)):
                img = Image.open("./.rooms/{}.png".format(roomName))
            else:
                print("getting {}".format(roomName))
                img = Image.open(BytesIO(
                    requests.get("https://d3os7yery2usni.cloudfront.net/map/shard3/zoom1/{}.png".
                                format(roomName)).content))
                img.save("./.rooms/{}.png".format(roomName))
            background.paste(img, (x * ROOM_PIXEL, y * ROOM_PIXEL))

    background.save('background.png')

def get_roomname(world_size=70):
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

    rooms = get_roomname()

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

        # print(rooms)
        # print(users)
        return rooms, users

def get_avatar(users):
    Path("../.avatar").mkdir(parents=True, exist_ok=True)

    for username in users:
        print(f'下载头像 - {username}')
        svg = requests.get(f'https://screeps.com/api/user/badge-svg?username={username}').content
        cairosvg.svg2png(bytestring=svg, write_to=f'../.avatar/{username}.png')
        # print()
        # img = Image.open(BytesIO(requests.get(f'https://screeps.com/api/user/badge-svg?username={username}').content))
        # img.save(f'../.avatar/{username}.png')