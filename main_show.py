import gc
import os
import sys
import weakref
from func import *
import py_resource
from PyQt5 import sip
from background import Ui_Form
from PyQt5.QtGui import QWheelEvent, QMouseEvent, QMoveEvent
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QLabel, QPushButton
from PyQt5.QtCore import pyqtSlot, QRect, QParallelAnimationGroup, QPropertyAnimation, \
    QCoreApplication, Qt, QSize, QPoint, QTimer

print(f'pid:{os.getpid()}')


class MyLabel(QWidget):
    def __init__(self, f_list, string, win_size, show_type, parent=None):
        super().__init__(parent)
        self.labels = []
        self.f_list = f_list
        self.enter_flag = True
        self.label_x1 = QLabel()
        self.label_x = win_size[0]  # 窗口宽
        self.label_y = win_size[1]  # 窗口高
        self.show_type = show_type
        self.string = string
        settings = read_setting()
        self.fonts = settings['font']  # 字体
        self.char_size = settings['char_size']  # 汉字字号
        self.char_label_h = settings['char_label_h']  # 汉字标签高
        self.py_size = settings['py_size']  # 拼音字号
        self.paragraph_space = settings['paragraph_space']  # 段落间隔（行距
        self.char_space = settings['char_space']  # 汉字之间间距
        self.msg_space = settings['msg_space']  # 每条消息之间间距
        self.char_label_w = settings['char_label_w']  # 汉字标签宽
        self.py_label_h = settings['py_label_h']  # 拼音标签高
        """self.win_background = settings['win_background']  # 窗口背景颜色"""
        self.char_color = settings['char_color']  # 汉字字体颜色
        self.py_color = settings['py_color']  # 拼音字体颜色
        self.w = 50
        self.en_w = 0
        self.en_h = 0
        self.up_num = 0
        self.lx = 10  # x坐标
        self.ly = self.label_y - 20  # y坐标
        self.color = ''
        del settings
        gc.collect()
        pass

    def get_label(self):
        print(self.f_list)
        if self.show_type:
            img_url = '/label_background/label_background.png'
        else:
            img_url = ''
        for num, list_or_string in enumerate(self.f_list):
            if (num % 2) == 0:  # 拼音和汉字 索引为双数0,2,4,6,8
                # i 索引值，char_or_py 元素 ; list_or_string:['语', 'yǔ', '言', 'yán', '非', 'fēi']
                for i, char_or_py in enumerate(list_or_string):
                    if (i % 2) == 0:  # 字label 索引为双数0,2,4,6,8
                        if self.lx + self.w - 10 > self.label_x:
                            self.ly += self.paragraph_space
                            self.lx = 10

                        info = {'char': char_or_py, 'x': self.lx, 'y': self.ly,
                                'style': label_style(self.char_size, font=self.fonts, color=self.char_color,
                                                     border_image=img_url),
                                'w': self.char_label_w, 'h': self.char_label_h}

                        self.labels.append(info)
                        pass
                    else:  # 拼音label 索引为单数1,3,5,7
                        char_or_py = self.supplement(char_or_py)

                        info = {'char': char_or_py, 'x': self.lx, 'y': self.ly - self.py_label_h,
                                'style': label_style(self.py_size, font=self.fonts, color=self.py_color,
                                                     border_image=img_url),
                                'w': self.char_label_w, 'h': self.py_label_h}

                        self.labels.append(info)
                        self.lx += self.char_space + self.char_label_w  # 换行，随字体大小变化来变化
                        pass
                        """elif list_or_string == ':' and self.enter_flag:
                self.ly += self.paragraph_space
                self.lx = 10
                self.enter_flag = False"""

            else:  # 不是双数为英语/符号label
                if ': ' in list_or_string and self.enter_flag:
                    new_list = list_or_string.split(': ')
                    new_list.insert(1, ': ')
                    for i, en in enumerate(new_list):
                        self.create_en_label(en, img_url)
                        if i == 1:
                            self.ly += self.paragraph_space
                            self.lx = 10
                            self.enter_flag = False
                else:
                    self.create_en_label(list_or_string, img_url)
                if '*-' in list_or_string:
                    self.color = '#ff8385'
                pass
            pass
        up_num = self.label_y - self.ly - self.py_label_h
        up_num1 = self.label_y - self.ly - self.en_h
        self.up_num = up_num if up_num < up_num1 else up_num1
        self.make_align(self.up_num - self.paragraph_space + 10)
        min_w, min_h, max_w, max_h = self.find_extreme()
        print(max_h, min_h)
        del self.fonts, self.char_size, self.char_label_h, \
            self.py_size, self.paragraph_space, self.char_space, \
            self.msg_space, self.char_label_w, self.py_label_h, \
            self.char_color, self.py_color
        gc.collect()
        return self.labels, min_w, min_h, max_w, max_h, self.color

    @pyqtSlot()
    def create_en_label(self, en, img_url):
        if not en:
            pass
        else:
            self.en_w, self.en_h = self.get_label_info(en, style=label_style(self.char_size,
                                                                             font=self.fonts,
                                                                             border_image=img_url))

            if self.lx + self.en_w - 10 > self.label_x:
                self.ly += self.paragraph_space
                self.lx = 10

            info = {'char': en, 'x': self.lx, 'y': self.ly,
                    'style': label_style(self.char_size, font=self.fonts, color=self.char_color,
                                         border_image=img_url),
                    'w': self.en_w, 'h': self.en_h}

            self.labels.append(info)
            self.lx += self.char_space + self.en_w

    @pyqtSlot()
    def get_label_info(self, zh, style=label_style()):  # 获取label宽高
        self.label_x1 = QLabel(zh, self)
        self.label_x1.move(0, 0)
        self.label_x1.setStyleSheet(style)
        self.label_x1.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.label_x1.show()
        w = self.label_x1.width()
        h = self.label_x1.height()
        sip.delete(self.label_x1)
        del self.label_x1
        return w, h

    @pyqtSlot()
    def make_align(self, up_num):  # 句子与底部对齐
        label_len = len(self.labels)
        for i in range(label_len):
            self.labels[i]['y'] += up_num
            pass
        pass

    @pyqtSlot()
    def find_extreme(self):  # 左上点和右下点
        min_w = 99999  # 左x坐标
        max_w = 0  # 右x坐标
        min_h = 99999  # 左上y坐标
        max_h = 0  # 右下y坐标
        for info in self.labels:
            if info['x'] <= min_w:
                min_w = info['x']
            elif info['x'] + info['w'] > max_w:
                max_w = info['x'] + info['w']
            if info['y'] <= min_h:
                min_h = info['y']
            elif info['y'] + info['h'] > max_h:
                max_h = info['y'] + info['h']
        return min_w, min_h, max_w, max_h

    @pyqtSlot()
    def supplement(self, char):
        # 拼音补充
        s = {'罖': 'wǎng', '椛': 'huā', '穒': 'ke', '㿟': 'bái',
             '尛': 'mó', '丷': 'bā', '橴': 'zǐ', '凪': 'zhǐ', '訁': 'yán',
             '辻': 'shí', '匁': 'liǎng'}
        try:
            return s[char]
        except KeyError:
            """if self.labels[-1]['char'] == char:
                with open('char_no_in.txt', 'a+') as f:
                    f.write(char)"""
            return char
        finally:
            del s
        pass


class Widget(QWidget):
    # 移动参数
    _startPos = None
    _endPos = None

    def __init__(self, show_type, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.label_xs = []  # 所有消息标签列表
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle(self.title)
        self.max_h = 0  # 储存最后一个背景标签的y+h，往下滚动时归位要用到
        self.move_flag = True
        self.press_flag = 0  # 按下鼠标的标志
        self.resize_flag = 0  # 松开鼠标标志
        self.label_x = QLabel()  # 单个列表初始化
        self.show_type = show_type  # 是否显示网格0, 1
        self.title_label = QLabel()  # 标题label初始化
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.del_animation)
        if self.title != 'SuperChat':
            self.time_clear = QTimer(self)
            self.time_clear.timeout.connect(self.clear_label)
            self.time_clear.start(600000)
        self.setMouseTracking(True)  # 设置在窗口内的鼠标移动追踪
        size = read_setting()[self.title + 'size']  # 读取不同功能的窗口的大小
        self.resize(size[0], size[1])  # 应用读取的大小
        d = read_setting()[self.title]  # 读取对应标题的窗口位置
        self.move(d[0], d[1])  # 移动窗口到此位置
        self.exit_button = QPushButton()  # 关闭按钮的初始化
        self.clear_button = QPushButton()  # 清空按钮的初始化
        self.goto_last_button = QPushButton()  # 转到最新按钮的初始化
        self.animation = QParallelAnimationGroup(self)  # 动画组
        self.background_label = QLabel(self)  # 消息背景的初始化
        self.background_label.setMouseTracking(True)
        self.background_label.setGeometry(QRect(0, 0, 3080, 2160))  # 窗口背景的初始化
        self.background_label.setStyleSheet("image: url(:/label_background/gui_back.png);")  # 设置背景图
        # self.setStyleSheet('border-image: url(:/label_background/gui_back.png);')

    @pyqtSlot()
    def resizeEvent(self, a0: QSize) -> None:
        settings = read_setting()
        val = a0.size()
        settings[self.title + 'size'] = (val.width(), val.height())  # str(a0.size()).split('(')[-1].split(')')[0]
        save_setting(settings)

    @pyqtSlot()
    def moveEvent(self, a0: QMoveEvent) -> None:
        settings = read_setting()
        val = a0.pos()
        settings[self.title] = (val.x(), val.y())  # str(a0.size()).split('(')[-1].split(')')[0]
        save_setting(settings)

    @pyqtSlot()
    def wheelEvent(self, a0: QWheelEvent) -> None:
        s = a0.angleDelta()
        self.move_label(s.y())
        """
        an = weakref.proxy(self.animation)
        self.make_label_up(s.y())
        an.start()
        self.timer.start(1000)"""
        pass

    @pyqtSlot()
    def enterEvent(self, event):  # 鼠标移进时调用
        # self.setCursor(Qt.CrossCursor)  # 设置鼠标形状。
        self.background_label.setStyleSheet("image: url(:/label_background/gui_back_2.png);")  # 设置深背景
        # size = read_setting()['size']
        self.create_title()

    @pyqtSlot()
    def leaveEvent(self, event):  # 鼠标移出时调用
        self.background_label.setStyleSheet("image: url(:/label_background/gui_back.png);")  # 设置浅背景
        a = self.findChild(QPushButton, 'exit'), self.findChild(QLabel, 'title'), \
            self.findChild(QPushButton, 'clear'), self.findChild(QPushButton, 'goto')
        for obj in a:
            try:
                sip.delete(obj)  # 删除标题和关闭按钮
            except TypeError:
                pass

    @pyqtSlot()
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        size = read_setting()[self.title + 'size']
        a = a0.pos()
        self.resize_flag = self.is_resize(a, size)
        if self.press_flag:
            self.make_resize(self.resize_flag, a)

    @pyqtSlot()
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.press_flag = True
        self._startPos = QPoint(a0.x(), a0.y())

    @pyqtSlot()
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.press_flag = False
        self.move_flag = True
        self._startPos = None
        self._endPos = None

    @pyqtSlot()
    def make_resize(self, direction, pos):
        if not direction:
            pass
        # 左上
        elif direction == 1:
            self.resize(self.width() - pos.x(), self.height() - pos.y())
            self.move(self.x() + pos.x(), self.y() + pos.y())
        # 上
        elif direction == 2:
            self.resize(self.width(), self.height() - pos.y())
            self.move(self.x(), self.y() + pos.y())
        # 移动窗口
        elif direction == 3:
            self._endPos = pos - self._startPos
            self.move(self.pos() + self._endPos)
            self.move_flag = False
        # 右
        elif direction == 4:
            self.resize(pos.x(), self.height())
        # 右下
        elif direction == 5:
            self.resize(pos.x(), pos.y())
        # 下
        elif direction == 6:
            self.resize(self.width(), pos.y())
        # 左
        elif direction == 7:
            self.resize(self.width() - pos.x(), self.height())
            self.move(self.x() + pos.x(), self.y())

    @pyqtSlot()
    def is_resize(self, pos, win_size):
        dis = 10
        # 左上
        if self.move_flag:
            if pos.x() < dis and pos.y() < dis:
                self.setCursor(Qt.SizeFDiagCursor)
                ret = 1
            # 上
            elif win_size[0] - dis >= pos.x() >= dis >= pos.y():
                self.setCursor(Qt.SizeVerCursor)
                ret = 2
            # 移动窗口
            elif dis < pos.x() < win_size[0] - dis and pos.y() < 35:
                self.unsetCursor()
                ret = 3
            # 右
            elif pos.x() > win_size[0] - dis and dis <= pos.y() <= win_size[1] - dis:
                self.setCursor(Qt.SizeHorCursor)
                ret = 4
            # 右下
            elif pos.x() >= win_size[0] - dis and pos.y() >= win_size[1] - dis:
                self.setCursor(Qt.SizeFDiagCursor)
                ret = 5
            # 下
            elif dis <= pos.x() <= win_size[0] - dis and pos.y() >= win_size[1] - dis:
                self.setCursor(Qt.SizeVerCursor)
                ret = 6
            # 左
            elif pos.x() < dis <= pos.y() <= win_size[1] - dis:
                self.setCursor(Qt.SizeHorCursor)
                ret = 7
            else:
                self.unsetCursor()
                ret = 0
        else:
            ret = 3
        return ret

    @pyqtSlot()
    def del_animation(self):
        sip.delete(self.animation)
        self.animation = QParallelAnimationGroup(self)

    @pyqtSlot()
    def test_msg(self):
        string = '小王子: 这是一条测试语句，剑阁峥嵘而崔嵬チョコレート，一夫爽if当关clicked，万夫莫open。所守或匪亲，化为狼与豺。'
        self.on_pushButton_clicked(string)

    @pyqtSlot()
    def create_title(self):
        size = self.x(), self.y(), self.width(), self.height()
        self.exit_button = QPushButton('╳', self)  # 显示关闭
        self.exit_button.setObjectName('exit')  # 命名为exit
        self.exit_button.setGeometry(QRect(size[2] - 20, 0, 20, 20))  # 位置始终位于右上
        self.exit_button.clicked.connect(self.on_exit_button)  # 连接槽函数
        self.exit_button.show()  # 显示按钮
        self.clear_button = QPushButton('清空', self)
        self.clear_button.setObjectName('clear')
        self.clear_button.setGeometry(QRect(size[2] - 60, 0, 40, 20))
        self.clear_button.clicked.connect(self.clear_label)
        self.clear_button.show()
        self.goto_last_button = QPushButton('转到最新消息', self)
        self.goto_last_button.setObjectName('goto')
        self.goto_last_button.setGeometry(QRect(size[2] - 140, 0, 80, 20))
        self.goto_last_button.clicked.connect(self.goto_last)
        self.goto_last_button.show()
        self.title_label = QLabel(self.title, self)
        self.title_label.setObjectName('title')
        self.title_label.setGeometry(QRect(0, 0, 85, 20))
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.title_label.setStyleSheet(label_style(size=9, color='rgb(255, 255, 255)', background='rgb(0,0,0)'))
        self.title_label.show()
        self.title_label.setMouseTracking(True)

    @pyqtSlot(str)
    def on_pushButton_clicked(self, string):
        # an = weakref.proxy(self.animation)
        settings = read_setting()
        s = 1
        color = ''
        try:
            if string[-7] == '#':
                # 含有颜色信息的弹幕
                s = 0
                color = string[-7:]  # 颜色
                string = string[:-7]  # 句子
        except IndexError:
            pass

        # 调用
        f_list, s_list = get_py(string)
        my_label = MyLabel(f_list, string, (self.width(), self.height()), self.show_type)
        lists, left_x, left_y, right_x, right_y, colors = my_label.get_label()
        if colors == '' and s:
            color = settings['msg_background']
        elif color != '' and colors != '':
            color = colors
        # self.make_label_up(left_y - right_y - settings['msg_space'])
        self.move_label(left_y - right_y - settings['msg_space'])
        maxY = self.find_minY()
        if maxY > right_y:
            t_len = len(lists)
            for i in range(t_len):
                lists[i]['y'] = maxY + lists[i]['y'] - right_y
            self.create_msg(lists, left_x, left_y + maxY - right_y, right_x, right_y + maxY - right_y, color)
        else:
            self.create_msg(lists, left_x, left_y, right_x, right_y, color)
        # an.start()
        for _ in locals().keys():
            del _
        # gc.collect()
        # self.timer.start(1000)
        self.if_limit()
        # self.animation = QParallelAnimationGroup(self)

    @pyqtSlot()
    def on_exit_button(self):  # 右上exit的槽函数
        for _ in self.label_xs:
            sip.delete(_)
        gc.collect()
        self.close()

    @pyqtSlot()
    def create_msg(self, lists, left_x, left_y, right_x, right_y, color):
        self.create_label('', left_x-5, left_y-5, label_style(background=color),
                          w=right_x - left_x+10, h=right_y - left_y+10, start_x=left_x, start_y=right_y)

        self.max_h = right_y
        for self.obj in lists:
            try:

                self.create_label(self.obj['char'], self.obj['x'], self.obj['y'], w=self.obj['w'],
                                  h=self.obj['h'], style=self.obj['style'], start_x=left_x, start_y=right_y)

            except KeyError:

                self.create_label(self.obj['char'], self.obj['x'], self.obj['y'],
                                  w=self.obj['w'], h=self.obj['h'], start_x=left_x, start_y=right_y)

    @pyqtSlot()
    def create_label(self, zh, x, y, style=label_style(), w=0, h=0, start_x=0, start_y=0):  # 创造label
        """global n
        n += 1"""
        self.label_x = QLabel(zh, self)
        """name = 'label' + str(n)
        self.label_x.setObjectName(name)"""
        if w == 0 and h == 0:
            self.label_x.move(x, y)
        else:
            self.label_x.setGeometry(QRect(x, y, w, h))
        self.label_x.setStyleSheet(style)
        self.label_x.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.label_x.show()
        self.label_xs.append(self.label_x)
        self.label_x.setMouseTracking(True)
        # self.add_animate(self.label_x, x, y, w, h, start_x, start_y, 0, 0)

    @pyqtSlot()
    def add_animate(self, obj, x, y, w, h, start_x, start_y, start_w, start_h):
        animate = QPropertyAnimation(self)
        animate.setTargetObject(obj)
        animate.setPropertyName(b'geometry')
        animate.setStartValue(QRect(start_x, start_y, start_w, start_h))  # 设置起始点;初始尺寸
        animate.setEndValue((QRect(x, y, w, h)))  # 设置终点；终止尺寸
        animate.setDuration(30)  # 时长单位毫秒
        an = weakref.proxy(self.animation)
        an.addAnimation(animate)
        # sip.delete(animate)

    @pyqtSlot()
    def make_label_up(self, move_len):
        for lab in self.label_xs:
            self.add_animate(lab, lab.x(), lab.y() + move_len, lab.width(),
                             lab.height(), lab.x(), lab.y(), lab.width(), lab.height())

    @pyqtSlot()
    def goto_last(self):
        move_len = self.height() - 20 - self.find_minY()
        self.make_label_up(move_len)
        an = weakref.proxy(self.animation)
        an.start()
        self.timer.start(800)
        # self.animation = QParallelAnimationGroup(self)

    @pyqtSlot()
    def clear_label(self):  # 清除label
        try:
            try:
                for _ in self.label_xs:
                    sip.delete(_)
                    del _
            except RuntimeError:
                pass
        except TypeError:
            error_title = 'Error'
            error_info = '无标签'
            QMessageBox.information(self, error_title, error_info)
        self.label_xs = []
        self.time_clear.start(600000)
        gc.collect()
        print('clear!')

    @pyqtSlot()
    def move_label(self, move_len):
        for obj in self.label_xs:
            try:
                x, y, h = obj.x(), obj.y(), obj.height()
                y = y + move_len
                obj.move(x, y)
                """if y + h + 150 <= 0:
                    self.label_xs.remove(obj)
                    sip.delete(obj)"""
                for _ in locals().keys():
                    # sip.delete(_)
                    del _
            except (AttributeError, RuntimeError):
                pass

    @pyqtSlot()
    def if_limit(self):
        limit = 1000
        now_num = len(self.label_xs)
        print(f'{self.title} now_num:{now_num}')
        try:
            if now_num > limit:
                num = now_num - limit
                for _ in range(num):
                    sip.delete(self.label_xs[_])
                    del self.label_xs[_]
        except (IndexError, RuntimeError):
            pass

    @pyqtSlot()
    def find_minY(self):
        try:
            obj1 = self.label_xs[-1]
            obj2 = self.label_xs[-2]
            obj1_l = obj1.height() + obj1.y()
            obj2_l = obj2.height() + obj2.y()
            return obj1_l if obj1_l > obj2_l else obj2_l
        except (IndexError, RuntimeError):
            return 0


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = Widget(0, '直接运行的窗口')
    # win.setAttribute(Qt.WA_TranslucentBackground)
    win.show()
    sys.exit(app.exec_())
