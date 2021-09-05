from PyQt5 import QtCore, QtWebSockets, QtNetwork, QtGui, QtWidgets, uic
from PyQt5.QtCore import QUrl
import sys

class MyServer():
    def __init__(self, name, ui):
        self.ui = ui
        self.server = QtWebSockets.QWebSocketServer(name, QtWebSockets.QWebSocketServer.NonSecureMode)
        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
        self.clients = []

    def setup(self):
        if self.server.listen(QtNetwork.QHostAddress.LocalHost, 1302):
            print(f"INFO: Listening {self.server.serverName()}:{self.server.serverAddress().toString()}:{str(self.server.serverPort())}")
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

    def receive_message(self, message):
        self.ui.receive_message(message)


    def onAcceptError(accept_error):
        print("INFO: Accept Error: {}".format(accept_error))

    def onNewConnection(self):
        print("INFO: new Client connected!")
        self.clientConnection = self.server.nextPendingConnection()
        
        self.clientConnection.textMessageReceived.connect(self.receive_message)
        self.clientConnection.disconnected.connect(self.socketDisconnected)
        self.clients.append(self.clientConnection)
        self.ui.label_connect.setText("Connected")

    def socketDisconnected(self):
        print("INFO: socket disconnected")
        if self.clientConnection:
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()
        if self.server.isListening():
            self.ui.label_connect.setText("Listening..")




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

    def build(self):
        # central widget: widget
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        # add layout
        layout_server = QtWidgets.QHBoxLayout()
        self.button_setupserver = QtWidgets.QPushButton("Setup Server")
        self.button_setupserver.clicked.connect(self.server.setup)
        self.button_closeserver = QtWidgets.QPushButton("Close Server")
        self.button_closeserver.clicked.connect(self.server.close)
        layout_server.addWidget(self.button_setupserver)
        layout_server.addWidget(self.button_closeserver)
        layout.addLayout(layout_server)

        layout_info = QtWidgets.QHBoxLayout()
        self.label_connect = QtWidgets.QLabel("is Listening: ")
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
        layout_line.addWidget(self.line_edit)
        layout_line.addWidget(button_send)
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

    def closeEvent(self, event):
        self.server.close()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    app.exec_()

    print("Closing from UI")
    quit()
