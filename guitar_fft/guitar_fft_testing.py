from guitar_fft.fft import GuitarFFT
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

RESOURCE_FOLDER = Path(__file__).parent.parent / "resources"


def test_filter_wav():
    guitar = GuitarFFT()
    file = RESOURCE_FOLDER / "c4.wav"
    rate, raw_data = guitar.load_file(file)

    n = raw_data.size
    filtered_data = guitar.filter_wav(raw_data, rate, (80, 1000), 'bandpass')

    freq_raw, spec_raw = guitar.calc_fft(raw_data, rate, n)
    freq_filtered, spec_filtered = guitar.calc_fft(filtered_data, rate, n)

    plt.subplot(2, 2, 1)
    plt.title('raw data')
    plt.plot(raw_data)
    plt.xlim(0, 40000)

    plt.subplot(2, 2, 2)
    plt.title('filtered data')
    plt.plot(filtered_data)
    plt.xlim(0, 40000)

    plt.subplot(2, 2, 3)
    plt.title('raw data fft')
    plt.plot(freq_raw, spec_raw)
    plt.xlim(-10, 5000)

    plt.subplot(2, 2, 4)
    plt.title('filtered data fft ')
    plt.plot(freq_filtered, spec_filtered)
    plt.xlim(-10, 5000)

    plt.show()


def test_window():
    guitar = GuitarFFT()
    file = RESOURCE_FOLDER / "a5.wav"
    rate, raw_data = guitar.load_file(file)

    raw_data = raw_data

    n = raw_data.size
    filtered_data = guitar.filter_wav(raw_data, rate, (80, 1000), 'bandpass')

    freq_raw, spec_raw = guitar.calc_fft(raw_data, rate, n)
    freq_hamming, spec_hamming = guitar.calc_fft(filtered_data, rate, n)
    freq, spec = guitar.calc_fft(filtered_data, rate, n, do_hamming=False)

    data_hamming = raw_data * np.hamming(raw_data.size)

    plt.subplot(2, 2, 1)
    plt.title('raw data')
    plt.plot(raw_data)

    plt.subplot(2, 2, 2)
    plt.title('data hamming')
    plt.plot(data_hamming)

    plt.subplot(2, 2, 3)
    plt.title('raw data fft')
    plt.plot(freq, spec)
    plt.xlim(-10, 1000)

    plt.subplot(2, 2, 4)
    plt.title('hamming data fft ')
    plt.plot(freq_hamming, spec_hamming)
    plt.xlim(-10, 1000)

    plt.show()


def test_downsampling():
    guitar = GuitarFFT()
    file = RESOURCE_FOLDER / "amin.wav"
    rate, raw_data = guitar.load_file(file)

    downsample = 2
    downsample_data = raw_data[::downsample]

    n = raw_data.size
    filtered_data = guitar.filter_wav(raw_data, rate, (80, 2000), 'bandpass')
    freq, spec = guitar.calc_fft(filtered_data, rate, n)

    n2 = downsample_data.size
    down_rate = rate / downsample
    filtered_data_down = guitar.filter_wav(downsample_data, down_rate, (80, 2000), 'bandpass')
    freq_down, spec_down = guitar.calc_fft(filtered_data_down, down_rate, n2)

    plt.subplot(2, 2, 1)
    plt.title('data')
    plt.plot(raw_data)
    #plt.xlim(0, 40000)

    plt.subplot(2, 2, 2)
    plt.title(str(downsample) + 'x downsampled data')
    plt.plot(downsample_data)
    #plt.xlim(0, 40000)

    plt.subplot(2, 2, 3)
    plt.title('fft')
    plt.plot(freq, spec)
    plt.xlim(-10, 3000)

    plt.subplot(2, 2, 4)
    plt.title(str(downsample) + 'x downsampled fft ')
    plt.plot(freq_down, spec_down)
    plt.xlim(-10, 3000)

    plt.show()


if __name__ == '__main__':
    #test_filter_wav()
    #test_window()
    test_downsampling()
