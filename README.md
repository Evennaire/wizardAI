# Wizard AI

通信程序，支持互发消息、发语音

## Run

wizard：`wizard/`目录下运行`python3 wizard.py`

user：`user/`目录下运行`python3 user.py`

复制wizard界面ip和端口号到user界面，connect，显示连接成功即可。

## Installation

+ PyQt5
+ pyaudio

> **windows pyaudio安装**
>
> + Find the Python version and bit number (e.g. 3.7.3 and 64bit (AMD64))
>
>   ```
>   python --version
>   ```
>
> + Find the corresponding `.whl` file: [lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
>
>   The number after `cp` is the version number and the number after `win` is the bit information
>
> + Download `.whl` file and pip install:
>
>   ```
>   pip install <filename>
>   ```

## Todo

+ 保存消息记录（到txt+wav），便于之后分析实验数据
+ 语音消息显示在聊天界面上（类似于微信语音消息）

