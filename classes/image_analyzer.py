from PIL import Image, ImageOps
import numpy as np
import math


class ImageAnalizer():
    def __landscapify__(self, image):
        """
        return a rotated image to fit landscape format
        """
        width, height = image.size
        print(width, height)
        if height > width:
            image = image.rotate(90, expand=True)
        image = ImageOps.flip(image)
        return image

    def open(self, path):
        return Image.open(path)

    def get_frames_and_bins(self, image):
        """
        returns the frames and bins of a landscapifyed image as
        it were a spectrogram
        """
        image = self.__landscapify__(image)
        width, height = image.size

        # return the highest closest power of 2 + 1
        n_bins = int(2**math.ceil(math.log(height, 2))) + 1
        n_frames = width

        image = image.resize((n_frames, n_bins))

        return image, n_frames, n_bins

    def colors_to_db(self, channel, max_db):
        # 0..255 -> -60..0
        channel = channel / max_db
        channel = channel ** 7
        channel = channel * 120 - 120

        return channel

    def split_channels(self, image):
        image = Image.Image.split(image)
        R = np.array(image[0])
        G = np.array(image[1])
        B = np.array(image[2])
        Grey = 0.299 * R + 0.587 * G + 0.114 * B

        max_db = np.max([R, G, B, Grey])
        R = self.colors_to_db(R, max_db).T
        G = self.colors_to_db(G, max_db).T
        B = self.colors_to_db(B, max_db).T
        Grey = self.colors_to_db(Grey, max_db)

        return (R, G, B, Grey)
