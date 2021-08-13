import queue
import sys
import time

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import click

from fft import GuitarFFT, GUITAR_LOW_HZ_CUTOFF, GUITAR_HIGH_HZ_CUTOFF, GUITAR_MIN_HZ
from music_theory import MusicTheory


class PlotInput:
    def __init__(self, blocksize, samplerate, downsample, plot_update, window, device, channels, fft_update):
        self.blocksize = blocksize

        if samplerate is None:
            device_info = sd.query_devices(device, 'input')
            self.samplerate = device_info['default_samplerate'] / downsample
        else:
            self.samplerate = samplerate / downsample

        self.downsample = downsample
        self.interval = plot_update
        self.window = window
        self.device = device
        self.channels = channels
        self.fft_update = fft_update
        self.fft_start = time.time()

        self.guitar_fft = GuitarFFT()
        self.music_theory = MusicTheory()

        self.mapping = [c - 1 for c in channels]  # Channel numbers start with 1
        self.queue = queue.Queue()

        self.plotdata = None
        self.line = None
        self.spec = None
        self.freq = None

        self.figure = None

        self.note_start = time.time()
        self.print_count = 0

        self.setup_plot()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Fancy indexing with mapping creates a (necessary!) copy:
        self.queue.put(indata[::self.downsample, self.mapping])

    def update_plot(self, frame):
        """This is called by matplotlib for each plot update.

        Typically, audio callbacks happen more frequently than plot updates,
        therefore the queue tends to contain multiple blocks of audio data.

        """
        while True:
            try:
                data = self.queue.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            self.plotdata = np.roll(self.plotdata, -shift, axis=0)
            self.plotdata[-shift:, :] = data

            if (time.time() - self.fft_start) > self.fft_update:
                self.fft_start = time.time()
                formatted_data = self.plotdata.ravel()
                filtered_data = self.guitar_fft.filter_wav(formatted_data, self.samplerate,
                                                           (GUITAR_LOW_HZ_CUTOFF, GUITAR_HIGH_HZ_CUTOFF), 'bandpass')
                #TODO self.freq doesnt change once program started, can replace with _ maybe
                self.freq, self.spec = self.calc_fft(filtered_data, self.samplerate)

            if (time.time() - self.note_start) > 1:
                self.note_start = time.time()
                self.get_notes(self.freq, self.spec)
                self.print_count = self.print_count + 1
                print("Print count: " + str(self.print_count), flush=True)
                # print("data size: " + str(self.plotdata.size), flush=True)
                # print("freq 15/500: " + str(freq[15]) + "/" + str(freq[500]), flush=True)

        self.line[0].set_ydata(self.plotdata)
        self.line[1].set_ydata(self.spec)

        return self.line

    def calc_fft(self, data, rate):
        n = data.size
        #TODO find difference between these two
        if True:
            return self.guitar_fft.calc_fft(data, rate, n)
        else:
            data = data * np.hamming(n)
            time_step = 1. / rate

            sp = np.fft.rfft(data)
            freq = np.fft.rfftfreq(n, time_step)

            sp_processed = sp.real * sp.real

            max_v = sp_processed.max()
            if max_v != 0:
                sp_normalized = sp_processed / max_v
            else:
                sp_normalized = sp_processed

            return freq, sp_normalized

    def get_notes(self, frequencies, spec):
        idx_min_dist = (GUITAR_MIN_HZ / (self.samplerate / 2)) * (self.plotdata.size / 2)
        # TODO threshold value
        threshold = 0.06
        f_peaks, id_peaks = self.guitar_fft.get_peaks(frequencies, spec, threshold, idx_min_dist)
        chord_name = self.music_theory.get_chords(f_peaks)
        unique_notes = self.music_theory.get_unique_notes(f_peaks)

        print("Chords:", flush=True)
        print(chord_name, flush=True)
        print("Notes: ", flush=True)
        print(unique_notes, flush=True)
        #print("F peaks: ", flush=True)
        #print(f_peaks, flush=True)

    def setup_plot(self):
        try:
            length = int(self.window * self.samplerate / (1000 * self.downsample))
            self.plotdata = np.zeros((length, len(self.channels)))

            self.freq, self.spec = self.calc_fft(self.plotdata.ravel(), self.samplerate)

            fig, (ax1, ax2) = plt.subplots(1, 2)
            line1, = ax1.plot(self.plotdata)
            line2, = ax2.plot(self.freq, self.spec) # TODO freq only used here?
            self.line = [line1, line2]

            if len(self.channels) > 1:
                ax1.legend(['channel {}'.format(c) for c in self.channels],
                          loc='lower left', ncol=len(self.channels))

            ax1.axis((0, len(self.plotdata), -0.05, 0.05))
            ax2.axis((0, 1500, -0.1, 1.1))
            ax1.set_yticks([0])
            ax1.yaxis.grid(True)
            ax1.tick_params(bottom=False, top=False, labelbottom=False,
                            right=False, left=False, labelleft=False)
            fig.tight_layout(pad=0)

            self.figure = fig

        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
            exit(-1)

    def record_and_plot(self):
        stream = sd.InputStream(channels=max(self.channels), device=self.device,
                                samplerate=self.samplerate, blocksize=self.blocksize, callback=self.audio_callback)
        ani = FuncAnimation(self.figure, self.update_plot, interval=self.interval, blit=True)
        with stream:
            plt.show()


@click.command()
@click.option('--list-devices', '-l', help='show list of audio devices and exit', is_flag=True)
@click.option('--blocksize', '-b', help='block size (in samples)', default=0, show_default=True)
@click.option('--samplerate', '-r', help='sampling rate of audio device, default of the device will be used if not set')
@click.option('--downsample', '-n', help='display every Nth sample', default=10, show_default=True)
@click.option('--plot_update', '-p', help='minimum time between plot updates in ms', default=30, show_default=True)
@click.option('--fft_update', '-f', help='minimum time between fft updates in sec', default=0.2, show_default=True)
@click.option('--window', '-w', help='visible time slot in ms', default=5000, show_default=True)
@click.option('--device', '-d', help='input device (numeric ID or substring), leave blank for default device')
@click.option('--channels', '-c', help='input channels to plot', multiple=True, default=[1], show_default=True)
def main(list_devices, blocksize, samplerate, downsample, plot_update, window, device, channels, fft_update):
    """Program to plot input audio and perform fft. Run with no options to use default device and options."""
    if list_devices:
        print(sd.default.device)
        print("------")
        print(sd.query_devices())
        return
    if any(c < 1 for c in channels):
        print('argument CHANNEL: must be >= 1')
        return

    plot_input = PlotInput(blocksize, samplerate, downsample, plot_update, window, device, channels, fft_update)
    plot_input.record_and_plot()


if __name__ == '__main__':
    main()
