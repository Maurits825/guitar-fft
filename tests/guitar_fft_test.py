from guitar_fft import GuitarFFT
import matplotlib.pyplot as plt
from pathlib import Path

RESOURCE_FOLDER = Path(__file__).parent.parent / "resources"


def test_filter_wav():
    guitar = GuitarFFT()
    file = RESOURCE_FOLDER / "a_maj.wav"
    rate, raw_data = guitar.load_file(file)

    n = raw_data.size
    filtered_data = guitar.filter_wav(raw_data, rate, (80, 1000), 'bandpass')

    freq_raw, spec_raw = guitar.calc_fft(raw_data, rate, n)
    freq_filtered, spec_filtered = guitar.calc_fft(filtered_data, rate, n)

    plt.subplot(1, 2, 1)
    plt.title('raw data')
    plt.plot(freq_raw, spec_raw)
    plt.xlim(-10, 5000)

    plt.subplot(1, 2, 2)
    plt.title('filtered data')
    plt.plot(freq_filtered, spec_filtered)
    plt.xlim(-10, 5000)

    plt.show()
