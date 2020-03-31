from guitar import guitar_fft


def test_find_triad():
    guitarFFT = guitar_fft.GuitarFFT()
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
                      ]

    for i, notes in enumerate(notes_list):
        chord_name = guitarFFT.find_triad(notes)
        if chord_name == expected_chord[i]:
            print('Pass')
        else:
            print('Fail:')
            print(notes)
            print('actual: ' + chord_name + ', expected: ' + expected_chord[i])


if __name__ == '__main__':
    test_find_triad()
