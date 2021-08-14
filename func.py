import json
import time
import asyncio
import bilibili_api

from xpinyin_n import Pinyin
from PyQt5.QtWidgets import QMessageBox, QWidget
from bilibili_api.live import LiveDanmaku
from PyQt5.QtCore import QThread, pyqtSignal

sc_msg = []
gift_msg = []
enter_msg = []
combo_msg = []
dan_mu_msg = []
effect_enter_msg = []
with open('setting.json', 'r+') as f_obj:
    room_display_id = json.load(f_obj)['room']

room = LiveDanmaku(room_display_id=room_display_id)
p = Pinyin()


def label_style(size=14, font='Arial', bold='', color='rgb(205, 13, 73)', background='rgb', border_image='image_url'):
    if background == 'rgb' or background == '':
        background = ''
    else:
        background = f';background-color: {background};'
    if border_image == 'image_url' or border_image == '':
        border_image = ''
    else:
        border_image = f';border-image: url(:{border_image});'
    style = f'font:{bold} {size}pt \"{font}\";border-radius:10px;color:{color}{background}{border_image}'
    return style


def read_setting():
    with open('setting.json', 'r+') as f:
        set_dict = json.load(f)
    return set_dict


def save_setting(set_dicts):
    with open('setting.json', 'w+') as f_obj1:
        json.dump(set_dicts, f_obj1)


def get_py(string='无参数 '):
    or_list, a_str = is_Chinese(string)
    remove_list, a_str = is_illegal(or_list, a_str)
    illegal_word, a_str, f_word = remove_illegal(remove_list, a_str)
    f_list, s_list = remove_py_illegal(illegal_word, a_str, f_word)
    return f_list, s_list


def get_str(msg):  # 解析json内容并分发任务
    user = is_Chinese(str(msg["data"]["info"][2][1]))
    com = is_Chinese(str(msg["data"]["info"][1]))
    return user, com


def turn_to(a_str):  # 返回汉字+拼音
    lists = list()
    py_list = p.get_pinyin(a_str, tone_marks='marks').split('-')
    for i, n in enumerate(a_str):
        lists.append(n)
        try:
            lists.append(py_list[i])
        except IndexError:
            pass
    return lists


def is_Chinese(a_str):  # 判断是否为汉字
    num = 0  # 不是汉字的位置编号计数
    or_dict = dict()  # 没啥用
    or_list = list()  # 位置编号列表
    for ch in a_str:
        if '\u3400' <= ch <= '\uFA2D' or \
                '\u3041' <= ch <= '\u30F4' or \
                '\u30a1' <= ch <= '\u30f3':  # 汉字utf区间(\u4e00-\u9fff)
            pass
        else:
            or_dict[num] = ch  # 没啥用
            or_list.append(num)
        num += 1  # 过一个字计数+1
    if len(or_list) == 0:  # 无不是中文字符
        # return ''.join(turn_to(a_str))
        return turn_to(a_str)
    else:
        # return is_illegal(or_list, a_str)
        return or_list, a_str  # 返回


def is_illegal(or_list, a_str):  # 将不合法字符从字符串中选出
    remove_list = list()  # 将要移除的字符或字符串的索引
    num = len(or_list)
    for n in range(0, num + 1):
        try:
            if or_list[n] - or_list[n - 1] == 1:
                pass
            else:
                if n - 1 != -1:
                    if remove_list[-1] == or_list[n - 1]:
                        remove_list.append(or_list[n - 1] + 1)
                    else:
                        remove_list.append(or_list[n - 1] + 1)
                remove_list.append(or_list[n])
        except IndexError:
            try:
                remove_list.append(or_list[n])  # 第一个不合法字符触发
            except IndexError:
                remove_list.append(or_list[-1] + 1)  # 最后一个不合法字符触发
    # return remove_illegal(remove_list, a_str)
    return remove_list, a_str  # 返回


def remove_illegal(remove_list, a_str):  # 移除非法字符
    f_word = list()  # {0[0]} 标记填充位置
    illegal_word = list()  # 切出来的字符串列表
    num = len(remove_list)
    for n in range(0, num - 1, 2):
        illegal_word.append(a_str[remove_list[n]:remove_list[n + 1]])  # 对字符串切片
    for i, word in enumerate(illegal_word):  # 标记切除的位置
        f_word.append(' {' + '0[{}'.format(str(i)) + ']} ')
        a_str = a_str.replace(word, '%^$', 1)
    # return remove_py_illegal(illegal_word, a_str, f_word)
    return illegal_word, a_str, f_word


def remove_py_illegal(illegal_word, a_str, f_word):
    new = list()  # 加好拼音的字符串列表
    word = a_str.split('%^$')  # 合法的字符串列表
    for i, n in enumerate(word):
        new.append(turn_to(n))  # 将字符串加入带拼音的列表
        try:
            new.append(illegal_word[i])
        except IndexError:
            pass
    # return me_str(new, illegal_word)
    return new, illegal_word


def me_str(f_lists, s_lists):
    # lists = merge_sentences(f_lists, 0)
    sentences = ''.join(f_lists)

    sentences = sentences.format(s_lists)
    # print(sentences)
    return sentences


"""
DANMU_MSG: 用户发送弹幕
SEND_GIFT: 礼物
COMBO_SEND：礼物连击
GUARD_BUY：续费大航海
SUPER_CHAT_MESSAGE：醒目留言（SC）
SUPER_CHAT_MESSAGE_JPN：醒目留言（带日语翻译？）
WELCOME: 老爷进入房间
WELCOME_GUARD: 房管进入房间
PREPARING: 直播准备中
LIVE: 直播开始
INTERACT_WORD: 用户进入直播间
本模块自定义事件：
VIEW: 直播间人气更新
ALL: 所有事件
DISCONNECT: 断开连接（传入连接状态码参数）
TIMEOUT: 心跳响应超时
"""


# 用户进入直播间
@room.on("INTERACT_WORD")
async def in_user(msg_json):
    msg = msg_json['data']['data']['uname'] + ' 进入直播间'
    enter_msg.append(msg)


# 弹幕
@room.on("DANMU_MSG")  # 指定事件名
async def on_dan_mu(msg_json):
    # com = ''.join(msg_json) + ' '  # 内容
    u_name = msg_json['data']['info'][2][1]
    com = msg_json['data']['info'][1]
    color = msg_json['data']['info'][2][7]
    dan_mu_msg.append(f'{u_name}: {com}{color}')
    """if com[:2] == '*-':
        color = 'rgb(125, 0, 0)'
        msg = [color, f'{u_name}: {com}']
        dan_mu_msg.append(msg)"""


# 礼物
@room.on("SEND_GIFT")
async def in_user(msg_json):
    msg = msg_json['data']['data']['uname'] + ' 投喂 ' + msg_json['data']['data']['giftName']
    gift_msg.append(msg)
    del msg


# 礼物连击
@room.on("COMBO_SEND")
async def in_user(msg_json):
    user_name = msg_json['data']['data']['uname']
    combo_num = msg_json['data']['data']['combo_num']
    gift_name = msg_json['data']['data']['gift_name']
    price = msg_json['data']['data']['combo_total_coin']
    price = '%.1f' % float(price / 1000)
    msg = f'{user_name}  {price}￥: {gift_name} × {combo_num}'
    gift_msg.append(msg)
    del user_name, combo_num, gift_name, price, msg


# 拥有进入特效的用户(舰长，提督等)进入直播间
@room.on("ENTRY_EFFECT")
async def in_user(msg_json):
    u = msg_json['data']['data']['copy_writing']
    u = u.split('<%')[1]
    u1 = u.split('%>')[0]
    msg = f'{u1} 进入直播间'
    effect_enter_msg.append(msg)
    del u, u1, msg


# sc醒目留言
@room.on("SUPER_CHAT_MESSAGE")
async def in_user(msg_json):
    user_name = msg_json['data']['data']['user_info']['uname']
    message = msg_json['data']['data']['message']
    price = msg_json['data']['data']['price']
    msg = f'{user_name}  {price}￥: {message}'
    sc_msg.append(msg)
    del user_name, message, price, msg


# 开通大航海
@room.on("GUARD_BUY")
async def in_user(msg_json):
    user_name = msg_json['data']['data']['username']
    gift_name = msg_json['data']['data']['gift_name']
    price = msg_json['data']['data']['price']
    price = '%d' % (int(price) / 1000)
    msg = f'{price}￥: {user_name} 开通了 {gift_name}'
    sc_msg.append(msg)
    del price, user_name, gift_name, msg


class RoomWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RoomWorker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 1

    def run(self):
        global room
        print("start connect")
        """with open('setting.json', 'r+') as f:
            id = json.load(f)['room']

        room = LiveDanmaku(room_display_id=id)"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.num = 0
        try:
            bilibili_api.sync(room.connect())
        except (bilibili_api.exceptions.LiveException.LiveException, RuntimeError):
            QMessageBox.information(QWidget(), '重要提示', '连接出错')


class EnterWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, parent=None):
        super(EnterWorker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 0

    def run(self):
        while self.working:
            time.sleep(0.5)
            if enter_msg:
                for msg in enter_msg:
                    self.sinOut.emit(msg)
                    enter_msg.remove(msg)


class DanMuWorker(QThread):
    sinOut = pyqtSignal(str)
    sinOut1 = pyqtSignal(list)

    def __init__(self, parent=None):
        super(DanMuWorker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 0

    def run(self):
        while self.working:
            time.sleep(0.5)
            if dan_mu_msg:
                for msg in dan_mu_msg:
                    try:
                        self.sinOut.emit(msg)
                    except TypeError:
                        self.sinOut1.emit(msg)
                    dan_mu_msg.remove(msg)


class GiftWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, parent=None):
        super(GiftWorker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 0

    def run(self):
        while self.working:
            time.sleep(0.5)
            if gift_msg:
                for msg in gift_msg:
                    self.sinOut.emit(msg)
                    gift_msg.remove(msg)


class SCWorker(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, parent=None):
        super(SCWorker, self).__init__(parent)
        # 设置工作状态与初始num数值
        self.working = True
        self.num = 0

    def run(self):
        while self.working:
            time.sleep(0.5)
            if sc_msg:
                for msg in sc_msg:
                    self.sinOut.emit(msg)
                    time.sleep(0.5)
                    sc_msg.remove(msg)


class ShowSuperMsg(QThread):

    def __init__(self, msg, parent=None):
        super(ShowSuperMsg, self).__init__(parent)
        self.msg = msg

    def run(self):
        QMessageBox.information(QWidget(), '注意!!', self.msg)
