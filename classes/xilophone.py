from .image_analyzer import ImageAnalizer
from PIL import Image
import mido
from mido import Message
import threading
import numpy as np
import time
from . import settings


MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 11]


class Xilophone():
    def __init__(self, midi_channel, image_path, scale, root_note, n_scales):
        settings.init()
        self.midi_channel = midi_channel
        selected_scale = eval(scale)
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

        self.outport = mido.open_output()

    def send_note(self, note, duration, vel):
        msg = Message(
            'note_on',
            note=note,
            velocity=vel,
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

    def start(self):
        while(True):
            print(self.midi_channel, settings.speed_corrector)
            note_vel = np.random.choice(self.notes_matrix, p=self.norm_probs)
            pitch, volume = note_vel.split('-')
            pitch = int(self.notes[int(pitch)])
            volume = int(volume)
            time_sampled = max(0, np.random.normal(
                loc=int(2000),
                scale=500
            ))
            play_note = threading.Thread(
                target=self.send_note,
                args=(pitch, time_sampled, volume)
            )
            play_note.start()
            time_sampled = max(0, np.random.normal(
                loc=int(250),
                scale=250
            ))
            time.sleep(time_sampled/1000)
            self.current_time += time_sampled
