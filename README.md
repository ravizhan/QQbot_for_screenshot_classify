# QQbot_for_screenshot_classify

> SakuraFrp 水群同款机器人)

## 功能

- 自动识别图片并回复识别结果
- 静默模式，机器人不会回复任何消息
- 管理员可自定义静音时间，以秒为单位，默认600s。
- 随机回复延迟

## 行为
- 群成员发送图片时，机器人自动识别图片。
- 随机延迟回复，并获取随机一言。
- 若识别结果为拍屏，则机器人回复识别结果。
- 若识别结果为非拍屏，则机器人不会回复任何消息。

## 配置
编辑 `__init__.py` 文件第18行，填入允许使用机器人的群号

## 连接
使用反向websocket连接到本机器人

支持onebot v11协议

测试支持的框架：
- [LLOneBot](https://github.com/LLOneBot/LLOneBot)
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ)

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 命令

- `/安静`

开启机器人静默模式，机器人不会回复任何消息。 

管理员可自定义静音时间，以秒为单位，默认600s。

格式：`/安静 600`
- `/解除安静`

关闭机器人静默模式，仅能由管理员使用。

## 协议
因本项目使用了AGPLv3协议授权的 [screenshot_classify](https://github.com/ravizhan/screenshot_classify)，依据该协议相关规定，现以相同协议开源本项目，请自觉遵守。
