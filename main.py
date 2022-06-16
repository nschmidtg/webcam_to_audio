import argparse
from classes.image_analyzer import ImageAnalizer
from PIL import Image
import numpy as np
import mido
from mido import Message
import cv2
import threading
import time


speed_corrector = 0

parser = argparse.ArgumentParser()
parser.add_argument(
    "--image_path",
    help="path to the image to be processed",
    required=True,
)


def send_note(outport, note, duration, vel):
    msg = Message('note_on', note=note, velocity=vel)
    outport.send(msg)
    time.sleep(duration/1000)
    msg = Message('note_off', note=note)
    outport.send(msg)


def global_var():
    global speed_corrector
    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)

    if vc.isOpened():  # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False

    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        speed_corrector = np.average(frame)
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

    vc.release()
    cv2.destroyWindow("preview")


def main_xilo(conf):
    image_path = conf['image_path']

    notes = [
        38,
        40,
        42,
        43,
        45,
        47,
        49,
        50,
        62,
        64,
        66,
        67,
        69,
        71,
        73,
        74,
        76,
        78,
        79,
        81,
        83,
        85,
        86
    ]
    current_time = 1   # In beats
    n_notes = len(notes)
    image_a = ImageAnalizer()
    im = image_a.open(image_path)
    image = Image.Image.split(im)
    R = np.array(image[0])
    G = np.array(image[1])
    B = np.array(image[2])
    Grey = 0.299 * R + 0.587 * G + 0.114 * B
    W, H = Grey.shape
    delta_x = int(W/n_notes)
    delta_y = int(H/128)  # when using 2 synth

    prob_matrix = np.zeros(n_notes * 128)
    notes_matrix = [None] * (n_notes * 128)
    col_count = 0
    row_count = 0

    current = 0
    for col_count in range(0, n_notes):
        for row_count in range(0, 128):
            notes_matrix[current] = "%s-%s" % (col_count, row_count)
            prob_matrix[current] = np.sum(Grey[
                col_count * delta_x:(col_count + 1) * delta_x,
                row_count * delta_y:(row_count + 1) * delta_y
            ])
            current += 1

    max_value = np.sum(prob_matrix)
    norm_probs = prob_matrix / max_value

    outport = mido.open_output()

    y = threading.Thread(target=global_var)
    y.start()

    while(True):
        note_vel = np.random.choice(notes_matrix, p=norm_probs)
        pitch, volume = note_vel.split('-')
        pitch = int(notes[int(pitch)] + ((speed_corrector/255)*2-1)*0)
        volume = int(volume)
        time_sampled = max(0, np.random.normal(
            loc=int(2000+1000*((speed_corrector/255)*2-1)),
            scale=500
        ))
        x = threading.Thread(
            target=send_note,
            args=(outport, pitch, time_sampled, volume)
        )
        x.start()
        time_sampled = max(0, np.random.normal(
            loc=int(500+250*((speed_corrector/255)*2-1)),
            scale=250
        ))
        time.sleep(time_sampled/1000)
        current_time = current_time + time_sampled


if __name__ == "__main__":
    args = parser.parse_args()
    arg_dic = dict(vars(args))
    main_xilo(arg_dic)
