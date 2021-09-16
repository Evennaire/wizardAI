import os
import sys
import threading
import pyaudio
from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui, QtWidgets

import faulthandler
faulthandler.enable()

sys.path.append("..")
from utils import VoiceRecorder, VoicePlayer


class MyServer():
    def __init__(self, name, ui):
        self.ui = ui
        self.server = QtWebSockets.QWebSocketServer(name, QtWebSockets.QWebSocketServer.NonSecureMode)
        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
        self.port = 1302
        self.clients = []

    def setup(self):
        if self.server.listen(QtNetwork.QHostAddress.Any, self.port):
            print(f"INFO: Listening {self.server.serverName()}:{self.server.serverAddress().toString()}:{str(self.server.serverPort())}")
            for address in QtNetwork.QNetworkInterface().allAddresses():
                if address.protocol() == QtNetwork.QAbstractSocket.IPv4Protocol and address.toString() != "127.0.0.1":
                    print(address.toString())
                    self.ui.label_ipaddr.setText(f"{address.toString()}:{self.port}")
            # print(QtNetwork.QNetworkInterface().allAddresses()[1].toString())
        else:
            print("WARNING: server already listening")
            return
        self.clientConnection = None
        print("INFO: server set up", self.server.isListening())
        self.ui.label_connect.setText("Listening..")
        self.ui.button_setupserver.setEnabled(False)
        self.ui.button_closeserver.setEnabled(True)

    def close(self):
        for client in self.clients:  
            client.close()
        self.server.close()
        print("INFO: server closed", self.server.isListening())
        self.ui.label_connect.setText("Closed")
        self.ui.button_setupserver.setEnabled(True)
        self.ui.button_closeserver.setEnabled(False)


    def send_message(self, message):
        if len(self.clients) > 0:
            for client in self.clients:  
                client.sendTextMessage(message)
            return True
        return False

    def send_binary(self, binary):
        if len(self.clients) > 0:
            for client in self.clients:  
                client.sendBinaryMessage(QtCore.QByteArray(binary))
            return True
        return False

    def receive_message(self, message):
        self.ui.receive_message(message)
    
    def receive_binary(self, message):
        self.ui.receive_binary(message)


    def onAcceptError(accept_error):
        print("INFO: Accept Error: {}".format(accept_error))

    def onNewConnection(self):
        print("INFO: new Client connected!")
        self.clientConnection = self.server.nextPendingConnection()

        self.clientConnection.textMessageReceived.connect(self.receive_message)
        self.clientConnection.disconnected.connect(self.socketDisconnected)
        self.clientConnection.binaryMessageReceived.connect(self.receive_binary)
        self.clients.append(self.clientConnection)
        self.ui.label_connect.setText("Connected")

    def socketDisconnected(self):
        print("INFO: socket disconnected")
        if self.clientConnection:
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()
        if self.server.isListening():
            self.ui.label_connect.setText("Listening..")
    
    def is_connected(self):
        return len(self.clients) > 0




class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Server")
        desktop_size = QtWidgets.QDesktopWidget().availableGeometry(self)
        self.resize(int(desktop_size.width()*0.3), int(desktop_size.height()*0.5))
        # uic.loadUi("mainwindow.ui", self)
        self.server = MyServer("Server", self)
        self.show()
        self.build()
        self.server.setup()
        self.recorder = None

    def build(self):
        # central widget: widget
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        # add layout
        layout_server = QtWidgets.QHBoxLayout()
        self.label_ipaddr = QtWidgets.QLabel("ip addr")
        self.button_setupserver = QtWidgets.QPushButton("Setup Server")
        self.button_setupserver.clicked.connect(self.server.setup)
        self.button_closeserver = QtWidgets.QPushButton("Close Server")
        self.button_closeserver.clicked.connect(self.server.close)
        layout_server.addWidget(self.label_ipaddr)
        layout_server.addWidget(self.button_setupserver)
        layout_server.addWidget(self.button_closeserver)
        layout.addLayout(layout_server)

        layout_info = QtWidgets.QHBoxLayout()
        self.label_connect = QtWidgets.QLabel("status")
        self.label_ipaddr.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        button_clear = QtWidgets.QPushButton("Clear Text")
        layout_info.addWidget(self.label_connect)
        layout_info.addWidget(button_clear)
        layout.addLayout(layout_info)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        button_clear.clicked.connect(self.text_edit.clear)
        layout.addWidget(self.text_edit)

        layout_line = QtWidgets.QHBoxLayout()
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setClearButtonEnabled(True)
        button_send = QtWidgets.QPushButton("Send")
        button_send.clicked.connect(self.send_message)
        self.button_send_voice = QtWidgets.QPushButton("")
        self.button_send_voice.setIcon(QtGui.QIcon("../image/voice1.png"))
        self.button_send_voice.clicked.connect(self.send_voice)
        layout_line.addWidget(self.line_edit)
        layout_line.addWidget(button_send)
        layout_line.addWidget(self.button_send_voice)
        layout.addLayout(layout_line)
        self.line_edit.returnPressed.connect(button_send.click)

        layout_console = QtWidgets.QVBoxLayout()
        label_console = QtWidgets.QLabel("Console")
        # layout_console.addWidget(label_console)
        layout.addLayout(layout_console)


    def send_message(self):
        message = self.line_edit.text()
        if message == "":
            return
        if self.server.send_message(message):
            self.text_edit.append(f"{message}")
            cursor = self.text_edit.textCursor()
            textBlockFormat = cursor.blockFormat()
            textBlockFormat.setAlignment(QtCore.Qt.AlignRight)
            textBlockFormat.setLeftMargin(int(self.width()*0.3))
            textBlockFormat.setRightMargin(0)
            textBlockFormat.setTopMargin(3)
            textBlockFormat.setBottomMargin(3)
            # textBlockFormat.setBackground(QtCore.Qt.cyan)
            cursor.mergeBlockFormat(textBlockFormat)
            self.text_edit.setTextCursor(cursor)

            self.line_edit.clear()


    def send_voice(self):
        if not self.server.is_connected():
            return
        if self.recorder:
            self.recorder.stop_record()
            bdata = self.recorder.get_frame()
            self.server.send_binary(bdata)
            del(self.recorder)
            self.recorder = None
            self.button_send_voice.setIcon(QtGui.QIcon("../image/voice1.png"))
        else:
            self.recorder = VoiceRecorder()
            self.recorder.start_record()
            self.button_send_voice.setIcon(QtGui.QIcon("../image/voice2.png"))

        


        # text = self.line_edit.text()
        # subscription_key = "3b526f03d9ef4808af2920587b8b04b2"
        # # tts = input("Input some text to convert to speech: ")  # 控制台输入
        # tts = text
        # timestr = time.strftime("%Y%m%d-%H%M")
 
        # # # 如果需要代理
        # # proxies = {
        # #     "http": "代理地址1",
        # #     "https": "代理地址2",
        # # }
 
        # fetch_token_url = "https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        # headers = {
        #     'Ocp-Apim-Subscription-Key': subscription_key
        # }
        # response = requests.post(fetch_token_url, headers=headers,  verify=False) #proxies=proxies,
        # access_token = str(response.text)
        # print(">> 获取到Token：" + access_token)
        # constructed_url = 'https://westus.tts.speech.microsoft.com/cognitiveservices/v1'
        # headers = {
        #     # 前面带有单词 Bearer 的授权令牌
        #     'Authorization': 'Bearer ' + access_token,
 
        #     # 指定所提供的文本的内容类型。 接受的值：application/ssml+xml。
        #     'Content-Type': 'application/ssml+xml',
 
        #     # 指定音频输出格式，取值如下：
        #     # raw-16khz-16bit-mono-pcm
        #     # raw-8khz-8bit-mono-mulaw
        #     # riff-8khz-8bit-mono-alaw
        #     # riff-8khz-8bit-mono-mulaw
        #     # riff-16khz-16bit-mono-pcm
        #     # audio-16khz-128kbitrate-mono-mp3
        #     # audio-16khz-64kbitrate-mono-mp3
        #     # audio-16khz-32kbitrate-mono-mp3
        #     # raw-24khz-16bit-mono-pcm
        #     # riff-24khz-16bit-mono-pcm
        #     # audio-24khz-160kbitrate-mono-mp3
        #     # audio-24khz-96kbitrate-mono-mp3
        #     # audio-24khz-48kbitrate-mono-mp3
        #     'X-Microsoft-OutputFormat': 'raw-16khz-16bit-mono-pcm',
 
        #     # 应用程序名称，少于 255 个字符。
        #     # Chrome的 User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
        #     'User-Agent': 'Chrome/73.0.3683.86'
        # }
        # xml_body = ElementTree.Element('speak', version='1.0')
        # xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-cn')
        # voice = ElementTree.SubElement(xml_body, 'voice')
        # voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-cn')
        # # 'en-US-Guy24kRUS'，全称：'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
        # voice.set('name','en-US-Guy24kRUS')
        # voice.text = tts
        # body = ElementTree.tostring(xml_body)
        # print(">> 调用接口转换语音中......")
        # response = requests.post(constructed_url, headers=headers, data=body, verify=False) #proxies=proxies, 
        # if response.status_code == 200:
        #     fileName = 'testsound-' + timestr + '.wav'
        #     with open(fileName, 'wb') as audio:
        #         audio.write(response.content)
        #         print(">> 文本转语音已完成，生成的音频文件：" + fileName)
        # else:
        #     print("[失败] response code: " + str(response.status_code)
        #             + "\nresponse headers: " + str(response.headers) )







        # message = "test"
        # if self.server.send_message(message):
        #     self.text_edit.append(f"{message}")



    def receive_message(self, message):
        self.text_edit.append(f"{message}")
        cursor = self.text_edit.textCursor()
        textBlockFormat = cursor.blockFormat()
        textBlockFormat.setAlignment(QtCore.Qt.AlignLeft)
        textBlockFormat.setRightMargin(int(self.width()*0.3))
        textBlockFormat.setLeftMargin(0)
        textBlockFormat.setTopMargin(3)
        textBlockFormat.setBottomMargin(3)
        cursor.mergeBlockFormat(textBlockFormat)
        self.text_edit.setTextCursor(cursor)
    
    def receive_binary(self, binary):
        if QtWidgets.QMessageBox.question(self, u'新语音消息', u"您有一条来自智能助手的语音消息。是否播放？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
            player = VoicePlayer(binary)
            player.start()

    def closeEvent(self, event):
        self.server.close()
    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    app.exec_()

    print("Closing from UI")
    quit()
