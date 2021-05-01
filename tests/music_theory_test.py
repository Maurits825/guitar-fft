from music_theory import MusicTheory


def test_find_scale():
    music_theory = MusicTheory()
    music_theory.find_scale(['G', 'A', 'E', 'C', 'D', 'B', 'F'])


def test_find_chord():
    music_theory = MusicTheory()
    chords = music_theory.find_chords(['C#', 'G#', 'F'])
    print(chords)


def test_find_triad():
    music_theory = MusicTheory()
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
        chord_names = music_theory.find_chords(notes)
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
