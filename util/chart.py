import math
import bisect
from decimal import ROUND_HALF_UP, Decimal

from .sp_path import SP_Path

class Chart:
    NOTE_SCORE = 50
    MY_HEART_SCORE = 78762
    BROKED_SCORE = 55850
    KILLING_SCORE = 393643
    MEUERRO_SCORE = 159402
    BATCOUNTRY_SCORE_NO_SOLO = 363378
    BATCOUNTRY_SCORE = 390278
    BATCOUNTRY_SCORE_21_5 = 389850
    SOULLESS4_SCORE = 2079014
    BROKED_AVGMULT = 3.777

    def __init__(self, difficulty, resolution):
        self.difficulty = difficulty
        self.resolution = resolution
        self.sections = []
        self.notes = []  
        self.solo_sections = []
        self.sp_phrases = []
        self.solo_end_notes = []

        self.length = 0

        self.sp = 0
        self.sl = 0
        self.sa = 0

    def calc_chart_length(self):
        if len(self.notes) == 0:
            return 0

        position = self.notes[len(self.notes) - 1]["position"]
        length = self.notes[len(self.notes) - 1]["length"]

        max_length = position + length

        note_numbers = []

        for i in range(len(self.notes) - 1, -1, -1): 
            if self.notes[i]["number"] not in note_numbers:
                if self.notes[i]["length"] > 0:
                    position = self.notes[i]["position"]
                    length = self.notes[i]["length"]

                    if position + length > max_length:
                        max_length = position + length 

                note_numbers.append(self.notes[i]["number"])

                if len(note_numbers) == 5 and 7 not in note_numbers:
                    break
                elif len(note_numbers) == 6:
                    break

        return max_length

    def add_sp_path(self):
        if self.sp_phrases:
            self.sp_path = SP_Path(self) 

    def pos_in_section(self, i, sections, position):
        while i < len(sections):
            if sections[i]["position"] + sections[i]["length"] - 1 < position:  
                i += 1
            else:
                return i, sections[i]["position"] <= position
            
        return i, False   

    def add_note(self, note):
        self.notes.append(note)

    def add_solo_section(self, solo_section):
        self.solo_sections.append(solo_section)

    def add_sp_phrase(self, sp_phrase):
        self.sp_phrases.append(sp_phrase)

    def add_solo_end_notes(self): 
        if not self.solo_sections:
            return
    
        solo_sections = self.solo_sections

        notes_pos = [note["position"] for note in self.notes]
    
        for s in range(len(solo_sections)):
            self.solo_end_notes.append(self.notes[bisect.bisect_right(
            notes_pos, solo_sections[s]["position"] + solo_sections[s]["length"] - 1) - 1])

    def total_unique_notes(self):
        notes_count = 0

        for i in range(len(self.notes)):
            if i == 0:
                notes_count += 1
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                notes_count += 1

        return notes_count

    def calc_unote_index(self, note):
        note_index = self.notes.index(note)
        unique_note_index = 0

        for i in range(note_index + 1):
            if i == 0:
                unique_note_index += 1
            elif self.notes[i]["position"] > self.notes[i - 1]["position"]:
                unique_note_index += 1

        return unique_note_index

    def calc_note_multiplier(self, unote_index):
        if unote_index > 30:
            return 4
        else:
            return math.floor(unote_index / 10) + 1

    def is_unique_note(self, note):
        note_index = self.notes.index(note)

        if note_index == 0:
            return True
        elif self.notes[note_index]["position"] > self.notes[note_index - 1]["position"]:
            return True
        
        return False

    def calculate_score(self, start, end):
        score = 0
        multiplier = 1
        unique_note_index = 0

        for i in range(start, end):

            unique_note = self.is_unique_note(self.notes[i])

            if unique_note:
                if multiplier < 4:
                    unique_note_index += 1
                    if unique_note_index > 30:
                        multiplier = 4
                    else:
                        multiplier = math.floor(unique_note_index / 10) + 1

            score += self.NOTE_SCORE * multiplier

            self.sl, pos_in_solo = self.pos_in_section(self.sl, self.solo_sections, self.notes[i]["position"])

            '''
            if self.sp_phrases:
                self.sa, pos_in_path = self.pos_in_section(self.sa, self.sp_path.sp_activations, self.notes[i]["position"])
                if pos_in_path:
                    score += self.NOTE_SCORE * multiplier
            '''

            if pos_in_solo:
                score += self.NOTE_SCORE * 2      

            if self.notes[i]["length"] > 0 and unique_note:
                score += self.NOTE_SCORE / 2 * multiplier * self.notes[i]["length"] / self.resolution
                score = int(Decimal(score).quantize(0, ROUND_HALF_UP))

        self.sp = 0
        self.sl = 0
        self.sa = 0
        return score

    def avg_multiplier(self):

        multiplier = 1

        chart_length = self.length

        if chart_length == 0:
            return multiplier

        sum_multiplier = 0       
        unique_note_index = 0

        # multinc_pos = []

        for i in range(len(self.notes)):
            if self.is_unique_note(self.notes[i]):
                if multiplier < 4:
                    unique_note_index += 1
                    if unique_note_index == 30:
                        multiplier = 4
                        # multinc_pos.append(self.notes[i]["position"])
                        # break
                    else:
                        multiplier = math.floor(unique_note_index / 10) + 1
                        '''
                        next_multiplier = math.floor(unique_note_index / 10) + 1
                        if next_multiplier > multiplier:
                            multiplier = next_multiplier
                            multinc_pos.append(self.notes[i]["position"])
                        '''

                sum_multiplier += multiplier

        '''
        multiplier = 1

        for position in range(0, song_length):
            if multinc_pos:
                if position >= multinc_pos[0]:
                    multiplier += 1
                    multinc_pos.remove(multinc_pos[0])

            sum_multiplier += multiplier

        return sum_multiplier / song_length
        '''
        return sum_multiplier / self.total_unique_notes()