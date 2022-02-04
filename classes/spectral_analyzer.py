import numpy as np
import matplotlib.pyplot as plt
import torch


class SpectralAnalizer():
    def __init__(self, stft_size, window_size, hop_size, sample_rate) -> None:
        self.stft_size = stft_size
        self.window_size = window_size
        self.hop_size = hop_size
        self.sample_rate = sample_rate

    def stftSynth(self, mY, pY):
        mY = torch.from_numpy(mY)
        pY = torch.from_numpy(pY)
        polar = mY * torch.cos(pY) + mY * torch.sin(pY) * 1j
        out = torch.istft(
            polar,
            (mY.shape[0] - 1) * 2,
            hop_length=self.hop_size,
            win_length=(mY.shape[0] - 1) * 1,
            window=torch.hamming_window((mY.shape[0] - 1) * 1),
            return_complex=False,
            onesided=True,
            center=True,
            normalized=False)
        return out.unsqueeze(0)

    def plot_spectrogram(self, xmX):
        plt.figure(1, figsize=(15, 10))
        plt.subplot(211)
        numFrames = int(xmX[:, 0].size)

        frmTime = self.hop_size * np.arange(numFrames) / self.sample_rate
        binFreq = np.arange(self.stft_size) * \
            float(self.sample_rate) / self.stft_size / 2
        plt.pcolormesh(frmTime, binFreq, np.transpose(xmX))
        plt.title(
            'xmX, M=' + str(self.window_size) +
            ', N=' + str(self.stft_size) + ', H=' + str(self.hop_size)
        )
        plt.autoscale(tight=True)
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (s)')
        plt.tight_layout()
        plt.savefig('spectrogram.png')
