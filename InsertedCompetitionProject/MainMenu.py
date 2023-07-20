# -*-coding:utf-8 -*-
import sys
import time
import threading

import paho.mqtt.client as mqtt
import time
import hashlib
import hmac
import random
import json

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import socket

ld1 = [' ', ' ', '', '', '']
ld_length = 0
ld = 0
temp = 0.0
epoch = 0


class MyWidget(QWidget):
    signal_event = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.resize(900, 500)
        self.setWindowTitle("MainWindow")
        self.setStyleSheet("border-image: url:(./picture.jpg)")
        # 创建主界面垂直布局，用来装显示信息
        self.m_menu = QVBoxLayout()
        # 标题显示
        self.title = QLabel("Real-Time-Chart")
        self.title.setStyleSheet("font: bold; font-size: 30px; ")
        self.title.setAlignment(Qt.AlignCenter)

        # 创建水平布局1，用来显示温度的详细信息
        self.temp_layout = QHBoxLayout()
        self.temp_lable = QLabel("Temprture:")
        self.temp_dis_lable = QLabel(str(temp))
        self.highThreshold1_lable = QLabel("60")
        self.lowThreshold1_lable = QLabel("0")
        self.state1_lable = QLabel("Online")

        self.temp_layout.addWidget(self.temp_lable)
        self.temp_layout.addWidget(self.temp_dis_lable)
        self.temp_layout.addWidget(self.highThreshold1_lable)
        self.temp_layout.addWidget(self.lowThreshold1_lable)
        self.temp_layout.addWidget(self.state1_lable)
        self.temp_layout.setContentsMargins(200, 0, 200, 0)

        self.temp_layout.setStretchFactor(self.temp_lable, 1)
        self.temp_layout.setStretchFactor(self.temp_dis_lable, 3)
        self.temp_layout.setStretchFactor(self.highThreshold1_lable, 3)
        self.temp_layout.setStretchFactor(self.lowThreshold1_lable, 3)
        self.temp_layout.setStretchFactor(self.state1_lable, 1)

        # 创建水平布局2，用来显示湿度的详细信息
        self.humid_layout = QHBoxLayout()
        self.humid_lable = QLabel("Humidity:  ")
        self.humid_dis_lable = QLabel(str(humid))
        self.highThreshold2_lable = QLabel("80")
        self.lowThreshold2_lable = QLabel("0")
        self.state2_lable = QLabel("Online")

        self.humid_layout.addWidget(self.humid_lable)
        self.humid_layout.addWidget(self.humid_dis_lable)
        self.humid_layout.addWidget(self.highThreshold2_lable)
        self.humid_layout.addWidget(self.lowThreshold2_lable)
        self.humid_layout.addWidget(self.state2_lable)
        self.humid_layout.setContentsMargins(200, 0, 200, 0)

        self.humid_layout.setStretchFactor(self.humid_lable, 1)
        self.humid_layout.setStretchFactor(self.humid_dis_lable, 3)
        self.humid_layout.setStretchFactor(self.highThreshold2_lable, 3)
        self.humid_layout.setStretchFactor(self.lowThreshold2_lable, 3)
        self.humid_layout.setStretchFactor(self.state2_lable, 1)

        # 创建水平布局3，用来显示光强的详细信息
        self.light_layout = QHBoxLayout()
        self.light_lable = QLabel("Light:    ")
        self.light_dis_lable = QLabel(str(ld))
        self.highThreshold3_lable = QLabel("50000")
        self.lowThreshold3_lable = QLabel("0")
        self.state3_lable = QLabel("Online")

        self.light_layout.addWidget(self.light_lable)
        self.light_layout.addWidget(self.light_dis_lable)
        self.light_layout.addWidget(self.highThreshold3_lable)
        self.light_layout.addWidget(self.lowThreshold3_lable)
        self.light_layout.addWidget(self.state3_lable)
        self.light_layout.setContentsMargins(200, 0, 200, 0)

        self.light_layout.setStretchFactor(self.light_lable, 1)
        self.light_layout.setStretchFactor(self.light_dis_lable, 3)
        self.light_layout.setStretchFactor(self.highThreshold3_lable, 3)
        self.light_layout.setStretchFactor(self.lowThreshold3_lable, 3)
        self.light_layout.setStretchFactor(self.state3_lable, 1)

        # 将水平布局1\2\3放进主界面垂直布局器
        self.m_menu.addWidget(self.title)
        self.m_menu.addStretch()
        self.m_menu.addLayout(self.temp_layout)
        self.m_menu.addLayout(self.humid_layout)
        self.m_menu.addLayout(self.light_layout)
        self.m_menu.addStretch()

        # 创建下载日志和更新数据按钮
        self.log_button = QPushButton("Download Log")
        self.log_button.setGeometry(750, 400, 100, 50)
        self.log_button.setStyleSheet("font:bold; font-size:20; color:(128, 128, 128); ")
        self.update_button = QPushButton("Update Data")
        self.update_button.setGeometry(650, 400, 100, 50)
        self.update_button.setStyleSheet("font:bold; font-size:20; color:(128, 128, 128); ")
        # 将垂直主布局器加入到窗口
        self.setLayout(self.m_menu)
        # 将日志下载按钮和更新日志按钮加入窗口
        self.log_button.setParent(self)
        self.update_button.setParent(self)
        palette = QPalette()
        palette.setBrush(self.backgroundRole(),
                         QBrush(QPixmap("./picture.jpg").scaled(self.size(),
                                                                Qt.IgnoreAspectRatio,
                                                                Qt.SmoothTransformation)))
        self.setPalette(palette)
        # 关联信号与槽
        self.log_button.clicked.connect(self.log_window)
        self.log_button.clicked.connect(self.close)
        self.update_button.clicked.connect(self.startThread)
        self.signal_event.connect(self.update_info)

        self.link_iot()
        self.alert()
        self.Online()

    # def paintEvent(self):
    #     painter = QPainter(self)
    #     pixmap = QPixmap("./picture.jpg")
    #     painter.drawPixmap(self.rect(), pixmap)

    def link_iot(self):
        self.client = getAliyunIoTClient()
        # client.on_connect = on_connect
        # client.on_message = on_message
        self.client.connect(HOST, 1883, 300)
        print("Link Alinet Platform...")
        payload_json = {
            'id': int(time.time()),
            'params': {
                'temp': temp,  # 随机温度
                'humid': humid,  # 随机相对湿度
                'ld': ld  # 随机光强
            },
            'method': "thing.event.property.post"
        }
        print('send data to iot server: ' + str(payload_json))
        self.client.loop_start()
        self.client.publish(PUB_TOPIC, payload=str(payload_json), qos=1)
        print("Upload Success")
        # client.loop_forever()

    def update_iot(self,temp_update, humid_update, ld_update):
        print("Link Alinet success")

        payload_json = {
            'id': int(time.time()),
            'params': {
                'temp': temp_update,  # 随机温度
                'humid': humid_update,  # 随机相对湿度
                'ld': ld_update  # 随机光强
            },
            'method': "thing.event.property.post"
        }
        # print('send data to iot server: ' + str(payload_json))
        # self.client.loop_start()
        self.client.publish(PUB_TOPIC, payload=str(payload_json), qos=1)
        print("Transimision sFuccess")
        print("")

    def alert(self):
        if temp > float(self.highThreshold1_lable.text()) or temp < float(self.lowThreshold1_lable.text()):
            # 数据颜色变成黄色
            self.temp_dis_lable.setStyleSheet("background:yellow")
            print("temperature out of range")
        else:
            self.temp_dis_lable.setStyleSheet("background:white")
            # 提示错误信息
            print("temprature out of range")
        if humid > float(self.highThreshold2_lable.text()) or humid < float(self.lowThreshold2_lable.text()):
            # 数据颜色变成黄色
            self.humid_dis_lable.setStyleSheet("background:yellow")
            # 提示错误信息
            print("humidity out of range")
        else:
            self.humid_dis_lable.setStyleSheet("background:white")

        if ld > int(self.highThreshold3_lable.text()) or ld < int(self.lowThreshold3_lable.text()):
            # 数据颜色变成黄色
            self.light_dis_lable.setStyleSheet("background:yellow")
            # 提示错误信息
            print("light intensity out of range")
        else:
            self.light_dis_lable.setStyleSheet("background:white")


    def log_window(self):
        # from LogMenu import MainUi
        self.log_window_class = MainUi()
        self.log_window_class.show()

    def update_info(self,signal):
        self.temp_dis_lable.setText(str(signal[0]))
        self.humid_dis_lable.setText(str(signal[1]))
        self.light_dis_lable.setText(str(signal[2]))
        print("upload data success")
        print("")
        self.update_iot(signal[0], signal[1], int(signal[2]))
        self.Online()
        self.alert()

    def startThread(self):
        '''
        这里使用python的threading.Thread构造线程，并将线程设置为守护线程，这样
        主线程退出后守护线程也会跟着销毁
        '''
        thread = threading.Thread(target = self.get_info)
        # thread.setDaemon(True)  # 守护线程
        thread.start()  # 启动线程

    def get_info(self):
        global temp, humid, ld, ld_length, epoch
        recv_data = client_socket.recv(1024)
        # 计算光强位数
        for epoch in range(5):
            ld_length = 0
            for i in range(5):
                if recv_data[i + 20 * epoch] != 0:
                    ld_length = ld_length + 1

            temp1 = [recv_data[5 + 20 * epoch] - 48, recv_data[6 + 20 * epoch] - 48, recv_data[7 + 20 * epoch], recv_data[8 + 20 * epoch] - 48]
            humid1 = [recv_data[9 + 20 * epoch] - 48, recv_data[10 + 20 * epoch] - 48, recv_data[11 + 20 * epoch] - 48, recv_data[12 + 20 * epoch] - 48]

            ld = 0
            for i in range(ld_length):
                ld = ld + (recv_data[(ld_length - 1 - i) + epoch * 20] - 48) * pow(10, i)
            temp = temp1[0] * 10 + temp1[1] + temp1[3] * 0.1
            humid = int(humid1[0] * 10 + humid1[1] + humid1[3] * 0.1)

            # 得到信息后的动作，打印信息，开启线程
            print("begin to print data")
            signal = (temp, humid, ld)
            print("temp:%s, humidity:%s, light:%s" % (temp, humid, ld))
            self.signal_event.emit(signal)
            time.sleep(5)


    def Online(self):
        if temp<0:
            self.state1_lable.setText("offline")
            self.state1_lable.setStyleSheet("background:yellow")
        else:
            self.state1_lable.setText("online")
            self.state1_lable.setStyleSheet("background:white")

        if humid<0:
            self.state2_lable.setText("offline")
            self.state2_lable.setStyleSheet("background:yellow")
        else:
            self.state2_lable.setText("online")
            self.state2_lable.setStyleSheet("background:white")

        if ld < 0:
            self.state3_lable.setText("offline")
            self.state3_lable.setStyleSheet("background:yellow")
        else:
            self.state3_lable.setText("online")
            self.state3_lable.setStyleSheet("background:white")

class MainUi(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.th = MyThread()
        self.th.signalForText.connect(self.onUpdateText)
        sys.stdout = self.th

    def onUpdateText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def init_ui(self):
        self.setFixedSize(900, 500)
        self.setWindowTitle("Log Detail")
        self.main_layout = QVBoxLayout()  # 整体为垂直布局
        # 标题显示
        self.title = QLabel("Log Display Widget")
        self.title.setStyleSheet("font: bold; font-size: 30px; ")
        self.title.setAlignment(Qt.AlignCenter)

        self.start_layout = QHBoxLayout()
        self.start_button = QPushButton("begin")
        self.start_layout.addWidget(self.start_button)
        self.start_layout.addStretch()

        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(800)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setFixedWidth(780)
        self.process.setFixedHeight(250)
        self.process.move(30, 50)

        self.quit_log_layout = QHBoxLayout()
        self.quit_log_layout.addStretch(4)
        self.quit_log_button = QPushButton("back to Main Widget")
        self.quit_log_layout.addWidget(self.quit_log_button)
        self.quit_log_layout.addStretch(1)

        self.main_layout.addWidget(self.title)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.start_layout)
        self.main_layout.addWidget(self.process)
        self.main_layout.addLayout(self.quit_log_layout)

        self.setLayout(self.main_layout)
        # 绑定信号和槽，退回主界面
        self.start_button.clicked.connect(self.genMastClicked)
        self.quit_log_button.clicked.connect(self.main_window)
        self.quit_log_button.clicked.connect(self.close)

    def search(self):
        try:
            self.t = MyThread()
            self.t.start()
        except Exception as e:
            raise e

    def genMastClicked(self):
        """Runs the main function."""
        self.search()

        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()

    # def closeEvent(self, event):
    #     """Shuts down application on close."""
    #     # Return stdout to defaults.
    #     sys.stdout = sys.__stdout__
    #     super().closeEvent(event)

    def main_window(self):
        # from MainMenu import MyWidget
        self.main_window_class = MyWidget()
        self.main_window_class.show()

    def close_log_menu(self):
        self.main_widget.close()


class MyThread(QThread):
    signalForText = pyqtSignal(str)
    def __init__(self, data=None, parent=None):
        super(MyThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.signalForText.emit(str(text))  # 发射信号

    def run(self):
        # print("temp:%s, humidity:%s, light:%s" % (temp, humid, ld))
        time.sleep(1)



# 这个就是我们在阿里云注册产品和设备时的三元组啦
# 把我们自己对应的三元组填进去即可
options = {
    'productKey': 'ip7zJKb8jXk',
    'deviceName': 'real_monitor',
    'deviceSecret': 'e67d4c4d16ffb4392e0a239d84cd2740',
    'regionId': 'cn-shanghai'
}

HOST = options['productKey'] + '.iot-as-mqtt.' + options['regionId'] + '.aliyuncs.com'
PORT = 1883
PUB_TOPIC = "/sys/" + options['productKey'] + "/" + options['deviceName'] + "/thing/event/property/post";


# The callback for when the client receives a CONNACK response from the server.
# def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))
    # client.subscribe("the/topic")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def hmacsha1(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha1).hexdigest()


def getAliyunIoTClient():
    timestamp = str(int(time.time()))
    CLIENT_ID = "paho.py|securemode=3,signmethod=hmacsha1,timestamp=" + timestamp + "|"
    CONTENT_STR_FORMAT = "clientIdpaho.pydeviceName" + options['deviceName'] + "productKey" + options[
        'productKey'] + "timestamp" + timestamp
    # set username/password.
    USER_NAME = options['deviceName'] + "&" + options['productKey']
    PWD = hmacsha1(options['deviceSecret'], CONTENT_STR_FORMAT)
    client = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
    client.username_pw_set(USER_NAME, PWD)
    return client




def init_info():
    global temp, humid, ld, ld_length
    print("connecting to client")
    # 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定本地信息
    tcp_server_socket.bind(("", 8081))
    # 让默认的套接字由主动变为被动,允许客户端排队数量128
    tcp_server_socket.listen(128)
    # 等待客户端的连接
    client_socket, client_addr = tcp_server_socket.accept()
    print("connect clent:%s success!" % client_addr[0])
    recv_data = client_socket.recv(1024)

    # 计算光强位数
    for i in range(5):
        if recv_data[i] != 0:
            ld_length = ld_length + 1

    temp1 = [recv_data[5] - 48, recv_data[6] - 48, recv_data[7], recv_data[8] - 48]
    humid1 = [recv_data[9] - 48, recv_data[10] - 48, recv_data[11] - 48, recv_data[12] - 48]

    for i in range(ld_length):
        ld = ld + (recv_data[ld_length - 1 - i] - 48) * pow(10, i)
    temp = temp1[0] * 10 + temp1[1] + temp1[3] * 0.1
    humid = int(humid1[0] * 10 + humid1[1] + humid1[3] * 0.1)

    print(ld)
    print(temp)
    print(humid)

    return (client_socket, client_addr, recv_data)
    # client_socket.send('o')
    # client_socket.send('k')
    # client_socket.close()
    # tcp_server_socket.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client_socket, client_addr, recv_data = init_info()
    w = MyWidget()
    w.show()
    app.exec_()



