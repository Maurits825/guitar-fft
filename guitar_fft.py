import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import scipy.io.wavfile
import peakutils
from peakutils.plot import plot as pplot
import json
from scipy import signal
import re

TOTAL_NOTES = 12


class GuitarFFT:
    def __init__(self):
        self.raw_wav = None
        self.filtered_wav = None
        self.sampling_rate = 0
        self.frequencies = None
        self.normal_spec = None
        self.peak_indexes = None
        self.peak_frequencies = None

        freq_dict = json.loads(open('note_frequencies.json').read())
        self.note_frequencies = [[k, v] for k, v in freq_dict.items()]
        self.frequencies_np_arr = np.array(list(zip(*self.note_frequencies))[1])

        self.musical_alphabet = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    def calc_fft(self, data, rate, n, noise=None):
        data = data * np.hamming(data.size)
        time_step = 1. / rate

        sp = np.fft.rfft(data, n)
        freq = np.fft.rfftfreq(n, time_step)

        if noise is not None:
            sp_corrected = (np.abs(sp) / (n * 2)) - noise
        else:
            sp_corrected = np.abs(sp) / (n * 2)

        sp_normalized = sp_corrected / sp_corrected.max()

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

    def get_note(self, frequency):
        idx = (np.abs(self.frequencies_np_arr - frequency)).argmin()
        return self.note_frequencies[idx][0]

    def get_chord(self, peak_frequencies):
        print("Notes:")
        unique_notes = []
        for frequency in peak_frequencies[:6]:
            note = self.get_note(frequency)
            print(str(frequency) + 'Hz, ' + str(note))
            note_letter = re.search(r'(.*?)[0-9].*', note)
            if note_letter.group(1) not in unique_notes:
               unique_notes.append(note_letter.group(1))

        num_notes = len(unique_notes)
        chord = 'None'
        if num_notes == 3:
            chord = self.find_triad(unique_notes)

        return chord

    def find_triad(self, notes):
        chord_name = 'Unknown'
        for idx, root_note in enumerate(notes):
            triad_notes = self.get_triad_types(root_note)

            slash_chord = ''
            inversion = ''
            if idx > 0:
                slash_chord = notes[0] + '/'

            for triad_type in triad_notes:
                if triad_notes[triad_type][1] in notes and triad_notes[triad_type][2] in notes:
                    if notes[0] == triad_notes[triad_type][1]:
                        inversion = ' (first inversion)'
                    elif notes[0] == triad_notes[triad_type][2]:
                        inversion = ' (second inversion)'

                    chord_name = slash_chord + root_note + ' ' + triad_type + inversion

                    return chord_name

    def get_triad_types(self, root_note):
        triad_types = {
            "Major": [4, 7],
            "Minor": [3, 7],
            "Diminished": [3, 6],
            "Sus2": [2, 7],
            "Sus4": [5, 7],
        }

        triad_notes = {}

        root_ind = self.musical_alphabet.index(root_note)
        for triad_type in triad_types:
            notes = [root_note]
            for interval in triad_types[triad_type]:
                notes.append(self.musical_alphabet[(root_ind + interval) % TOTAL_NOTES])

            triad_notes[triad_type] = notes

        return triad_notes

    def plot_data(self, data, freq, spec, peak_idx):
        plt.subplot(1, 2, 1)
        plt.plot(data)
        plt.subplot(1, 2, 2)
        pplot(freq, spec, peak_idx)
        plt.xlim(-10, 1500)
        plt.show()

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

    def basic_operate(self, noise, file=None, length=3):
        if file:
            rate, raw_data = self.load_file(file)
            noise_rate, noise_raw_data = self.load_file('E major noise.wav')
        else:
            if noise:
                noise_rate, noise_raw_data = self.record_audio(length)
            print('Recording...')
            rate, raw_data = self.record_audio(length)
            print('Recording done!')
        n = raw_data.size

        if noise:
            noise_f, noise_spec = self.calc_fft(noise_raw_data, noise_rate, n)

        filtered_data = self.filter_wav(raw_data, rate, (80, 1500), 'bandpass')
        frequencies, spec = self.calc_fft(filtered_data, rate, n)

        freq_min_dist = 20 # you cant play two notes 20hz apart on guitar at same time
        idx_min_dist = (freq_min_dist / (rate/2)) * (n/2)
        #TODO threshold value
        f_peaks, id_peaks = self.get_peaks(frequencies, spec, 0.007, idx_min_dist)

        chord_name = self.get_chord(f_peaks)
        print(chord_name)
        self.plot_data(raw_data, frequencies, spec, id_peaks)


if __name__ == '__main__':
    guitar_fft = GuitarFFT()
    guitar_fft.basic_operate(False, length=3)

#TODO and notes:  interpolate thing on peaks
#mag of lower freq are low - do some research? maybe some hz to mag ratio?

#remember, "noise" or nosiy fft is not actual noise in time domain, not really
#averaging fft is  common practice
#make func to detect notes -- improve, other chords,
#threshold algorithm?
#combine with live input, either find note very 0.5sec if not too slow, how ot print?
#only detect chord if there is input detected?
