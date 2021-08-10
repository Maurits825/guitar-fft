import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import scipy.io.wavfile
import peakutils
from peakutils.plot import plot as pplot
from scipy import signal
import music_theory as mt

# The lowest and highest Hz that can be played on 24 fret guitar in standard tunning
GUITAR_LOW_HZ_CUTOFF = 70
GUITAR_HIGH_HZ_CUTOFF = 1500
GUITAR_MIN_HZ = 20  # you cant play two notes 20hz apart on guitar at same time


class GuitarFFT:
    def __init__(self):
        self.raw_wav = None
        self.filtered_wav = None
        self.sampling_rate = 0
        self.frequencies = None
        self.normal_spec = None
        self.peak_indexes = None
        self.peak_frequencies = None
        self.music_theory = mt.MusicTheory()

    def calc_fft(self, data, rate, n, noise=None):
        data = data * np.hamming(data.size)
        time_step = 1. / rate

        sp = np.fft.rfft(data, n)
        freq = np.fft.rfftfreq(n, time_step)

        if noise:
            sp_corrected = (np.abs(sp) / (n * 2)) - noise
        else:
            sp_corrected = np.abs(sp) / (n * 2)

        max_sp = sp_corrected.max()
        if max_sp != 0:
            sp_normalized = sp_corrected / sp_corrected.max()
        else:
            sp_normalized = sp_corrected

        #ret_sp = self.window_smooth(sp_normalized, 6)
        ret_sp = sp_normalized

        return freq, ret_sp

    def load_file(self, file_name):
        rate, wav_data = scipy.io.wavfile.read(file_name)
        if wav_data.shape[1] > 1:
            wav_data = wav_data[:, 0]

        return rate, wav_data

    def record_audio(self, length):
        fs = 44100 #TODO
        duration = length
        wav_data = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()

        if wav_data.shape[1] > 1:
            wav_data = wav_data[:, 0]
        return fs, wav_data

    def filter_wav(self, data, rate, wn, filter_type):
        sos = signal.butter(10, wn, filter_type, fs=rate, output='sos')
        return signal.sosfilt(sos, data)

    def window_smooth(self, data, window_size):
        n = data.size
        padded_data = np.zeros(n + window_size)
        half_window_size = int(window_size/2)
        padded_data[half_window_size:n+half_window_size] = data
        ret_arr = np.zeros(n)

        for i in range(n - half_window_size):
            ret_arr[i] = np.average(padded_data[i:i+window_size])

        return ret_arr

    def get_peaks(self, freq, spec, thres, min_dist):
        peak_indexes = peakutils.indexes(spec, thres=thres, min_dist=min_dist, thres_abs=True)
        return freq[peak_indexes], peak_indexes

    def plot_data(self, data, freq, spec, peak_idx):
        plt.subplot(1, 2, 1)
        plt.plot(data)
        plt.subplot(1, 2, 2)
        pplot(freq, spec, peak_idx)
        plt.xlim(-10, 1500)
        plt.show()

    #TODO what does this do
    def peaks_passes(self, raw_data, rate, frequencies, spec):
        n = raw_data.size
        f_passes = np.array([150, 400, 2000])
        min_dist_passes = np.rint((np.array([20, 25, 30]) / (rate / 2)) * n)
        indexes = np.rint((f_passes / (rate / 2)) * n)

        start_i = 80
        freq_peaks = np.array([])
        indexes_peaks = np.array([], dtype=int)
        iteration = 0
        for i in indexes:
            f_peaks, id_peaks = self.get_peaks(frequencies, spec[start_i:int(i)], 0.00001, min_dist_passes[iteration])
            freq_peaks = np.concatenate([freq_peaks, f_peaks])
            indexes_peaks = np.concatenate([indexes_peaks, id_peaks])
            start_i = int(i)
            iteration += 1

        freq_peaks = np.asarray(freq_peaks)

    def get_data_from_recording(self, noise, length):
        noise_spec = None
        if noise:
            print('Recording noise...')
            noise_rate, noise_raw_data = self.record_audio(length)
            _, noise_spec = self.calc_fft(noise_raw_data, noise_rate, noise_raw_data.size)

        print('Recording audio...')
        rate, raw_data = self.record_audio(length)
        print('Recording done!')

        return raw_data, rate, noise_spec

    def get_data_from_file(self, file, noise_file=None):
        noise_spec = None
        rate, raw_data = self.load_file(file)
        if noise_file:
                noise_rate, noise_raw_data = self.load_file(noise_file)
                _, noise_spec = self.calc_fft(noise_raw_data, noise_rate, noise_raw_data.size)

        return raw_data, rate, noise_spec

    def operate(self, raw_data, rate, noise_spec):
        n = raw_data.size

        filtered_data = self.filter_wav(raw_data, rate, (GUITAR_LOW_HZ_CUTOFF, GUITAR_HIGH_HZ_CUTOFF), 'bandpass')
        frequencies, spec = self.calc_fft(filtered_data, rate, n, noise_spec)

        idx_min_dist = (GUITAR_MIN_HZ / (rate / 2)) * (n / 2)
        # TODO threshold value
        threshold = 0.06
        f_peaks, id_peaks = self.get_peaks(frequencies, spec, threshold,
                                           idx_min_dist)

        chord_name = self.music_theory.get_chords(f_peaks)
        print('Chords:')
        print(chord_name)
        self.plot_data(raw_data, frequencies, spec, id_peaks)

    def basic_file_operate(self, file, noise_file=None):
        raw_data, rate, noise_spec = self.get_data_from_file(file, noise_file)
        self.operate(raw_data, rate, noise_spec)

    def basic_record_operate(self, noise, length=3):
        raw_data, rate, noise_spec = self.get_data_from_recording(noise, length)
        self.operate(raw_data, rate, noise_spec)


if __name__ == '__main__':
    guitar_fft = GuitarFFT()
    guitar_fft.basic_file_operate(file="../resources/recording.wav")

#TODO and notes:  interpolate thing on peaks?
#combine with live input, either find note very 0.5sec if not too slow, how ot print?
#only detect chord if there is input detected?
#with the exact Hz, we can determine the exact note/string/fret
