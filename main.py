from bilibili_api import Credential, sync, live,Danmaku
from math import ceil
from time import sleep
import json
import pathlib
import sys
import os
from random import randint

credential = Credential()

"""
魔改了bilibili_api 所以你肯定没法从源码跑这个(
"""

path = os.path.dirname(os.path.abspath(__file__))+'/account.json'
print(f"账号json路径: {path}")
print(f"当前版本 v1.0.0")
with open(path, 'r') as f:
    data = json.load(f)
    sessdata, bili_jct, buvid3 = data['sessdata'], data['bili_jct'], data['buvid3']
    credential=Credential(sessdata, bili_jct, buvid3)

_live_info = sync(live.get_self_live_info(credential))
_live_guard = _live_info['count']['guard']  # 当前大航海数量
_live_fans_medal = _live_info['count']['fans_medal']  # 当前粉丝勋章数量
_live_title = _live_info['count']['title']  # 活动头衔

_live_guard_pages = ceil(_live_guard/10)  # 分页大航海页数


_danmu=["(｡･ω･｡)ﾉ♡","(^・ω・^ )","(=・ω・=)","(°∀°)ﾉ","w(ﾟДﾟ)w","Σ( ° △ °|||)"]
_danmu_len = len(_danmu)

def get_guard_list():
    _my_guards= sync(live.get_self_guards(credential,1))['list']

    for page in range(1,_live_guard_pages):
        page+=1
        sleep(0.5)
        _my_guards+=((sync(live.get_self_guards(credential,page)))['list'])
    return _my_guards
print(f"当前账号大航海数量: {_live_guard}")
_guard_list = get_guard_list()

def get_bagid_and_nums():
    call = dict()
    bag = sync(live.get_self_bag(credential))
    for item in bag['list']:
        if item['gift_id']==30725: #30725 -> 打call棒
            call[item['bag_id']]=item['gift_num']
    a=sorted(call.items(), key = lambda x:x[1], reverse=True)
    #print(a[0][0],a[0][1])
    return (a[0][0],a[0][1])


def send_call(room,bag_id):
    res = sync(room.send_gift(5702480,bag_id,30725,2))
    return res

def send_danmu(room):
    room_info = sync(room.get_room_play_info())
    if room_info['live_status']==1:
        print(f'    该直播间正在直播,跳过')
        return
    elif room_info['live_status']==0:
        print(f'    该直播间未开播,发送弹幕')
    elif room_info['live_status']==2:
        print(f'    该直播间轮播中,发送弹幕')
    else: return

    for _ in range(3):
        sleep(randint(20,25))
        danmu = _danmu[randint(0,_danmu_len-1)]
        try:
            sync(room.send_danmaku(Danmaku(danmu)))
            print(f"    {_} 发送弹幕: {danmu}")
        except:
            print(f"    {_} 发送弹幕频率过快!")

def reveive_reward(room:live.LiveRoom):
    res = sync(room.receive_reward(2))
    if res['status_code']==0:
        _rewards= ','.join([f"{item['name']}:{item['num']} " for item in res['awards_list']])
        print(f"    成功领取 {_rewards}")
    elif res['status_code']==2:
        print(f"    该直播间暂无可领取奖励.")


for i in range(1,_live_guard+1):
    print(f"{i}/{_live_guard}")
    info = _guard_list[i-1]
    #print(info)
    room2 = live.LiveRoom(info['room_id'],credential)
    sleep(1)
    print(f"进入直播间 room_id: {info['room_id']}  |  rusername: {info['rusername']}  |  live_status: {info['live_status']}")
    print(f"    尝试签到")
    #task_id = 1447 # 大航海签到
    __res=sync(room2.get_room_play_info())
    #print(__res)
    _res = sync(room2.send_task(1447))
    #print(f"    {_res}")
    print(f"    已签到")
    sleep(1)
    print(f"    尝试赠送两个打call棒")
    bag_id, nums = get_bagid_and_nums()
    print(f"    使用包裹id: {bag_id} , 此包裹剩余打call棒数量{nums}")
    if nums>=2:
        res = send_call(room2,bag_id)
        if res['send_tips']=='赠送成功':
            print(f"    赠送打call棒两个成功")
        else:
            print(f"    赠送失败")
    else:
        print(f"    打call棒数量不足")
    sleep(3)

    send_danmu(room2)

    print(f"    尝试领取奖励")
    reveive_reward(room2)
    print("\n")

    