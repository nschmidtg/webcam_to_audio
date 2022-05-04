import argparse
from classes.spectral_analyzer import SpectralAnalizer
from classes.image_analyzer import ImageAnalizer
import torch
import torchaudio

parser = argparse.ArgumentParser()
parser.add_argument(
    "--image_path",
    help="path to the image to be processed",
    required=True,
)
parser.add_argument(
    "--sample_rate",
    default=16000,
    help="sample rate of the output audio",
    required=False,
    type=int
)
parser.add_argument(
    "--hop_size",
    default=512,
    help="hop size to synthetized audio. The higher, the longer",
    required=False,
    type=int
)
parser.add_argument(
    "--out_name",
    default='output.wav',
    help="file name of the synthetized output audio",
    required=False,
)


def main(conf):
    torchaudio.set_audio_backend(backend='soundfile')
    image_path = conf['image_path']
    sample_rate = conf['sample_rate']
    hop_size = conf['hop_size']
    out_name = conf['out_name']

    image_a = ImageAnalizer()
    im = image_a.open(image_path)
    im, n_frames, n_bins = image_a.get_frames_and_bins(im)
    R, G, B, Grey = image_a.split_channels(im)

    spectral_a = SpectralAnalizer(n_frames, n_bins, hop_size, sample_rate)
    spectral_a.plot_spectrogram(Grey)

    # analyze the sources
    R = spectral_a.stftSynth(R, R)
    G = spectral_a.stftSynth(G, G)
    B = spectral_a.stftSynth(B, B)
    Grey = spectral_a.stftSynth(Grey, Grey)

    # mix the sources (stereo)
    # x = np.array([Grey - R/4, Grey - B])
    x = Grey.to(torch.float32)
    max_value = torch.max(torch.abs(x))
    x /= max_value

    # save audio
    torchaudio.save(out_name, x, sample_rate=sample_rate)


if __name__ == "__main__":
    args = parser.parse_args()
    arg_dic = dict(vars(args))
    main(arg_dic)
