import threading
import time
from . import settings
from mido import Message

DIRECTIONS = {
    "left to right": 0,
    "right to left": 1,
    "out to center": 2,
}


class Ramp(threading.Thread):
    def __init__(
        self,
        midi_out_port,
        low=0,
        high=127,
        start=0,
        step=1,
        speed=1,
        channel=0,
        control=21,
        inst_num=0,
        direction='left to right'
    ):
        threading.Thread.__init__(self)
        self.midi_out_port = midi_out_port
        self.low = low
        self.high = high
        self.step = step
        self.speed = speed
        self.channel = channel
        self.control = control
        self.inst_num = inst_num
        self.count = start
        self.up = True
        self.curr_val = 0
        self.old_val = 0
        self.direction = direction

    def run(self):
        while(settings.keep_playing):
            tmp_value = 0
            if self.direction == "left to right":
                tmp_value = int(
                    float(
                        settings.coords[self.inst_num][0] / settings.x_screen_size
                    ) * 127
                )
            elif self.direction == "right to left":
                tmp_value = 127 - int(
                    float(
                        settings.coords[self.inst_num][0] / settings.x_screen_size
                    ) * 127
                )
            elif self.direction == "out to center":
                if settings.coords[self.inst_num][0] <= (settings.x_screen_size/2):
                    tmp_value = int(
                        float(
                            settings.coords[
                                self.inst_num
                            ][0] / (settings.x_screen_size/2)
                        ) * 127
                    )
                else:
                    tmp_value = 127 - int(
                        float(
                            (settings.coords[
                                self.inst_num
                            ][0] - (settings.x_screen_size/2)) / (settings.x_screen_size/2)
                        ) * 127
                    )

            temp_step = float((tmp_value - self.old_val)/self.speed)
            for i in range(self.speed):
                self.curr_val = int(self.curr_val + temp_step)
                if self.curr_val >= self.high:
                    self.curr_val = self.high
                elif self.curr_val <= self.low:
                    self.curr_val = self.low
                print(self.curr_val)
                msg = Message(
                    'control_change',
                    channel=self.channel,
                    control=self.control,
                    value=self.curr_val
                )
                self.midi_out_port.send(msg)
                time.sleep(0.05)
            self.old_val = self.curr_val
            time.sleep(0.1)
