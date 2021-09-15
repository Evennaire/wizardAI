from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui, QtWidgets, uic
import pyaudio
import sys


class MyClient():
    def __init__(self, name, ui):
        self.ui = ui
        self.client = QtWebSockets.QWebSocket(name,QtWebSockets.QWebSocketProtocol.Version13,None)
        self.client.error.connect(self.error)
        self.client.textMessageReceived.connect(self.receive_message)
        self.client.binaryMessageReceived.connect(self.receive_binary)
        self.client.stateChanged.connect(self.ui.connect_status)
    
    def connect(self, server_addr):
        self.client.open(QtCore.QUrl(f"ws://{server_addr}"))

    def disconnect(self):
        if self.client.state() == 3:
            self.client.close()


    def send_message(self, message):
        if self.client.state() == 3: #QtWebSockets.ConnectedState:
            self.client.sendTextMessage(message)
            return True
        return False
    
    def receive_message(self, message):
        self.ui.showNormal()
        self.ui.receive_message(message)
    
    def receive_binary(self, message):
        self.ui.showNormal()
        self.ui.receive_binary(message)


    def error(self, error_code):
        print(f"ERROR: {error_code} {self.client.errorString()}")

    


class MainWindow_Client(QtWidgets.QMainWindow):
    def __init__(self, server_addr):    
        super(MainWindow_Client, self).__init__()
        self.setWindowTitle("Client")
        desktop_size = QtWidgets.QDesktopWidget().availableGeometry(self)
        self.resize(int(desktop_size.width()*0.3), int(desktop_size.height()*0.3))
        # uic.loadUi("mainwindow.ui", self)
        self.client = MyClient("Client", self)
        self.show()
        self.build()
        if server_addr:
            self.line_edit_ip.setText(server_addr)
            self.connect()

    def build(self):
        # central widget: widget
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        # add layout
        layout_client = QtWidgets.QHBoxLayout()
        self.line_edit_ip = QtWidgets.QLineEdit()
        self.button_connect = QtWidgets.QPushButton("Connect to Server")
        self.button_connect.clicked.connect(self.connect)
        self.button_disconnect = QtWidgets.QPushButton("Disconnect")
        self.button_disconnect.clicked.connect(self.client.disconnect)
        layout_client.addWidget(self.line_edit_ip)
        layout_client.addWidget(self.button_connect)
        layout_client.addWidget(self.button_disconnect)
        layout.addLayout(layout_client)

        layout_info = QtWidgets.QHBoxLayout()
        self.label_connect = QtWidgets.QLabel("Disconnected")
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
        button_send_voice = QtWidgets.QPushButton("Voice")
        button_send_voice.clicked.connect(self.send_voice)
        layout_line.addWidget(self.line_edit)
        layout_line.addWidget(button_send)
        layout_line.addWidget(button_send_voice)
        layout.addLayout(layout_line)
        self.line_edit.returnPressed.connect(button_send.click)

        layout_console = QtWidgets.QVBoxLayout()
        label_console = QtWidgets.QLabel("Console")
        # layout_console.addWidget(label_console)
        layout.addLayout(layout_console)

    def connect(self):
        if self.line_edit_ip.text() == "":
            QtWidgets.QMessageBox.critical(self, u'提示', u"请输入serverip:port")
        else:
            self.client.connect(self.line_edit_ip.text())

    def send_message(self):
        message = self.line_edit.text()
        if message == "":
            return
        if self.client.send_message(message):
            self.text_edit.append(f"{message}")
            cursor = self.text_edit.textCursor()
            textBlockFormat = cursor.blockFormat()
            textBlockFormat.setAlignment(QtCore.Qt.AlignRight)
            textBlockFormat.setLeftMargin(int(self.width()*0.3))
            textBlockFormat.setRightMargin(0)
            textBlockFormat.setTopMargin(3)
            textBlockFormat.setBottomMargin(3)
            cursor.mergeBlockFormat(textBlockFormat)
            self.text_edit.setTextCursor(cursor)

            self.line_edit.clear()

    def send_voice(self):
        pass


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
        # self.text_edit.append(f"{binary}")
        if QtWidgets.QMessageBox.question(self, u'新语音消息', u"您有一条来自智能助手的语音消息。是否播放？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
        #?res = QtWidgets.QMessageBox.question(self, u'新语音消息', u"是否播放？", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
            p = pyaudio.PyAudio()
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100

            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            output=True)
            data = binary
            stream.write(data)
            # # 播放  
            # while data != '':
            #     stream.write(data)
            #     data = wf.readframes(CHUNK)
            stream.stop_stream()
            stream.close()
            p.terminate()




    def connect_status(self):
        if self.client.client.state() == 3:
            self.label_connect.setText("Connected")
            self.button_connect.setEnabled(False)
            self.button_disconnect.setEnabled(True)
        else:
            self.label_connect.setText("Disconnected")
            self.button_connect.setEnabled(True)
            self.button_disconnect.setEnabled(False)

    def closeEvent(self, event):
        self.client.disconnect()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    server_addr = None
    if len(sys.argv) > 1:
        server_addr = sys.argv[1]

    window = MainWindow_Client(server_addr)
    app.exec_()

    print("Closing from UI")
    quit()