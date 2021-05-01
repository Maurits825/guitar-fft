import music_theory as mt


def test_find_scale():
    music_theory = mt.MusicTheory()
    music_theory.find_scale(['G', 'A', 'E', 'C', 'D', 'B', 'F'])


def test_find_chord():
    music_theory = mt.MusicTheory()
    chords = music_theory.find_chords(['C#', 'G#', 'F'])
    print(chords)
