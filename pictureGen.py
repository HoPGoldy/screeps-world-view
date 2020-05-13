import json
import os
from io import BytesIO
from pathlib import Path

from PIL import Image
import requests

dim = 20
dim_rooms = 200

world_dim = 14

background = Image.new('RGBA', (world_dim * dim_rooms,) * 2, (0xff,) * 4)

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
        background.paste(img, (x * dim_rooms, y * dim_rooms))


# get user data


def room_name_x():
    s = "W"
    n = 69
    while n < 70:
        yield "{}{}".format(s, n)
        if s == "W":
            if n == 0:
                s = "E"
            else:
                n -= 1
        else:
            n += 1


def room_name_y():
    s = "N"
    n = 69
    while n < 70:
        yield "{}{}".format(s, n)
        if s == "N":
            if n == 0:
                s = "S"
            else:
                n -= 1
        else:
            n += 1


# auth
with open("config.JSON") as auth:
    d = json.load(auth)
    username = d["username"]
    password = d["password"]
auth_path = 'https://screeps.com/api/auth/signin'
r = requests.post(auth_path, json={'email': username, 'password': password})
r.raise_for_status()
token = json.loads(r.text)["token"]
path = 'https://screeps.com/api/game/map-stats'

data = {}
users = []
for x in room_name_x():
    rooms = []
    for y in room_name_y():
        rooms.append(x + y)
    params = {'rooms': rooms, 'shard': 'shard3', 'statName': 'owner0'}
    r = requests.post(path, json=params, headers={'X-Token': token,
                                                  'X-Username': token})
    token = r.headers["X-Token"]
    ret = json.loads(r.text)
    for room_name in ret["stats"]:
        data[room_name] = {
            "status": ret["stats"][room_name]["status"]
        }
        if ("own" in ret["stats"][room_name]) and not ret["stats"][room_name]["own"]["user"] == "2":
            data[room_name]["owner"] = ret["stats"][room_name]["own"]["user"]
            data[room_name]["rcl"] = ret["stats"][room_name]["own"]["level"]

    for user in ret["users"]:
        if not user == "2" and user not in users:
            users.append(user)

# print(data)
# print(users)

# background.show()
