import PySimpleGUI as sg
import time
import mido
import mido.backends.rtmidi
from mido import Message
from classes import settings
import threading
from classes.xilophone_handler import XilophoneHandler
import cv2
import os
import sys
import re
import json
import sys

toggle_btn_off = b'iVBORw0KGgoAAAANSUhEUgAAAGQAAAAoCAYAAAAIeF9DAAAPpElEQVRoge1b63MUVRY//Zo3eQHyMBEU5LVYpbxdKosQIbAqoFBraclatZ922Q9bW5b/gvpBa10+6K6WftFyxSpfaAmCEUIEFRTRAkQFFQkkJJghmcm8uqd763e6b+dOZyYJktoiskeb9OP2ne7zu+d3Hve2smvXLhqpKIpCmqaRruu1hmGsCoVCdxiGMc8wjNmapiUURalGm2tQeh3HSTuO802xWDxhmmaraZotpmkmC4UCWZZFxWKRHMcZVjMjAkQAEQqFmiORyJ+j0ei6UCgUNgyDz6uqym3Edi0KlC0227YBQN40zV2FQuHZbDa7O5fLOQBnOGCGBQTKNgzj9lgs9s9EIrE4EomQAOJaVf5IBYoHAKZpHs7lcn9rbm7+OAjGCy+8UHKsD9W3ruuRSCTyVCKR+Es8HlfC4bAPRF9fHx0/fpx+/PFH6unp4WOYJkbHtWApwhowYHVdp6qqKqqrq6Pp06fTvHnzqLq6mnWAa5qmLTYM48DevXuf7e/vf+Suu+7KVep3kIWsXbuW/7a0tDREo9Ed1dXVt8bjcbYK/MB3331HbW1t1N7eTgAIFoMfxSZTF3lU92sUMcplisJgxJbL5Sifz1N9fT01NjbSzTffXAKiaZpH+/v7169Zs+Yszr344oslFFbWQlpaWubGYrH3a2pqGmKxGCv74sWL9Pbbb1NnZyclEgmaNGmST13kUVsJ0h4wOB8EaixLkHIEKKAmAQx8BRhj+/btNHnyZNqwYQNNnDiR398wjFsTicSBDz74oPnOO+/8Gro1TbOyhWiaVh+Pxz+ura3FXwbj8OHDtHv3bgI448aNYyCg5Ouvv55mzJjBf2traykajXIf2WyWaQxWdOrUKTp//rww3V+N75GtRBaA4lkCA5NKpSiTydDq1atpyZIlfkvLstr7+/tvTyaT+MuAUhAQVVUjsVgMYABFVvzOnTvp888/Z34EIDgHjly6dCmfc3vBk4leFPd/jBwo3nHo559/pgMfHaATX59ApFZCb2NJKkVH5cARwAAUKBwDdOHChbRu3Tq/DegrnU4DlBxAwz3aQw895KpRUaCsp6urq9fDQUHxsIojR47QhAkTCNYCAO677z5acNttFI3FyCGHilaRUqk0myi2/nSaRwRMV9c1UhWFYrEozZo9mx3eyW9OMscGqexq3IJS7hlJOk+S3xTnvLyNB+L333/P4MycOVMYwGRN02pt234PwHFAJCxE1/Vl48aNO1hXV6fAEj777DPCteuuu44d9w033EDr16/3aQlKv3TpEv8tHS6exXiCvmpqaigWj5NCDqXT/bT9tdfoYnc39yWs5WqXcr6j0rHwK/I+KAy66u7upubmZlq8eLG47mQymeU9PT0fg95UD00lFAptSyQSHNrCgcM6xo8fz2DceOONtHnTJt4v2kXq7LxAHR0d7CvYccujRlNIwchX3WO06ejopM6ODrKsIgP0xy1bGGhhSRgZV7sELaNcRBnclzcwDt4dLAPdAhih+3A4/A8wEKyIAdE0bU0kEuGkDyaGaAo3YwMod999NyvZtCx20JlMf8lDkaK6ICgq8X/sRrxj1QUMwJw/D1BMvu8P99/PYTPCRAHI1Uxf5aLESvQ1FChQPPQKHQvRNG1pNBpdDf2rHl2hHMI3nD592g9tcdy8ppl03eCR3N3VxT5D5n9331U6/2XLUEv2Fe9vsWjRha5uKloWhUMGbdiwnjkVPkVEGWPNUoLnKJB/BdvACqBb6Bg5nbhmGMZWpnBVVWpDodDvw+EQO+H9+/fzDbhx9uzZTC2OU6Te3l5Wms/3AV9R8tCOe9FRSps4pJBdtCh56RKHyfX1DTRnzhx2dgAf/mQ0Iy9ky0jMFi1aVHL+k08+YWWAs4WibrnlFlq+fPmQ/bW2ttJPP/1EW7ZsGbLdiRMn2P/KdT74EfFbYAboGAn2rFlu4qjrGjCoVVVVawqFQiHDCHG0hNwBSKGjhYsWckf5XJ5yHBkJK3AtwPcVgq48y1A0lVRN8Y5Vv72GB1I1DgXzuRw5tsPZLHwJnJ5cdrnSbdq0afTAAw8MAgOybNkyVuqUKVN8yxxJJRa0i204wful0+lBVEwD1sA6hq77+lI8eBVFBQZNqqZpvxMZ97Fjxxg9HONhq6uq2IlnsjkXaU/xLlVppLHCNRck35m759FO0zyHrwpwNB8kvJjt2DS+bjxn/fAloMWRKGY4gWXI8X4luffee5kJ8LsjEQyakVArgEBbYRWyyNQFXUPnQoCFrmnafFwEICgUohEU1tDQQLbtlQXsImmqihyPFMWjI4bbIdUBFam8r5CbCJLi0pU79AjunRzVvU/1ruPFsOHhkO0fOnRoIFu9QtpasGCBv//DDz/Qu+++S2fOnOF3RMSIeh1yIggS3D179pQMhMcee4yTWVEWEgI9wfKEwDHv27dvUPUBx3DecjgvrguQ0Aa6xvMJqgQWuqqqMwXP4SHA4xCMWlGbwYh3exXde0onDwQSICnAhc+riuIn74yh15oR5HMqjyIEDPUN9cynIgS+0rxEKBuOc9u2bczXSG5h+QgiXn31VXrwwQc5t4KffOutt0pCb7QTpaCgUhEJyccoJUH5QfBEqUi0C1q+qBIjg5f6m6Fjlk84H/AekjgcV1VXk+Ol/6Cjih5ciOfkub2iuqA4A5Yi4GMsaaCtYxdpwvgJPh1cKWWBrjCSIaADhJg4J49YKB/hOwCBgnFdBuTRRx8d1O/JkyfZksSAhSBRxiYLAoXnn3/eD1AqvY+okCeTSd96VFWtASBVgtegFNFJyNDdhwTlqKXoO/6oH8BpiKDLvY5+yjSwHcdNOD0KG80kEX5KTBHIIxj7YAMhSNaG+12E5hiwsJyhBP0gIsXAFgOjkgidCwEWuhzNyOk+/Af8BUdRnqpLaojSUen5YSTQGC8gttFw6HIfsI5KRUxQspCuri6aOnXqkP1isCB6Gu4ZOSq9zLxKfj7dcZw+x3Gq0BG4U/wgRhfMXCR//s3Sv25hl52GDw1T0zAIKS5zMSUWbZsLkqMlGJ1QCCwD1dUDBw6UHf1w7hBEdwBEVsrjjz8+yKmDXuCL5HZw6shNhFMXDhu+J+hTyonQuRBgoXsrJqpwDlVesUIC3BaJRlh7hqaxB/B8OXk+2hvtiqi4+2gzpqoHkIi6PJ5TvAQRlFfwKOpCV9eoluORaM6dO5dp4+GHH+aKNWpvUBIsA5EVSkLkRWHBAieOca/s1EVkFHTyACno1L11CEM+o5hhRFAgRWCXdNu2TxWLxQaghYdEZIJ9/J00eTKRbZIaCZPDilcGrMJz0H6465kEY6EKvDwa5PkRhfy4S3HbF7MWJ4ciJA2+8C8RvBzmbwAIBGGqHKoGZceOHX6oLysa5wTlyRIsi4iioezsg/Mj5WhORLCYUZTuO606jnNMOFPkAzB37KNE4BRdSsEmlKX5SR6SQdU77yaFqtfGTQA1r6blZvAaZ/AaX1M4D7FdJ+7Y9O2335aMUnlJzS/ZEOm8+eabw8KJFR9ggmB4e7kSLL3L7yCfl6/h3aHrm266yffhtm0fV23b3i8mR+bPn8+NgBx4NZnsYZ7PZtxMHQBwJq55ZRKpNKJ5inYVrvrZO498v42bteNcNpsjx7G5DI0QFCNytOZG8Bznzp2j5557jvbu3TvoOsrfTzzxBE8vI+TFCB8pXVZSMlUAo9IcPJeP8nmuoQmxbbsVlNViWVbBsqwQHg4ZOhwjlHPkiy9oxR13kJ3P880iKWKK4mxcJHkeiSkDeYbrLRQ/ifTDAcWhXD5Hhby7EqZ1XyuHh6JaUO4lfomgLzwz1gOgYArnLSIfXMO7iOQPx0ePHuUAALOeGBTwIeWeBZNyTz75pF9shd8dDozgOYS6CJqga+l3gEELoiwsd3wvn89vxMOtXLmSXn75ZR6xKKXM6ezkim9vX68/Hy78uVISbXl+Y8C1uDgEEhVMUvVe6iWbHDrXfo6OHT/GeYBY8zVagJBUwkDfcp1M8dZLydVlgCCmIMjL1is9B/oT+YjwfZXAKAeMyGk2btzotykWi8Agyfxgmua/gBiQmzVrFq8iwTFuRljHcTXTWDfPaah+kVHMhahSAdGt6mr+vIjq+ReVR1R3dxf3hQryG2+84U+EyRYyWiJCdvSN3wA4YoKIZ+ekyE6uwoqp5XI0JqItWJhYxXk5YIhKMPIelG1owGqegc4ZENu2d+fz+cNi9m7Tpk0MiEASnGuaFs/2dXRcoGwmw5EUNkVUc0maPfRnEL3pTkXhEjumcTHraBaLXE/CbyBslOP2K3Xo/4tNVra8lQNA3jDgUUuDLjZv3iw780PZbHYP9K0hTvc6OKYoyp9CoZDCixJiMfrqq694FKATOF6Ej7AAHMMpozDII01xfUq5OQwoHY4bnIsySSFf4AVkyAvgs8DBQ43Iq0VGa5EDEk5MiUvW4eTz+ft7e3vP4roMSLvjOBN1XV8CM4TyoUxM6YIzAQJm2VA1TcQTbDHpVIp9S8Es8LFYHIb7+nr7qKu7i3r7+tgqIOfOtdMrr/yHHaMMxtW6eC44+iu1Ce4PBQYWyzU1NfnXsTo+lUr9G8EE1xI//PBDv0NVVaPxePwgFsqJFYrvvPMOT3lCeeBcOEdUSRcvXkS1NdJCOZIrjAOFeeyjxNzW9hFXTGF5oClBVWNlGRCNwkI5VAjuuecevw0WyqVSqd8mk8ks2vCMqQwIuWUDfykplAaFARAAA/qCtXhL7KmurpamT5tOU6ZiKalbagAUuWyOkj1JOtt+1l80IRxr0ImPFTCCUinPKLeUFMoGTWHqWAiWknqrFnkpqZi1HATIqlWrMFk0Nx6P82Jrsb4XieLrr7/O88CinO0MfP8wqGKrDHzk409Xim2sLiWly1hsDdoW0RSCJFFdRlvLss729/c3NzY2fo3gRi7Bl139joZtbW3LHcfZYds2f46AXGTr1q1MO8h+kaNAsZVWi/gZvLeUUvGmbRFJ4IHHsgR9RPBzBGzwwcgzsKpGBq9QKOBzhI0rVqw4Q16RUZaKH+w0Njae3b9//+22bT9lWZb/wQ6iA/wIoqYvv/ySK6siivLXp5aJtsYqNVUSAYao7MLHYmEIyvooQckTWZ4F4ZO2Z9Pp9CNNTU05+ZosZSkrKAcPHsQnbU/H4/ElYgX8/z9pG14kSj+UyWT+vnLlyoNBAF566aWS4xEBIuTTTz/Fcse/RqPRteFwOCy+ExHglFtuea2IHCJ7/qRgmubOfD7/jPfRpz+TOFQYPQiQoUQ4asMw8Fk0FtitCIVCv9F1nT+LVlW16hoFJOU4Tsq2bXwWfdyyrNZCodBSKBSScNgjXsBBRP8FGptkKVwR+ZoAAAAASUVORK5CYII=' # noqa:
toggle_btn_on = b'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' # noqa:
file_types = [("PNG (*.png)", "*.png")]


x_screen_size = 0
y_screen_size = 0


def video_tracker(midi_channels, demo, camera):
    classNames = { 15: 'person' }

    # Open video file or capture device.
    video = None
    if demo:
        video_demo = None
        if getattr(sys, 'frozen', False):
            video_demo = os.path.join(
                sys._MEIPASS,
                "images/video.mp4"
            )
        else:
            video_demo = "images/video.mp4"
        video = cv2.VideoCapture(video_demo)
    else:
        if sys.platform == 'win32':
            # fix for Windows
            video = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
        else:
            video = cv2.VideoCapture(camera)
        if camera == 1:
            video.set(3, 1280)
            video.set(4, 720)

    # Load the Caffe model
    net = None
    if getattr(sys, 'frozen', False):
        proto = os.path.join(
            sys._MEIPASS,
            "model/MobileNetSSD_deploy.prototxt"
        )
        caffe = os.path.join(
            sys._MEIPASS,
            "model/MobileNetSSD_deploy.caffemodel"
        )
        net = cv2.dnn.readNetFromCaffe(
            proto,
            caffe
        )
    else:
        net = cv2.dnn.readNetFromCaffe(
            "model/MobileNetSSD_deploy.prototxt",
            "model/MobileNetSSD_deploy.caffemodel"
        )
    
    read_every = 1000000 # adjust sample rate to avoid over CPU utilization
    if demo:
        read_every = 10000
    current_read = 0
    while True:
        # Read a new frame
        if current_read % read_every == 0:
            ok, frame = video.read()
            if not ok:
                break

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
            # fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

            # For get the class and location of object detected,
            # There is a fix index for class, location and confidence
            # value in @detections array .

            n_people = 0
            for i in range(detections.shape[2]):
                if i > 3:
                    break
                confidence = detections[0, 0, i, 2]  # Confidence of prediction
                if confidence > float(settings.params["THRESHOLD"] / 100):
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
                            (xLeftBottom + labelSize[0], yLeftBottom + baseLine), # noqa
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
                            (
                                int((xRightTop + xLeftBottom) / 2),
                                int((yRightTop + yLeftBottom) / 2)
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 0, 255)
                        )
                        coord = min(midi_channels - 1, n_people)
                        settings.coords[max(coord, 0)] = (
                            ((xRightTop + xLeftBottom) / 2),
                            ((yRightTop + yLeftBottom) / 2)
                        )
                        n_people += 1

            # Set the number of people in the frame
            settings.people_counter = min(n_people, 4)
            cv2.putText(
                frame,
                "Press ESC to exit",
                (100, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (50, 170, 50),
                2)
            cv2.putText(
                frame,
                "N of People : " + str(n_people),
                (100, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (50, 170, 50),
                2)
            cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) >= 0:  # Break with ESC
                break
        current_read += 1
    video.release()
    cv2.destroyWindow("frame")


loaded = False
if(os.path.exists("json_data_values.json") and
   os.path.exists("json_data_toggles.json")):
    with open('json_data_values.json') as json_file:
        loaded_data = json.load(json_file)
    with open('json_data_toggles.json') as json_file:
        loaded_toggles = json.load(json_file)
    loaded = True

xilos = []
for index in range(0, 4):
    row1 = [
        sg.Text("Channel"),
        sg.Combo(
            key=f"CHANNEL-{index}",
            values=[i for i in range(1, 17)],
            readonly=True,
            default_value=loaded_data[
                f"CHANNEL-{index}"
            ] if loaded else index + 1),
        sg.Text("Scale"),
        sg.Combo(
            key=f"SCALE-{index}",
            values=[
                "MAJOR",
                "DORIAN",
                "PHRYGIAN",
                "LYDIAN",
                "MIXOLYDIAN",
                "MINOR",
                "LOCRIAN",
                "CUSTOM"
            ],
            enable_events=True,
            readonly=True,
            default_value=loaded_data[
                f"SCALE-{index}"
            ] if loaded else "MINOR"
        ),
        sg.Text(
            "Intervals",
            key=f"INPUTSCALE-{index}-TEXT",
            visible=True if loaded and loaded_data[
                f"SCALE-{index}"
            ] == "CUSTOM" else False
        ),
        sg.InputText(
            loaded_data[
                f"INPUTSCALE-{index}"
            ] if loaded else "0,2,4,5,7,9,11",
            key=f"INPUTSCALE-{index}",
            visible=True if loaded and loaded_data[
                f"SCALE-{index}"
            ] == "CUSTOM" else False,
            size=12
        ),
        sg.Text("Root"),
        sg.Combo(
            key=f"ROOT-{index}",
            values=[i for i in range(1, 128)],
            readonly=True,
            default_value=loaded_data[
                f"ROOT-{index}"
            ] if loaded else 60
        ),
        sg.Text("Octaves"),
        sg.Combo(
            key=f"OCTAVES-{index}",
            values=[i for i in range(1, 11)],
            readonly=True,
            default_value=loaded_data[
                f"OCTAVES-{index}"
            ] if loaded else 2
        )
    ]
    row2 = [
        sg.Text("Duration"),
        sg.Slider(
            orientation="horizontal",
            key=f"DURATION-{index}",
            range=(1, 10000),
            default_value=loaded_data[
                f"DURATION-{index}"
            ] if loaded else 2000
        ),
        sg.Text("Separation"),
        sg.Slider(
            orientation="horizontal",
            key=f"SEPARATION-{index}",
            range=(1, 2500),
            default_value=loaded_data[
                f"SEPARATION-{index}"
            ] if loaded else 1500
        ),
        sg.Text("Compressed"),
        sg.Button(
            "",
            image_data=toggle_btn_on if (loaded and
                                        not loaded_toggles[
                                            index
                                        ]) else toggle_btn_off,
            key=f"TOGGLE-{index}-GRAPHIC",
            button_color=(
                sg.theme_background_color(),
                sg.theme_background_color()),
            border_width=0
        )
    ]
    row3 = [
        sg.Text('CC'),
        sg.Combo(
            key=f"CC-{index}",
            values=[i for i in range(128)],
            readonly=True,
            default_value=loaded_data[
                f"CC-{index}"
            ] if loaded else 21 + index
        ),
        sg.Text('min'),
        sg.Combo(
            key=f"MIN-{index}",
            values=[i for i in range(128)],
            readonly=True,
            default_value=loaded_data[
                f"MIN-{index}"
            ] if loaded else 0
        ),
        sg.Text('max'),
        sg.Combo(
            key=f"MAX-{index}",
            values=[i for i in range(128)],
            readonly=True,
            default_value=loaded_data[
                f"MAX-{index}"
            ] if loaded else 127
        ),
        sg.Text('Direction'),
        sg.Combo(
            key=f"DIRECTION-{index}",
            values=[
                "left to right",
                "right to left",
                "out to center"
            ],
            readonly=True,
            default_value=loaded_data[
                f"DIRECTION-{index}"
            ] if loaded else "left to right"
        ),
        sg.Button("Map", key=f"TRAIN-{index}"),
        sg.Text("", key=f"COUNTDOWN-{index}")
    ]
    instrument = sg.Frame(f"Instrument {index + 1}", [row1, row2, row3])
    xilos.append([instrument])

# ----- Full layout -----
layout = [
    [
        sg.Frame(
            "Settings",
            [[
                sg.Column(
                    [
                        [
                            sg.Text(
                                "Midi Output Port",
                            )
                        ],
                        [
                            sg.Combo(
                                key="OUTPUT",
                                values=list(set(mido.get_output_names())),
                                readonly=True,
                                enable_events=True,
                                default_value=loaded_data[
                                    "OUTPUT"
                                ] if loaded else ""
                            )
                        ]
                    ]
                ),
                sg.Column(
                    [
                        [
                            sg.Text(
                                "Video Threshold",
                            )
                        ],
                        [
                            sg.Slider(
                                orientation="horizontal",
                                key="THRESHOLD",
                                range=(1, 100),
                                default_value=loaded_data[
                                    "THRESHOLD"
                                ] if loaded else 20
                            )
                        ],
                    ]
                ),
                sg.Column(
                    [
                        [
                            sg.Combo(
                                key="DEMO",
                                values=[
                                    "Normal",
                                    "Demo (4 people)"
                                ],
                                readonly=True,
                                default_value=loaded_data[
                                    "DEMO"
                                ] if loaded else "Demo (4 people)",
                            )
                        ],
                        [
                            sg.Text(
                                "Camera (ignored on Demo)",
                            )
                        ],
                        [
                            sg.Combo(
                                key="CAMERA",
                                values=[
                                    "0",
                                    "1"
                                ],
                                readonly=True,
                                default_value=loaded_data[
                                    "CAMERA"
                                ] if loaded else "0"
                            )
                        ]
                    ]
                )
            ],
            [
                sg.FileBrowse(
                    "Browse Image",
                    key="IMAGE",
                    file_types=file_types),
                sg.Text("", key="IMAGE-PATH")
            ]]
        ),
        sg.Button("Start", key="START"),
        xilos
    ]
]
# Create the window
window = sg.Window("Image to MIDI", layout)

port = None
if loaded:
    port = mido.open_output(loaded_data["OUTPUT"])
# Create an event loop
graphic_off = loaded_toggles if loaded else [True for i in range(4)]
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "OUTPUT":
        port = mido.open_output(values["OUTPUT"])
    if "TOGGLE-" in event:
        index = int(str(event).split('-')[1])
        graphic_off[index] = not graphic_off[index]
        window[event].update(
            image_data=toggle_btn_off if graphic_off[index] else toggle_btn_on
        )
    if "SCALE" in event:
        index = str(event).split('-')[1]
        if values[f"SCALE-{index}"] == "CUSTOM":
            window[f"INPUTSCALE-{index}-TEXT"].update(visible=True)
            window[f"INPUTSCALE-{index}"].update(visible=True)
        else:
            window[f"INPUTSCALE-{index}-TEXT"].update(visible=False)
            window[f"INPUTSCALE-{index}"].update(visible=False)
        window.refresh()
    if "TRAIN" in event:
        index = str(event).split('-')[1]
        if port is None:
            sg.popup_error("Select MIDI Output Port")
        else:
            count = 5
            while count > 0:
                window[f"COUNTDOWN-{index}"].update(str(count))
                window.refresh()
                count -= 1
                time.sleep(1)
            window[f"COUNTDOWN-{index}"].update("")
            window.refresh()
            # send midi CC
            msg = Message(
                'control_change',
                channel=int(values[f"CHANNEL-{index}"]) - 1,
                control=values[f"CC-{index}"],
                value=127
            )
            port.send(msg)
    if event == "START":
        if(port is None or
           values["IMAGE"] is None):
            sg.popup_error("Select MIDI Output Port and Image")
        else:
            if(not os.path.exists(values["IMAGE"]) or
               not values["IMAGE"].endswith('.png')):
                sg.popup_error("Select a valid png Image")
            else:
                valid_min_max = True
                for i in range(4):
                    if values[f"MAX-{i}"] <= values[f"MIN-{i}"]:
                        valid_min_max = False
                        break
                valid_notes = True
                for i in range(4):
                    if(127 <=
                       values[f"ROOT-{i}"] + 12 * values[f"OCTAVES-{i}"]):
                        valid_notes = False
                        break
                valid_intervals = True
                for i in range(4):
                    if(not bool(re.match("^\d+(,\d+)*$", values[f"INPUTSCALE-{i}"])) and values[f"SCALE-{i}"] == "CUSTOM"):
                        valid_intervals = False
                        break
                if not valid_min_max:
                    sg.popup_error(f"MAX has to be greater \
                        than MIN on instrument {i}")
                elif not valid_notes:
                    sg.popup_error(f"The number of octaves from \
the selected root note exceed the maximum \
number of midi notes (127). Try reducing \
the Root note or the number of octaves \
for instrument {i}")
                elif not valid_intervals:
                    sg.popup_error(f"Intervals should be in the \
form [digit1],[digit2],[digit3] \
for example '0,2,4,5,7,9,11' on instrument {i}")
                else:
                    test_video = None
                    if values["DEMO"] == "Demo (4 people)":
                        video_demo = None
                        if getattr(sys, 'frozen', False):
                            video_demo = os.path.join(
                                sys._MEIPASS,
                                "images/video.mp4"
                            )
                        else:
                            video_demo = "images/video.mp4"
                        test_video = cv2.VideoCapture(video_demo)
                    else:
                        if sys.platform == 'win32':
                            # fix for Windows
                            test_video = cv2.VideoCapture(int(values["CAMERA"]), cv2.CAP_DSHOW)
                        else:
                            test_video = cv2.VideoCapture(int(values["CAMERA"]))
                        if(int(values["CAMERA"]) == 1):
                            test_video.set(3, 1280)
                            test_video.set(4, 720)
                    ok, frame = test_video.read()
                    y_screen_size = len(frame)
                    x_screen_size = len(frame[0])
                    test_video.release()
                    settings.init(
                        values,
                        graphic_off,
                        x_screen_size,
                        y_screen_size
                    )
                    xilo_handler = XilophoneHandler(
                        values["IMAGE"],
                        4,
                        port
                    )
                    xilo_handler_thread = threading.Thread(
                        target=xilo_handler.xilo_lifecycle, daemon=False
                    )
                    # save values
                    with open('json_data_values.json', 'w') as outfile:
                        json.dump(values, outfile)
                    with open('json_data_toggles.json', 'w') as outfile:
                        json.dump(graphic_off, outfile)
                    xilo_handler_thread.start()
                    # start video
                    video_tracker(4, values["DEMO"] == "Demo (4 people)", int(values["CAMERA"]))
                    settings.keep_playing = False
                    xilo_handler_thread.join()
                    port.panic()

window.close()
