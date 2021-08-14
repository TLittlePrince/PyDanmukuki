import sys
import main_show
from func import *
from setting_show import Ui_Form
from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QColorDialog


set_dict = read_setting()


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.set_option = set_dict
        self.loads()
        self.dan_win = None
        self.test_win = None
        self.gift_win = None
        self.enter_win = None
        self.notice_win = None
        self.connect_room = QTimer()
        self.gift_thread = GiftWorker()
        self.notice_thread = SCWorker()
        self.room_thread = RoomWorker()
        self.enter_thread = EnterWorker()
        self.dan_mu_thread = DanMuWorker()
        # self.connect_room.timeout.connect(self)
        self.ui.py_size_spin.valueChanged.connect(self.save_py_size)
        self.ui.fontComboBox.currentTextChanged.connect(self.save_font)
        self.ui.msg_space_spin.valueChanged.connect(self.save_msg_space)
        self.ui.char_size_spin.valueChanged.connect(self.save_char_size)
        self.ui.char_space_spin.valueChanged.connect(self.save_char_space)
        self.ui.py_label_h_spin.valueChanged.connect(self.save_py_label_h)
        self.ui.char_label_w_spin.valueChanged.connect(self.save_char_label_w)
        self.ui.char_label_h_spin.valueChanged.connect(self.save_char_label_h)
        self.ui.win_opacity_spin.valueChanged.connect(self.save_win_opacity_spin)
        self.ui.obj_opacity_spin.valueChanged.connect(self.save_obj_opacity_spin)
        self.ui.paragraph_space_spin.valueChanged.connect(self.save_paragraph_space)

    @pyqtSlot()
    def loads(self):
        try:
            self.ui.url_edit.setText(self.set_option['room'])
            self.ui.check_box.setChecked(self.set_option['stay'])
            self.ui.py_size_spin.setValue(self.set_option['py_size'])
            self.ui.fontComboBox.setCurrentText(self.set_option['font'])
            self.ui.msg_space_spin.setValue(self.set_option['msg_space'])
            self.ui.char_size_spin.setValue(self.set_option['char_size'])
            self.ui.char_space_spin.setValue(self.set_option['char_space'])
            self.ui.py_label_h_spin.setValue(self.set_option['py_label_h'])
            self.ui.char_label_w_spin.setValue(self.set_option['char_label_w'])
            self.ui.char_label_h_spin.setValue(self.set_option['char_label_h'])
            self.ui.win_opacity_spin.setValue(self.set_option['win_opacity_spin'])
            self.ui.obj_opacity_spin.setValue(self.set_option['obj_opacity_spin'])
            self.ui.paragraph_space_spin.setValue(self.set_option['paragraph_space'])
        except KeyError:
            pass
        pass

    @pyqtSlot()
    def make_test_connect(self):
        self.ui.py_size_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.msg_space_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.char_size_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.char_space_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.py_label_h_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.char_label_w_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.char_label_h_spin.valueChanged.connect(self.test_win.test_msg)
        self.ui.fontComboBox.currentTextChanged.connect(self.test_win.test_msg)
        self.ui.paragraph_space_spin.valueChanged.connect(self.test_win.test_msg)

    @pyqtSlot()
    def make_connect(self):
        # self.room_thread.sinOut.connect()
        self.gift_thread.sinOut.connect(self.gift_win.on_pushButton_clicked)
        self.dan_mu_thread.sinOut.connect(self.dan_win.on_pushButton_clicked)
        self.enter_thread.sinOut.connect(self.enter_win.on_pushButton_clicked)
        self.notice_thread.sinOut.connect(self.notice_win.on_pushButton_clicked)
        pass

    @pyqtSlot()
    def start_thread(self):
        self.gift_thread.start()
        self.room_thread.start()
        self.enter_thread.start()
        self.dan_mu_thread.start()
        self.notice_thread.start()

    @pyqtSlot()
    def on_win_background_button_clicked(self):
        color = QColorDialog.getColor()
        self.set_option['win_background'] = color.name()
        save_setting(self.set_option)

    @pyqtSlot()
    def on_msg_background_button_clicked(self):
        color = QColorDialog.getColor()
        self.set_option['msg_background'] = color.name()
        save_setting(self.set_option)

    @pyqtSlot()
    def on_char_color_button_clicked(self):
        color = QColorDialog.getColor()
        self.set_option['char_color'] = color.name()
        save_setting(self.set_option)

    @pyqtSlot()
    def on_py_color_button_clicked(self):
        color = QColorDialog.getColor()
        self.set_option['py_color'] = color.name()
        save_setting(self.set_option)

    @pyqtSlot()
    def on_show_set_button_clicked(self):
        self.test_win = main_show.Widget(1, '测试窗口')
        self.test_win.show()
        self.make_test_connect()

    @pyqtSlot()
    def on_start_button_clicked(self):
        self.gift_win = main_show.Widget(0, '礼物')
        self.enter_win = main_show.Widget(0, '进入')
        self.dan_win = main_show.Widget(0, '弹幕消息')
        self.notice_win = main_show.Widget(0, 'SuperChat')
        self.dan_win.show()
        self.gift_win.show()
        self.enter_win.show()
        self.notice_win.show()
        self.start_thread()
        self.make_connect()

    @pyqtSlot()
    def on_ok_button_clicked(self):
        self.set_option['room'] = self.ui.url_edit.text().split('/')[-1].split('?')[0]
        save_setting(self.set_option)

    @pyqtSlot(bool)
    def on_check_box_toggled(self, val):
        self.set_option['stay'] = val
        save_setting(self.set_option)

    @pyqtSlot(bool)
    def connect_error(self, flag):
        self.room_thread.disconnect()
        pass

    @pyqtSlot(int)
    def save_char_size(self, size):
        self.set_option['char_size'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_py_size(self, size):
        self.set_option['py_size'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_char_space(self, size):
        self.set_option['char_space'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_msg_space(self, size):
        self.set_option['msg_space'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_paragraph_space(self, size):
        self.set_option['paragraph_space'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_char_label_w(self, size):
        self.set_option['char_label_w'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_char_label_h(self, size):
        self.set_option['char_label_h'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_py_label_h(self, size):
        self.set_option['py_label_h'] = size
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_win_opacity_spin(self, opacity):
        self.set_option['win_opacity_spin'] = opacity
        save_setting(self.set_option)

    @pyqtSlot(int)
    def save_obj_opacity_spin(self, opacity):
        self.set_option['obj_opacity_spin'] = opacity
        save_setting(self.set_option)

    @pyqtSlot(str)
    def save_font(self, font):
        self.set_option['font'] = font
        save_setting(self.set_option)


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = Widget()
    win.show()
    sys.exit(app.exec_())
