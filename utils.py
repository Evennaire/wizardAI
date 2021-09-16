import time
import threading
import pyaudio
import wave

import faulthandler
faulthandler.enable()


class VoiceRecorder():
    def __init__(self, filename="test.wav"):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 3  #需要录制的时间
        self.WAVE_OUTPUT_FILENAME = filename	#保存的文件名
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.recording_flag = False

    def start_record(self):
        self.stream = self.p.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK)
        self.recording_flag = True
        self.thread = threading.Thread(target=self.recording)
        self.thread.start()

    def recording(self):
        while self.recording_flag:
            self.frames.append(self.stream.read(self.CHUNK))

    def stop_record(self):
        self.recording_flag = False
        time.sleep(0.5)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def get_frame(self):
        return b''.join(self.frames)

    def save(self):
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')	#保存
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()


class VoicePlayer():
    def __init__(self, data=""):
        self.binary = data
    
    def start(self):
        thread = threading.Thread(target=self.play)
        thread.start()

    def play(self):
        p = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True)
        data = self.binary
        stream.write(data)
        stream.stop_stream()
        stream.close()
        p.terminate()