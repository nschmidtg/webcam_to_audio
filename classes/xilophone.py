from .image_analyzer import ImageAnalizer
from PIL import Image
from mido import Message
import threading
import numpy as np
import time
from . import settings
from .ramp import Ramp
import math
c = threading.Condition()

scales = {
    "MAJOR": [0, 2, 4, 5, 7, 9, 11],
    "DORIAN": [0, 2, 3, 5, 7, 9, 10],
    "PHRYGIAN": [0, 1, 3, 5, 7, 8, 10],
    "LYDIAN": [0, 2, 4, 6, 7, 9, 11],
    "MIXOLYDIAN": [0, 2, 4, 5, 7, 9, 10],
    "MINOR": [0, 2, 3, 5, 7, 8, 10],
    "LOCRIAN": [0, 1, 3, 5, 6, 8, 10],
}


class Xilophone(threading.Thread):
    def __init__(
        self,
        index,
        midi_channel,
        image_path,
        scale,
        root_note,
        n_scales,
        outport,
        note_length=2000,
        separation=None,  # include it for polyphonic sounds
        uncompressed=False,
        x_axis_direction='left to right',
        intervals=None
    ):
        threading.Thread.__init__(self)
        self.pause_cond = threading.Condition(threading.Lock())
        self.pause_cond.acquire()
        self.index = index
        self.paused = True
        self.poly = None
        if separation:
            self.poly = True
        self.uncompressed = uncompressed
        self.note_length = note_length
        self.midi_channel = midi_channel
        self.separation = separation
        if scale in scales.keys():
            selected_scale = scales[scale]
        elif scale == "CUSTOM":
            selected_scale = [int(note) for note in intervals.split(',')]
        self.x_axis_direction = x_axis_direction
        self.notes = []
        for i in range(n_scales):
            for note in selected_scale:
                self.notes.append(root_note + (12 * i) + note)
        max_velocity = 128
        self.current_time = 0
        self.n_notes = len(self.notes)
        image_a = ImageAnalizer()
        im = image_a.open(image_path)
        image = Image.Image.split(im)
        R = np.array(image[0])
        G = np.array(image[1])
        B = np.array(image[2])
        Grey = 0.299 * R + 0.587 * G + 0.114 * B
        W, H = Grey.shape
        delta_x = int(W/self.n_notes)
        delta_y = int(H/max_velocity)  # when using 2 synth

        # initialize prob dist
        prob_matrix = np.zeros(self.n_notes * max_velocity)
        self.notes_matrix = [None] * (self.n_notes * max_velocity)
        col_count = 0
        row_count = 0

        # populate prob dist based on white density on the image
        current = 0
        for col_count in range(0, self.n_notes):
            for row_count in range(0, max_velocity):
                self.notes_matrix[current] = "%s-%s" % (col_count, row_count)
                prob_matrix[current] = np.sum(Grey[
                    col_count * delta_x:(col_count + 1) * delta_x,
                    row_count * delta_y:(row_count + 1) * delta_y
                ])
                current += 1

        max_value = np.sum(prob_matrix)
        self.norm_probs = prob_matrix / max_value
        self.outport = outport

        # initialize midi CCs
        self.x_ramp = Ramp(
            self.outport,
            low=int(settings.params[f"MIN-{self.index}"]),
            high=int(settings.params[f"MAX-{self.index}"]),
            start=0,
            step=1,
            speed=5,
            channel=int(settings.params[f"CHANNEL-{self.index}"]) - 1,
            control=int(settings.params[f"CC-{self.index}"]),
            inst_num=self.index,
            direction=self.x_axis_direction)

    def stop_thread(self):
        if not self.paused:
            self.paused = True
            self.pause_cond.acquire()

    def resume_thread(self):
        if self.paused:
            self.paused = False
            # Notify so thread will wake after lock released
            self.pause_cond.notify()
            # Now release the lock
            self.pause_cond.release()

    def get_sum_distances(self, xilo_index):
        current = settings.coords[xilo_index]
        total = 0
        i = 0
        while i < settings.people_counter:
            total += self.calculate_distance(settings.coords[i], current)
            i += 1
        
        return total
            
    def compute_velocity_from_entropy(self):
        max_value = 20
        if settings.people_counter > 1:
            max_value = self.calculate_distance((0, 0), (settings.x_screen_size, settings.y_screen_size)) * (settings.people_counter - 1)
        velocity = -(127/max_value) * self.get_sum_distances(self.index) + 127
        print(self.index, ":", velocity)
        return min(int(velocity), 127)

    
    def calculate_distance(self, A, B):
        return math.sqrt(pow((A[0] - B[0]), 2) + pow((A[1] - B[1]), 2))


    def send_note(self, note, duration, vel):
        # print("midi", self.midi_channel)
        msg = Message(
            'note_on',
            note=note,
            velocity=self.compute_velocity_from_entropy(),
            channel=self.midi_channel
        )
        self.outport.send(msg)
        time.sleep(duration/1000)
        msg = Message(
            'note_off',
            note=note,
            channel=self.midi_channel
        )
        self.outport.send(msg)

    def join(self):
        self.x_ramp.join()
        self.resume_thread()
        super().join()

    def run(self):
        # read centroid
        self.x_ramp.start()
        while settings.keep_playing:
            with self.pause_cond:
                while self.paused:
                    # print("paused!")
                    for i in range(127):
                        msg = Message(
                            'note_off',
                            note=i,
                            channel=self.midi_channel
                        )
                        self.outport.send(msg)
                        self.x_ramp.stop_thread()
                    self.pause_cond.wait()
                # print("alive!", self.midi_channel)
                self.x_ramp.resume_thread()
                note_vel = np.random.choice(
                    self.notes_matrix,
                    p=self.norm_probs
                )
                pitch, volume = note_vel.split('-')
                pitch = int(self.notes[int(pitch)])
                volume = int(volume)
                if not self.uncompressed:
                    volume = 127
                time_sampled = max(0, np.random.normal(
                    loc=int(self.note_length),
                    scale=int(self.note_length/2)
                ))
                play_note = threading.Thread(
                    target=self.send_note,
                    args=(pitch, time_sampled, volume)
                )
                play_note.start()
                if self.poly:
                    time_separation = max(0, np.random.normal(
                        loc=int(self.separation),
                        scale=int(self.separation/2)
                    ))
                time.sleep(time_separation/1000)
                self.current_time += time_separation
