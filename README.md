# screeps-world-view

> **本项目已经废弃并停止维护，替代项目见 [screeps-world-printer](https://github.com/HoPGoldy/screeps-world-printer)。**

生成如下 screeps 的世界总览图，已实现全 shard 绘制，包含新手区及重生区，支持单次绘制和定时绘制。

[![Y54FPA.th.gif](https://s1.ax1x.com/2020/05/19/Y54FPA.th.gif)](https://s1.ax1x.com/2020/05/19/Y54FPA.gif)

# 版本需要

- python `3.7+`
- cairo `latest`（如果你出现了 `OSError: no library called "cairo" was found` 的报错，请按照 [本文](https://cairosvg.org/documentation/) 描述安装本依赖）

# 安装依赖

```
pip3 install -r requirements.txt
```

# 填写配置项

根目录下新建`config.json`，填入如下内容：

```
{
    "username": "填写你的 Screeps 用户名",
    "password": "填写你的 Screeps 密码"
}
```

# 运行

## 1、直接绘制

在项目根目录下执行以下命令来绘制 s0 - s3 的地图总览，首次执行会下载地图瓦片和玩家头像，所以首次绘制会比较慢。而后续执行则会应用地图缓存和对头像进行增量更新，绘制速度会显著提高。

```
python src/main.py
```

```bash
--- 开始绘制 Screeps Shard3 2020-05-19 ---
使用缓存地图 ✔
正在加载世界信息 ✔                                                                                  
下载头像 ✔                                                                                          
正在绘制世界 ✔                                                                                      
已保存至 dist/3/2020-05-19.png
```

任务配置项请参阅本文件（`src/main.py`）头部常量。

## 2、启动定时任务

在项目根目录下执行以下命令来启动定时任务，执行后绘制任务会直接开始，并在次日零点再次绘制。请确保该任务在后台运行。

```
python src/timer.py
```

任务配置项请参阅本文件（`src/timer.py`）头部常量。

# 感谢

感谢 [cookiesjuice](https://github.com/cookiesjuice/) 的代码贡献。
