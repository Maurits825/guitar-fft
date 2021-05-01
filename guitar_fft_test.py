import guitar_fft
import matplotlib.pyplot as plt

def test_find_triad():
    guitar = guitar_fft.GuitarFFT()
    notes_list = [['E', 'G#', 'B'],
                  ['E', 'B', 'G#'],
                  ['G#', 'E', 'B'],
                  ['B', 'E', 'G#'],
                  ['E', 'G', 'B'],
                  ['G', 'E', 'B'],
                  ['B', 'G', 'E'],
                  ['E', 'G', 'A#'],
                  ['E', 'A', 'B'],
                  ['E', 'F#', 'B'],
                  ['C', 'E', 'G', 'B'],
                  ['C', 'D#', 'G', 'A#'],
                  ['C', 'E', 'G', 'A#'],
                  ['C', 'E', 'G#'],
                  ['C', 'E', 'G', 'A#', 'D'],
                  ['C', 'E', 'G', 'B', 'D', 'F'],
                  ['C', 'E', 'G', 'D'],
                  ['C', 'G'],
                  ]
    expected_chord = ['E Major',
                      'E Major',
                      'G#/E Major (first inversion)',
                      'B/E Major (second inversion)',
                      'E Minor',
                      'G/E Minor (first inversion)',
                      'B/E Minor (second inversion)',
                      'E Diminished',
                      'E Sus4',
                      'E Sus2',
                      'C Major Seventh',
                      'C Minor Seventh',
                      'C Dominant Seventh',
                      'C Augmented',
                      'C Dominant Ninth',
                      'C Major Eleventh',
                      'C Add9',
                      'C 5',
                      ]

    pass_count = 0
    fail_count = 0
    for i, notes in enumerate(notes_list):
        chord_names = guitar.find_chords(notes)
        if chord_names[0] == expected_chord[i]:
            pass_count += 1
            print('Pass')
        else:
            fail_count += 1
            print('Fail:')
            print(notes)
            print('Expected: ' + expected_chord[i])
            print('Actual:')
            for chord in chord_names:
                print(chord)

    print('\n')
    print('Pass: ' + str(pass_count))
    print('Pass: ' + str(fail_count))


def test_filter_wav():
    guitar = guitar_fft.GuitarFFT()
    file = "a_maj.wav"
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


if __name__ == '__main__':
    test_find_triad()
