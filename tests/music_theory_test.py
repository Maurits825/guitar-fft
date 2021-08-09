from guitar_fft.music_theory import MusicTheory
import unittest


class MusicTheoryTest(unittest.TestCase):
    def setUp(self):
        self.mt = MusicTheory()

    def test_find_scale(self):
        scales = self.mt.find_scale(['G', 'A', 'E', 'C', 'D', 'B', 'F'])
        self.assertTrue("A Natural Minor" in scales)
        self.assertTrue("C Major" in scales)

    def test_find_chord(self):
        chords = self.mt.find_chords(['C#', 'G#', 'F'])
        self.assertEqual(['C# Major'], chords)

    def test_find_triad(self):
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

        for i, notes in enumerate(notes_list):
            chord_names = self.mt.find_chords(notes)
            self.assertEqual(expected_chord[i], chord_names[0])
