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
        chord_names = guitarFFT.find_chords(notes)
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

if __name__ == '__main__':
    test_find_triad()
