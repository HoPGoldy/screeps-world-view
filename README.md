# screeps-world-view

生成如下 screeps 的世界总览图（目前仅支持 shard3）

[![](https://s1.ax1x.com/2020/05/18/YfqmZT.th.png)](https://s1.ax1x.com/2020/05/18/YfqmZT.png)

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

```
python src/main.py
```