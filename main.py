import argparse
from classes.xilophone import XilophoneHandler
import cv2
import threading
from classes import settings


parser = argparse.ArgumentParser()
parser.add_argument(
    "--image-path",
    help="path to the image to be processed",
    required=True,
)
parser.add_argument(
    "--video",
    help="path to video file. If empty, camera's stream will be used"
)
parser.add_argument(
    "--prototxt",
    default="MobileNetSSD_deploy.prototxt",
    help='Path to text network file: \
        MobileNetSSD_deploy.prototxt for Caffe model or '
)
parser.add_argument(
    "--weights",
    default="MobileNetSSD_deploy.caffemodel",
    help='Path to weights: \
        MobileNetSSD_deploy.caffemodel for Caffe model or '
    )
parser.add_argument(
    "--thr",
    default=0.2,
    type=float,
    help="confidence threshold to filter out weak detections")
parser.add_argument(
    "--max-channels",
    default=5,
    help="max number of midi channles"
)


def video_tracker(midi_channels):
    classNames = {15: 'person'}

    # Open video file or capture device.
    if args.video:
        video = cv2.VideoCapture(args.video)
    else:
        video = cv2.VideoCapture(0)
    video = cv2.VideoCapture('../../Downloads/My Name Is - D Billions Kids Songs.mp4')

    # Load the Caffe model
    net = cv2.dnn.readNetFromCaffe(args.prototxt, args.weights)

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # resize frame for prediction
        frame_resized = cv2.resize(frame, (300, 300))

        # MobileNet requires fixed dimensions for input image(s)
        # so we have to ensure that it is resized to 300x300 pixels.
        # set a scale factor to image because network the objects
        # has differents size.
        # We perform a mean subtraction (127.5, 127.5, 127.5)
        # to normalize the input;
        # after executing this command our "blob" now has the shape:
        # (1, 3, 300, 300)
        blob = cv2.dnn.blobFromImage(
            frame_resized,
            0.007843,
            (300, 300),
            (127.5, 127.5, 127.5),
            False
        )
        # Set to network the input blob
        net.setInput(blob)
        # Prediction of network
        detections = net.forward()

        # Size of frame resize (300x300)
        cols = frame_resized.shape[1]
        rows = frame_resized.shape[0]
        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        # For get the class and location of object detected,
        # There is a fix index for class, location and confidence
        # value in @detections array .

        n_people = 0
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]  # C onfidence of prediction
            if confidence > args.thr:  # Filter prediction
                class_id = int(detections[0, 0, i, 1])  # Class label
                # Draw label and confidence of prediction in frame resized
                if class_id in classNames:

                    # Object location
                    xLeftBottom = int(detections[0, 0, i, 3] * cols)
                    yLeftBottom = int(detections[0, 0, i, 4] * rows)
                    xRightTop = int(detections[0, 0, i, 5] * cols)
                    yRightTop = int(detections[0, 0, i, 6] * rows)

                    # Factor for scale to original size of frame
                    heightFactor = frame.shape[0]/300.0
                    widthFactor = frame.shape[1]/300.0
                    # Scale object detection to frame
                    xLeftBottom = int(widthFactor * xLeftBottom)
                    yLeftBottom = int(heightFactor * yLeftBottom)
                    xRightTop = int(widthFactor * xRightTop)
                    yRightTop = int(heightFactor * yRightTop)
                    # Draw location of object
                    cv2.rectangle(
                        frame,
                        (xLeftBottom, yLeftBottom),
                        (xRightTop, yRightTop),
                        (0, 255, 0)
                    )

                    label = classNames[class_id] + ": " + str(confidence)
                    labelSize, baseLine = cv2.getTextSize(
                        label,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        1
                    )

                    yLeftBottom = max(yLeftBottom, labelSize[1])
                    cv2.rectangle(
                        frame,
                        (xLeftBottom, yLeftBottom - labelSize[1]),
                        (xLeftBottom + labelSize[0], yLeftBottom + baseLine),
                        (255, 255, 255),
                        cv2.FILLED
                    )
                    cv2.putText(
                        frame,
                        label,
                        (xLeftBottom, yLeftBottom),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0)
                    )
                    cv2.putText(
                        frame,
                        "C",
                        (int((xRightTop + xLeftBottom) / 2), int((yRightTop + yLeftBottom) / 2)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0,0,255)
                    )
                    # print(label)  # print class and confidence
                    coord = min(midi_channels - 1, n_people)
                    print(coord)
                    settings.coords[max(coord, 0)] = ((xRightTop + xLeftBottom) / 2), ((yRightTop + yLeftBottom) / 2)
                    n_people += 1
                    # len(frame) = 720
                    # len(frame[0]) = 1280

        # Set the number of people in the frame
        settings.people_counter = n_people
        cv2.putText(
            frame,
            "N of People : " + str(n_people),
            (100, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2)
        # Display FPS on frame
        cv2.putText(
            frame,
            "FPS : " + str(int(fps)),
            (100, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (50, 170, 50),
            2)
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) >= 0:  # Break with ESC
            break
    video.release()
    cv2.destroyWindow("preview")


def main(conf):
    # high pitch, poly, fast short notes
    try:
        settings.init(int(conf["max_channels"]))
        xilo_handler = XilophoneHandler(
            conf['image_path'],
            int(conf["max_channels"]),
            "PHRYGIAN"
        )
        xilo_handler_thread = threading.Thread(target=xilo_handler.xilo_lifecycle, daemon = True)
        xilo_handler_thread.start()
        # start video
        video_tracker(int(conf["max_channels"]))
        settings.keep_playing = False
    except(KeyboardInterrupt):
        settings.keep_playing = False


if __name__ == "__main__":
    args = parser.parse_args()
    arg_dic = dict(vars(args))
    main(arg_dic)
