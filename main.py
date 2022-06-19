import argparse
from classes.xilophone import Xilophone
import cv2
import threading
from classes import settings
import sys


parser = argparse.ArgumentParser()
parser.add_argument(
    "--image_path",
    help="path to the image to be processed",
    required=True,
)


def global_var():
    # cv2.namedWindow("preview")
    # vc = cv2.VideoCapture(0)
    # if vc.isOpened():  # try to get the first frame
    #     rval, frame = vc.read()
    # else:
    #     rval = False
    # while rval:
    #     cv2.imshow("preview", frame)
    #     rval, frame = vc.read()
    #     settings.speed_corrector = np.average(frame)
    #     key = cv2.waitKey(20)
    #     if key == 27:  # exit on ESC
    #         break
    tracker_type = 'TrackerMIL_create'

    tracker = cv2.TrackerMIL_create()

    # Read video
    # video = cv2.VideoCapture("input.mp4")
    video = cv2.VideoCapture(0)  # for using CAM

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()

    # Define an initial bounding box
    bbox = (287, 23, 86, 320)

    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            settings.x, settings.y = p1
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
        else:
            # Tracking failure
            cv2.putText(
                frame,
                "Tracking failure detected",
                (100, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 0, 255),
                2)

        # Display tracker type on frame
        cv2.putText(
            frame,
            tracker_type + " Tracker",
            (100, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2
        )

        # Display FPS on frame
        cv2.putText(
            frame,
            "FPS : " + str(int(fps)),
            (100, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2)
        # Display result
        cv2.imshow("Tracking", frame)

        # Exit if ESC pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press q button bar
            break
    video.release()
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
