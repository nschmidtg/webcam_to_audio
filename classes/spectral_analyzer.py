import math
import numpy as np
from scipy.fftpack import ifft
import matplotlib.pyplot as plt

class SpectralAnalizer():
    def __init__(self, stft_size, window_size, hop_size, sample_rate) -> None:
        self.stft_size = stft_size
        self.window_size = window_size
        self.hop_size = hop_size
        self.sample_rate = sample_rate
    
    def dftSynth(self, mX, pX):
        """
        from https://github.com/MTG/sms-tools
        Synthesis of a signal using the discrete Fourier transform
        mX: magnitude spectrum, pX: phase spectrum
        returns y: output signal
        """
        hN = mX.size                                            # size of positive spectrum, it includes sample 0
        N = (hN-1)*2                                            # FFT size
        if not(((N & (N - 1)) == 0) and N > 0):                 # raise error if N not a power of two, thus mX is wrong
            raise ValueError("size of mX is not (N/2)+1")

        hM1 = int(math.floor((self.window_size+1)/2))           # half analysis window size by rounding
        hM2 = int(math.floor(self.window_size/2))               # half analysis window size by floor
        fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
        y = np.zeros(self.window_size)                          # initialize output array
        Y = np.zeros(N, dtype = complex)                        # clean output spectrum
        Y[:hN] = 10**(mX/20) * np.exp(1j*pX)                    # generate positive frequencies
        Y[hN:] = 10**(mX[-2:0:-1]/20) * np.exp(-1j*pX[-2:0:-1]) # generate negative frequencies
        fftbuffer = np.real(ifft(Y))                            # compute inverse FFT
        y[:hM2] = fftbuffer[-hM2:]                              # undo zero-phase window
        y[hM2:] = fftbuffer[:hM1]
        return y

    def stftSynth(self, mY, pY) :
        """
        from https://github.com/MTG/sms-tools
        Synthesis of a sound using the short-time Fourier transform
        mY: magnitude spectra, pY: phase spectra
        returns y: output sound
        """
        hM1 = (self.window_size+1)//2                    # half analysis window size by rounding
        hM2 = self.window_size//2                        # half analysis window size by floor
        nFrames = mY[:,0].size                           # number of frames
        y = np.zeros(nFrames*self.hop_size + hM1 + hM2)  # initialize output array
        pin = hM1                  
        for i in range(nFrames):                         # iterate over all frames      
            y1 = self.dftSynth(mY[i,:], pY[i,:])         # compute idft
            y[pin-hM1:pin+hM2] += self.hop_size*y1       # overlap-add to generate output sound
            pin += self.hop_size                         # advance sound pointer
        y = np.delete(y, range(hM2))                     # delete half of first window which was added in stftAnal
        y = np.delete(y, range(y.size-hM1, y.size))      # delete the end of the sound that was added in stftAnal
        return y

    def plot_spectrogram(self, xmX):
        """
        part of the code is from sms-tools/lectures/04-STFT/plots-code/spectrogram.py.
        Plots a spectrogram given the magnitude spectrogram representation
        """
        plt.figure(1, figsize=(15, 10))
        plt.subplot(211)
        numFrames = int(xmX[:,0].size)
        frmTime = self.hop_size * np.arange(numFrames) / self.sample_rate
        binFreq = np.arange(self.stft_size + 1)*float(self.sample_rate) / self.stft_size / 2
        plt.pcolormesh(frmTime, binFreq, np.transpose(xmX))
        plt.title('xmX, M=' + str(self.window_size) + ', N=' + str(self.stft_size) + ', H=' + str(self.hop_size))
        plt.autoscale(tight=True)
        plt.ylabel('Frequency (Hz)')
        plt.xlabel('Time (s)')
        plt.tight_layout()
        plt.show()