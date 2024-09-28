import asyncio
import json
import time
import httpx
from nonebot import on_message, on_command
from nonebot.rule import is_type, Rule, to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment, PrivateMessageEvent
from nonebot.params import EventMessage, CommandArg
from .utils import ImageClassifier
import ssl
import random

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT')


async def is_auth_group(event: GroupMessageEvent) -> bool:
    # 这里填写允许使用机器人的群号
    if event.group_id in []:
        return True


async def is_image_msg(event: GroupMessageEvent) -> bool:
    msg = event.get_message()
    for segment in msg:
        if segment.type == "image" and segment.data["subType"] == 0:
            return True
    return False


async def is_quiet(event: GroupMessageEvent) -> bool:
    with open("data.json", "r") as f:
        data = json.load(f)
    if data["quiet"][str(event.group_id)] == 0:
        return True
    return data["quiet"][str(event.group_id)] < round(time.time())


async def is_admin(event: GroupMessageEvent) -> bool:
    role = event.sender.role
    return role in ["admin", "owner"]


rules = Rule(is_auth_group, is_image_msg, is_quiet)

pic_message = on_message(rule=is_type(GroupMessageEvent) & rules, priority=3)
no_quiet = on_command("解除安静", rule=is_type(GroupMessageEvent) & to_me() & Rule(is_admin), priority=2, block=True)
quiet = on_command("安静", rule=is_type(GroupMessageEvent) & to_me(), priority=1, block=True)
private_pic_message = on_message(rule=is_type(PrivateMessageEvent), priority=5)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}
classifier = ImageClassifier()
httpx_session = httpx.Client(http2=True, verify=ctx, headers=headers)


@pic_message.handle()
async def _(event: GroupMessageEvent, message: Message = EventMessage()):
    for segment in message:
        url = segment.data["url"]
        await asyncio.sleep(random.randint(0, 5))
        await asyncio.sleep(random.randint(0, 5))
        img = httpx_session.get(url).content
        result = classifier.classify(img)
        await asyncio.sleep(random.randint(5, 10))
        try:
            data = httpx_session.get("https://v1.hitokoto.cn/").json()
            text = data["hitokoto"]
        except:
            text = "没有每日一言"
        send_msg1 = MessageSegment.reply(event.message_id)
        send_msg2 = MessageSegment.at(event.user_id)
        send_msg3 = MessageSegment.text(" 请勿拍屏，请使用截图功能以获得更好的帮助。\n")
        send_msg4 = MessageSegment.text(f"图片识别结果为：{result[0]}, 置信度：{result[1]}%，用时：{result[2]:.3f}ms")
        send_msg5 = MessageSegment.text(f"\n每日一言：{text}\n如需暂停识别，请@我并发送 /安静")
        print(send_msg4)
        if result[0] == "拍屏":
            with open("data.json", "r") as f:
                data = json.load(f)
                data["cameracap_sender"][str(event.user_id)] = event.time
            with open("data.json", "w") as f:
                f.write(json.dumps(data))
            await pic_message.finish(Message([send_msg1, send_msg2, send_msg3, send_msg4, send_msg5]))
        else:
            return
            # await pic_message.finish(Message([send_msg1, send_msg4, send_msg5]))


@quiet.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    role = event.sender.role
    group_id = str(event.group_id)
    with open("data.json", "r") as f:
        data = json.load(f)
    if data["cameracap_sender"].get(str(event.user_id)) is not None and role == "member":
        if round(time.time()) - data["last_cameracap_sender"][str(event.user_id)] < 60 * 10:
            await quiet.finish(MessageSegment.text("您在十分钟内有拍屏记录，命令无效"))
            return
    if role in ["admin", "owener"] and args.extract_plain_text():
        try:
            t = args.extract_plain_text()
            if int(t) > 24 * 60 * 60 or int(t) < 0:
                await quiet.finish(MessageSegment.text("输入时间无效，已自动设置为10分钟"))
                data["quiet"][group_id] = round(time.time()) + 60 * 10
                sleep_time = time.strftime("%H:%M:%S", time.gmtime(60 * 10))
            else:
                data["quiet"][group_id] = round(time.time()) + int(t)
                sleep_time = time.strftime("%H:%M:%S", time.gmtime(int(t)))
        except:
            await quiet.finish(MessageSegment.text("输入时间无效，已自动设置为10分钟"))
            data["quiet"][group_id] = round(time.time()) + 60 * 10
            sleep_time = time.strftime("%H:%M:%S", time.gmtime(60 * 10))
    else:
        data["quiet"][group_id] = round(time.time()) + 60 * 10
        sleep_time = time.strftime("%H:%M:%S", time.gmtime(60 * 10))
    with open("data.json", "w") as f:
        f.write(json.dumps(data))
    time.sleep(random.randint(10, 15))
    try:
        data = httpx_session.get("https://v1.hitokoto.cn/").json()
        text = data["hitokoto"]
    except:
        text = "没有每日一言"
    await quiet.finish(MessageSegment.text(f"每日一言：{text}\n已进入安静模式，请勿拍屏。\n{sleep_time}后解除"))


@no_quiet.handle()
async def _(event: GroupMessageEvent):
    with open("data.json", "r") as f:
        data = json.load(f)
    with open("data.json", "w") as f:
        data["quiet"][str(event.group_id)] = 0
        f.write(json.dumps(data))
    time.sleep(random.randint(10, 15))
    try:
        data = httpx_session.get("https://v1.hitokoto.cn/").json()
        text = data["hitokoto"]
    except:
        text = "没有每日一言"
    await no_quiet.finish(MessageSegment.text(f"每日一言：{text}\n已解除安静模式"))


@private_pic_message.handle()
async def _(event: PrivateMessageEvent, message: Message = EventMessage()):
    for segment in message:
        url = segment.data["url"]
        await asyncio.sleep(random.randint(0, 5))
        await asyncio.sleep(random.randint(0, 5))
        img = httpx_session.get(url).content
        result = classifier.classify(img)
        await asyncio.sleep(random.randint(5, 10))
        try:
            data = httpx_session.get("https://v1.hitokoto.cn/").json()
            text = data["hitokoto"]
        except:
            text = "没有每日一言"
        send_msg1 = MessageSegment.text(f"图片识别结果为：{result[0]}, 置信度：{result[1]}%，用时：{result[2]:.3f}ms")
        send_msg2 = MessageSegment.text(f"\n每日一言：{text}")
        await private_pic_message.finish(Message([send_msg1, send_msg2]))
