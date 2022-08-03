import threading
import time
from . import settings
import mido
from mido import Message


class Ramp(threading.Thread):
    def __init__(
        self,
        low=0,
        high=127,
        start=0,
        step=1,
        speed=1,
        channel=1,
        control=1
    ):
        threading.Thread.__init__(self)
        self.low = low
        self.high = high
        self.step = step
        self.speed = speed
        self.channel = channel
        self.control = control
        self.count = start
        self.up = True
        self.port = mido.open_output()
        self.local_keep_playing = True

    def run(self):
        while(settings.keep_playing):
            if self.local_keep_playing:
                if self.count <= self.low:
                    self.up = True
                elif self.count >= self.high:
                    self.up = False
                if self.up:
                    self.count += self.step
                else:
                    self.count -= self.step
                msg = Message(
                    'control_change',
                    channel=self.channel,
                    control=self.control,
                    value=self.count
                )
                self.port.send(msg)
                time.sleep(float(1/self.speed))
        self.port.panic()
        self.port.close()

    def stop_thread(self):
        print("shutting down ramp")
        self.local_keep_playing = False

    def resume_thread(self):
        print("starting up ramp")
        self.local_keep_playing = True
