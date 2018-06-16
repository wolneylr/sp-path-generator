class Note:
    def __init__(self, position, number, length):
        self.position = position
        self.number = number
        self.length = length

class SP_Phrase:
    def __init__(self, position, length):
        self.position = position
        self.length = length

class Chart:
    NOTE_SCORE = 50
    MY_HEART_SCORE = 78762
    BROKED_SCORE = 61950
    KILLING_SCORE = 393643

    def __init__(self, instrument, difficulty, resolution):
        self.instrument = instrument
        self.difficulty = difficulty
        self.sections = []
        self.notes = []
        self.sp_phrases = []
        self.resolution = resolution
        self.measure_length = resolution * 4

    def add_note(self, note):
        self.notes.append(note)

    def add_sp_phrase(self, sp_phrase):
        self.sp_phrases.append(sp_phrase)

    def total_unique_notes(self):
        notes_count = 0

        for i in range(0, len(self.notes)):
            if i == 0:
                notes_count += 1
            elif self.notes[i].position != self.notes[i - 1].position:
                notes_count += 1

        return notes_count

    def base_score(self, note_length):
        score = 0
        multiplier = 1
        unique_note_index = 0

        for i in range(0, len(self.notes)):
            unique_note = False

            if i == 0:
                unique_note = True
            elif self.notes[i].position != self.notes[i - 1].position:
                unique_note = True

            if unique_note is True:
                unique_note_index += 1
                if unique_note_index > 30:
                    multiplier = 4
                else:
                    multiplier = unique_note_index % 10 + 1

            score += self.NOTE_SCORE * multiplier

            if note_length is True and self.notes[i].length > 0 and unique_note is True:
                score += self.NOTE_SCORE * 2 * multiplier * self.notes[i].length / self.measure_length

            """
            if note < len(self.notes) - 1:# and unique_note_index < 500:
                if self.notes[note]["position"] != self.notes[note + 1]["position"]:
                    print(str(unique_note_index) + " - " + str(score))
                    """

        return score

    def avg_multiplier(self):
        song_length = self.notes[len(self.notes) - 1].position + \
         self.notes[len(self.notes) - 1].length

        sum_multiplier = 0
        multiplier = 1

        for position in range(0, song_length):
            if position > 30:
                multiplier = 4
            else:
                multiplier = position % 10 + 1

            sum_multiplier += multiplier

        return sum_multiplier / song_length

class Song:

    DIFFICULTIES = ['ExpertSingle', 'HardSingle', 'MediumSingle', 'EasySingle',
        'ExpertDoubleBass','HardDoubleBass', 'MediumDoubleBass', 'EasyDoubleBass']

    def __init__(self, name, resolution=192):
        self.name = name if name != "" else "Unknown"
        self.resolution = resolution
        self.sections = []
        self.charts = []

    def add_section(self, section):
        self.sections.append(section)

    def add_chart(self, chart):
        self.charts.append(chart)