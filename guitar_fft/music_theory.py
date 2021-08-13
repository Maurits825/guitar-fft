import re
import numpy as np
import json
from pathlib import Path

RESOURCE_FOLDER = Path(__file__).parent.parent / "resources"

# Used to limit the notes taken from frequencies, the first six notes should
# be the only relevant ones as there are 6 strings right?
# Unless one of the harmonics of the lowest notes occur before a higher note
# that is actually quite likely
# for the A major wav file, this will correctly id as Amaj, if the limit is
# is removed there is a B5 at 993Hz there which makes it a Aadd9
# idk why there is a random peak at 993Hz, could it be a mix of harmonics?
GUITAR_STRINGS = 6

TOTAL_NOTES = 12

# TODO add below is json file?
MUSICAL_ALPHABET = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#',
                    'G', 'G#']
SCALE_PATTERNS = {
    'Major': [2, 2, 1, 2, 2, 2],
    'Natural Minor': [2, 1, 2, 2, 1, 2],
    'Minor Pentatonic': [3, 2, 2, 3],
}  # TODO add more scales

CHORD_TYPES = {
            "Major": [4, 7],
            "Minor": [3, 7],
            "Diminished": [3, 6],
            "Sus2": [2, 7],
            "Sus4": [5, 7],
            "Major Seventh": [4, 7, 11],
            "Minor Seventh": [3, 7, 10],
            "Dominant Seventh": [4, 7, 10],
            "Augmented": [4, 8],
            "Dominant Ninth": [4, 7, 10, 14],
            "Major Eleventh": [4, 7, 11, 14, 17],
            "Add9": [4, 7, 14],
            "5": [7],
}


class MusicTheory:
    def __init__(self):
        with open(RESOURCE_FOLDER / "note_frequencies.json") as notes_json:
            freq_dict = json.loads(notes_json.read())

        self.note_frequencies = [[k, v] for k, v in freq_dict.items()]
        self.frequencies_np_arr = np.array(
            list(zip(*self.note_frequencies))[1])

        self.scales = self.create_scales()

    def get_chords(self, peak_frequencies):
        unique_notes = self.get_unique_notes(peak_frequencies)
        chords = self.find_chords(unique_notes)

        return chords

    def get_note(self, frequency):
        idx = (np.abs(self.frequencies_np_arr - frequency)).argmin()
        return self.note_frequencies[idx][0]

    def get_unique_notes(self, peak_frequencies):
        unique_notes = []
        for frequency in peak_frequencies[:GUITAR_STRINGS]:
            note = self.get_note(frequency)
            note_letter = re.search(r'(.*?)[0-9].*', str(note)).group(1)
            if note_letter not in unique_notes:
                unique_notes.append(note_letter)

        return unique_notes

    def find_chords(self, notes):
        chord_names = []
        for idx, root_note in enumerate(notes):
            triad_notes = self.get_chord_types(root_note)

            for triad_type in triad_notes:
                slash_chord = ''
                inversion = ''

                if set(triad_notes[triad_type]) == set(notes):
                    try:
                        if notes[0] == triad_notes[triad_type][1]:
                            slash_chord = notes[0] + '/'
                            inversion = ' (first inversion)'
                        elif notes[0] == triad_notes[triad_type][2]:
                            slash_chord = notes[0] + '/'
                            inversion = ' (second inversion)'
                    except IndexError:
                        pass

                    chord_name = slash_chord + root_note + ' ' + triad_type + inversion

                    chord_names.append(chord_name)
        return chord_names

    def get_chord_types(self, root_note):
        chord_notes = {}

        root_ind = MUSICAL_ALPHABET.index(root_note)
        for chord_type in CHORD_TYPES:
            notes = [root_note]
            for interval in CHORD_TYPES[chord_type]:
                notes.append(MUSICAL_ALPHABET[(root_ind + interval) % TOTAL_NOTES])

            chord_notes[chord_type] = notes

        return chord_notes

    def create_scales(self):
        scales = {}
        for note in MUSICAL_ALPHABET:
            for pattern in SCALE_PATTERNS:
                scale_name = note + ' ' + pattern
                scales[scale_name] = [note]

                current_note = MUSICAL_ALPHABET.index(note)
                for inc in SCALE_PATTERNS[pattern]:
                    current_note = (current_note + inc) % TOTAL_NOTES
                    scales[scale_name].append(MUSICAL_ALPHABET[current_note])

        return scales

    def find_scale(self, notes):
        print('Notes match following scales:')
        scales = []
        for scale in self.scales:
            match = True
            for note in notes:
                if note not in self.scales[scale]:
                    match = False
                    break

            if match:
                scales.append(scale)
                print(scale)

        return scales
