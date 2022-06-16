import argparse
from classes.spectral_analyzer import SpectralAnalizer
from classes.image_analyzer import ImageAnalizer
import torch
import torchaudio
from PIL import Image
import pdb
import numpy as np
from midiutil import MIDIFile

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

def main_xilo(conf):
    torchaudio.set_audio_backend(backend='soundfile')
    image_path = conf['image_path']

    notes = [38,40,42,43,45,47,49,50,62,64,66,67,69,71,73,74,76,78,79,81,83,85,86] 
    track    = 0
    channel  = 0
    current_time     = 1   # In beats
    tempo    = 880  # In BPM
    quarter_length = int(1000/(tempo/60))
    n_notes = len(notes)
    image_a = ImageAnalizer()
    im = image_a.open(image_path)
    image = Image.Image.split(im)
    # pdb.set_trace()
    R = np.array(image[0])
    G = np.array(image[1])
    B = np.array(image[2])
    Grey = 0.299 * R + 0.587 * G + 0.114 * B
    W, H = Grey.shape
    #Grey=np.ones((H,W))
    delta_x = int(W/n_notes)
    delta_y = int(H/128)  # when using 2 synth
    # delta_vel = int(H/128)

    prob_matrix = np.zeros(n_notes * 128)
    notes_matrix = [None] * (n_notes * 128)
    col_count = 0
    row_count = 0

    current = 0
    for col_count in range(0, n_notes):
        for row_count in range(0, 128):
            notes_matrix[current] = "%s-%s" % (col_count, row_count)
            prob_matrix[current] = np.sum(Grey[col_count * delta_x :(col_count + 1) * delta_x, row_count * delta_y :(row_count + 1) * delta_y])
            current += 1

    max_value = np.sum(prob_matrix)
    norm_probs = prob_matrix / max_value

    
    MyMIDI = MIDIFile(1, eventtime_is_ticks=False) # One track, defaults to format 1 (tempo track
                        # automatically created)
    MyMIDI.addTempo(track, current_time, tempo)

    for i in range(1000):
        # pdb.set_trace()
        note_vel = np.random.choice(notes_matrix, p=norm_probs)
        pitch, volume = note_vel.split('-')
        pitch = notes[int(pitch)]
        volume = int(volume)
        time_sampled = max(quarter_length, int(np.random.normal(loc=quarter_length, scale=500)))
        # pdb.set_trace()
        duration = 16
        time_q = ms_to_quarters(time_sampled, quarter_length)
        
        MyMIDI.addNote(track, channel, pitch, current_time, 64, volume)
        current_time = current_time + time_q

    with open("major-scale.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)

def ms_to_quarters(onset, quarter_length):
    return int(onset/quarter_length)


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
    #main(arg_dic)
    main_xilo(arg_dic)
