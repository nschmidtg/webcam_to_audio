import argparse
from classes.xilophone import Xilophone
import numpy as np
import cv2
import threading
from classes import settings


parser = argparse.ArgumentParser()
parser.add_argument(
    "--image_path",
    help="path to the image to be processed",
    required=True,
)


def global_var():
    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)
    if vc.isOpened():  # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False
    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        settings.speed_corrector = np.average(frame)
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

    vc.release()
    cv2.destroyWindow("preview")


def main_xilo(conf):
    # high pitch, poly, fast short notes
    xilo1 = Xilophone(
        0,
        arg_dic['image_path'],
        'MAJOR',
        60,
        2,
        note_length=500,
        separation=300
    )
    xilo1_thread = threading.Thread(target=xilo1.start)
    xilo1_thread.start()

    # long compressed mono bass notes
    xilo2 = Xilophone(
        1,
        arg_dic['image_path'],
        'MAJOR',
        36,
        1,
        compressed=True,
        note_length=2000
    )
    xilo2_thread = threading.Thread(target=xilo2.start)
    xilo2_thread.start()

    # start video
    global_var()
    settings.keep_playing = False


if __name__ == "__main__":
    args = parser.parse_args()
    arg_dic = dict(vars(args))
    main_xilo(arg_dic)
