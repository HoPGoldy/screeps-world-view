import time, sched, datetime
from screeps_world_view import ScreepsWorldView

# 要绘制的 shard
DRAW_SHARD = [ 3, 2, 1, 0 ]
# 重试间隔（秒）
RETRY_INTERVAL = 200

# 新建调度器
s = sched.scheduler(time.time, time.sleep)


def get_draw_interval():
    """获取现在到明天零点的秒间隔

    Return:
        number: 现在到明天零点的秒数
    """
    # 获取现在的秒时间戳
    now_time_stamp = int(time.time())
    # 获取明天的秒时间戳
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_time_stamp = int(time.mktime(tomorrow.timetuple()))
    # 获取明天零点多一点的秒时间戳
    tomorrow_time_stamp = int(tomorrow_time_stamp / 1000) * 1000 + 1

    return tomorrow_time_stamp - now_time_stamp


#被调度触发的函数
def draw():
    """执行绘制任务
    若成功执行完绘制任务则第二天零点再次绘制
    否则间隔 RETRY_INTERVAL 秒后重试
    """
    try:
        # 遍历所有 shard 进行绘制
        for i in DRAW_SHARD:
            view = ScreepsWorldView(i)
            view.draw()
        
        # 如果正常绘制完成则安排下一次绘制任务
        s.enter(get_draw_interval(), 0, draw)
        print('\n绘制完成，将在次日 0 点重新进行绘制，请确保本任务在后台运行。\n')
    
    # 绘制异常则尝试重试
    except Exception as err:
        print(f'绘制出现异常，将在 {RETRY_INTERVAL} 秒后重试:\n', err)
        s.enter(RETRY_INTERVAL, 0, draw)


if __name__ == "__main__":
    s.enter(0, 0, draw)
    s.run()