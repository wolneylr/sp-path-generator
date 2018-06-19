import math

class Chart:
    NOTE_SCORE = 50
    MY_HEART_SCORE = 78762
    BROKED_SCORE = 55850
    KILLING_SCORE = 393643
    MEUERRO_SCORE = 159402
    SOULLESS4_AVGMULT = 2079014
    BROKED_AVGMULT = 3.777

    def __init__(self, difficulty, resolution):
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
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                notes_count += 1

        return notes_count

    def base_score(self, note_length, print_score):
        score = 0
        multiplier = 1
        unique_note_index = 0

        for i in range(0, len(self.notes)):
            unique_note = False

            if i == 0:
                unique_note = True
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                unique_note = True

            if unique_note is True:
                unique_note_index += 1
                if unique_note_index > 30:
                    multiplier = 4
                else:
                    multiplier = math.floor(unique_note_index / 10) + 1

            score += self.NOTE_SCORE * multiplier

            if note_length is True and self.notes[i]["length"] > 0 and unique_note is True:
                score += self.NOTE_SCORE * 2 * multiplier * self.notes[i]["length"] / self.measure_length

            if print_score:
                    if i == 0:
                        print(str(unique_note_index) + " - " + str(score))
                    elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                        print(str(unique_note_index) + " - " + str(score))               

        return score

    '''
        Since the song's length is based on the song file, the average multiplier is based on 
        the chart's length, not the song.
    '''
    def avg_multiplier(self):
        song_length = self.notes[len(self.notes) - 1]["position"] \
            + self.notes[len(self.notes) - 1]["length"]

        sum_multiplier = 0
        multiplier = 1
        unique_note_index = 0

        multinc_pos = []

        for i in range(0, len(self.notes)):
            unique_note = False

            if i == 0:
                unique_note = True
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                unique_note = True

            if unique_note is True:
                unique_note_index += 1
                if unique_note_index >= 30:
                    multiplier = 4
                    multinc_pos.append(self.notes[i]["position"])
                    break
                else:
                    next_multiplier = math.floor(unique_note_index / 10) + 1
                    if next_multiplier > multiplier:
                        multiplier = next_multiplier
                        multinc_pos.append(self.notes[i]["position"])

        multiplier = 1

        for position in range(0, song_length):
            if multinc_pos:
                if position >= multinc_pos[0]:
                    multiplier += 1
                    multinc_pos.remove(multinc_pos[0])

            sum_multiplier += multiplier

        return sum_multiplier / song_length

class Song:

    DIFFICULTIES = ['ExpertSingle', 'HardSingle', 'MediumSingle', 'EasySingle',
        'ExpertDoubleBass','HardDoubleBass', 'MediumDoubleBass', 'EasyDoubleBass'
        'ExpertDoubleRhythm','HardDoubleRhythm', 'MediumDoubleRhythm', 'EasyDoubleRhythm'
        'ExpertKeyboard','HardKeyboard', 'MediumKeyboard', 'EasyKeyboard'
        'ExpertDrums','HardDrums', 'MediumDrums', 'EasyDrums']

    def __init__(self, name, resolution=192):
        self.name = name if name else "Unknown"
        self.resolution = resolution
        self.bpms = []
        self.time_signatures = []
        self.sections = []
        self.charts = []


    def add_section(self, section):
        self.sections.append(section)

    def add_bpm(self, bpm):
        self.bpms.append(bpm)

    def add_time_signature(self, time_signature):
        self.time_signatures.append(time_signature)

    def add_chart(self, chart):
        self.charts.append(chart)