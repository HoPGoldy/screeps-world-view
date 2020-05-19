from screeps_world_view import ScreepsWorldView

# 要绘制的 shard
DRAW_SHARD = [ 3, 2, 1, 0 ]

if __name__ == "__main__":
    # 遍历所有 shard 进行下载
    for i in DRAW_SHARD:
        view = ScreepsWorldView(i)
        view.draw()