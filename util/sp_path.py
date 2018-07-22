import bisect
import math
from decimal import ROUND_HALF_UP, Decimal

import networkx as nx


class SP_Bar(object):
    def __init__(self, length):
        self.length = length
        self.set(0)

    def set(self, new_value):
        self.number = max(0, min(self.length, new_value))

    def calc_percentage(self):
        return self.number / self.length

class SP_Path:

    SP_BAR_BEATS = 32

    def __init__(self, chart):
        self.chart = chart
        self.sp_phrases = self.chart.sp_phrases

        self.sp_bar = SP_Bar(self.chart.resolution * self.SP_BAR_BEATS)

        #self.add_sp_values()
        #self.total_sp_value = sum([sp_phrase["value"] for sp_phrase in self.sp_phrases])   

        self.sp_end_notes = self.calc_sp_end_notes()

        self.pos_scores = self.calc_pos_values(0, self.chart.length)

        self.num_activations = int(self.pos_scores[len(self.pos_scores) - 1]["sp_value"] / (self.sp_bar.length / 2))

        '''
        sp_file = open("sp_values.txt","w") 

        for i in range(len(self.pos_scores)):
            sp_file.write(str(i) + " = " + str(self.pos_scores[i]["sp_value"]) + '\n') 
        
        sp_file.close() 
        '''

        # print("sum of sp values = " + str(sum([sp_phrase["value"] for sp_phrase in self.sp_phrases])))
        print("last pos sp value = " + str(self.pos_scores[len(self.pos_scores) - 1]["sp_value"]))

        self.max_score_lengths = self.calc_largest_scores(self.pos_scores, 
        int(self.sp_bar.length / 2) if self.chart.length > int(self.sp_bar.length / 2) \
        else self.chart.length, self.num_activations, 0, len(self.pos_scores)) 

        '''
        self.phrase_sums = self.calc_phrase_sums(len(self.sp_phrases))  
        for phrase_sum in self.phrase_sums:
            print(str(phrase_sum))
        print("len(self.phrase_sums) = " + str(len(self.phrase_sums)))
        '''

        self.sp_activations = []
        self.num_phrases = []
        #self.set_basic_sp_path() 

    def add_sp_values(self): 
        notes_pos = [note["position"] for note in self.chart.notes]

        upper_pos_i = 0

        for i in range(len(self.sp_phrases)):
            sp_value = 0

            lower_pos = self.sp_phrases[i]["position"]
            
            lower_pos_i = bisect.bisect_left(notes_pos, lower_pos, lo=upper_pos_i)

            upper_pos = lower_pos + self.sp_phrases[i]["length"] - 1

            upper_pos_i = bisect.bisect_right(notes_pos, upper_pos, lo=lower_pos_i)
            sp_notes = self.chart.notes[lower_pos_i:upper_pos_i]

            sp_value += self.sp_bar.length / 4

            for j in range(len(sp_notes)):
                if self.chart.is_unique_note(sp_notes[j]):     
                    sp_value += sp_notes[j]["length"]

            

            self.sp_phrases[i]["value"] = int(sp_value)

    def calc_pos_values(self, start, end): 

        pos_values = []

        c_length = start
    
        pos_length = 1

        c_multiplier = 1

        notes = self.chart.notes
        n = 0
        sustain_notes = []

        pos_in_phrase = False

        pos_score = 0
        sp_value = 0

        while c_length <= end:
            c_length += pos_length

            pos_score = 0

            if sustain_notes:
                for i in range(len(sustain_notes)):
                    length_score = self.chart.NOTE_SCORE / 2 * c_multiplier / self.chart.resolution

                    sustain_notes[i]["length"] -= pos_length          

                    pos_score += length_score          

                    if sustain_notes[i]["in_phrase"]:
                        sp_value += pos_length 

                    if sustain_notes[i] == 0:
                        tail_length = sustain_notes[i]["og_length"] / self.chart.resolution
                        tail_length = tail_length / 4
                        pos_score += tail_length

                        pos_score = int(Decimal(pos_score).quantize(0, ROUND_HALF_UP))
                # Removes notes with empty length
                for i in range(len(sustain_notes)):
                    if i >= len(sustain_notes):
                        break

                    if sustain_notes[i]["length"] == 0:
                        sustain_notes.remove(sustain_notes[i])       

            if n < len(notes): 
                while notes[n]["position"] < c_length:    
                    if c_multiplier < 4:
                        c_multiplier = self.chart.calc_note_multiplier(self.chart.calc_unote_index(notes[n])) 

                    pos_score += self.chart.NOTE_SCORE * c_multiplier  

                    self.chart.sp, pos_in_phrase = self.chart.pos_in_section(self.chart.sp, 
                        self.chart.sp_phrases, notes[n]["position"])   

                    if notes[n]["length"] > 0 and self.chart.is_unique_note(notes[n]):  

                        sustain_note =	{
                            "length": notes[n]["length"],
                            "og_length": notes[n]["length"],
                            "in_phrase": pos_in_phrase and (len(sustain_notes) == 0)
                        } 

                        sustain_notes.append(sustain_note)    
                    
                    if notes[n] in self.sp_end_notes:
                        sp_value += self.sp_bar.length / 4
                        


                    n += 1
                    
                    if n == len(notes):
                        break

            pos_value = {
                "score" : pos_score,
                "sp_value" : sp_value
            }
                        
            pos_values.append(pos_value) 
        
        self.chart.sp = 0
        return pos_values

    """
        Return the index where to insert item x in list a, assuming a is sorted in descending order.

        The return value i is such that all e in a[:i] have e >= x, and all e in
        a[i:] have e < x.  So if x already appears in the list, a.insert(x) will
        insert just after the rightmost x already there.

        Optional args lo (default 0) and hi (default len(a)) bound the
        slice of a to be searched.

        Essentially, the function returns number of elements in a which are >= than x.
        > a = [8, 6, 5, 4, 2]
        > reverse_bisect_right(a, 5)
        3
        > a[:reverse_bisect_right(a, 5)]
        [8, 6, 5]
    """
    def reverse_bisect_right(self, a, x, lo=0, hi=None):
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if x > a[mid]: hi = mid
            else: lo = mid + 1
        return lo

    # A modified version of Kadane's algorithm (Dynamic Programming)
    def calc_largest_scores(self, positions, length, num_scores, start, end):
        overlapping_lengths = False

        prev_seq_score = 0

        n_length = (end - start) if (end - start) < length else length

        for i in range(n_length):
            prev_seq_score += positions[i]["score"]

        start_i_final = 0

        end_i_final = n_length - 1

        max_score = {
            "score": prev_seq_score,
            "position": start_i_final,
            "length": (end_i_final - start_i_final + 1)
        }

        max_scores = [max_score]

        c_score = 0

        for i in range(length, end):
            c_score = prev_seq_score + positions[i]["score"] - positions[i - length]["score"]
            
            max_scores_scores = [max_score["score"] for max_score in max_scores]

            score_index = self.reverse_bisect_right(max_scores_scores, c_score)

            end_i_final = i
            start_i_final = i - length + 1

            c_max_score = {
                "score": c_score,
                "position": start_i_final,
                "length": (end_i_final - start_i_final + 1)
            }

            insert_length = True
            
            # Only insert length if length's starting position is bigger than first activation position
            if len(self.sp_end_notes) > 1:
                if (i - length + 1) < self.sp_end_notes[1]["position"]:
                    insert_length = False

            if not overlapping_lengths and insert_length:
                for j in range(len(max_scores)):
                    # Checks if current max score length overlaps with max score length from array
                    if c_max_score["position"] >= max_scores[j]["position"] and \
                    c_max_score["position"] < max_scores[j]["position"] + max_scores[j]["length"]:
                        if j >= score_index:
                            max_scores.remove(max_scores[j])     
                        else:
                            insert_length = False
                        break                 

            if insert_length:
                max_scores.insert(score_index, c_max_score)

                if len(max_scores) > num_scores:
                    max_scores.remove(max_scores[num_scores])

            prev_seq_score = c_score

        # Sorts max score list by position
        max_scores = sorted(max_scores, key=lambda k: k["position"])
        
        for max_score in max_scores:
            print(str(max_score))

        print("len(max_scores) = " + str(len(max_scores)))
        print("len(scores) = " + str(len(positions)))
        

        return max_scores

    def calc_sp_end_notes(self):
        sp_end_notes = []

        notes_pos = [note["position"] for note in self.chart.notes]
    
        for s in range(len(self.sp_phrases)):
            sp_end_note_i = bisect.bisect_right(notes_pos, self.sp_phrases[s]["position"] + \
            self.sp_phrases[s]["length"] - 1)

            sp_end_note_i = sp_end_note_i if sp_end_note_i < len(self.chart.notes) else len(self.chart.notes) - 1

            sp_end_notes.append(self.chart.notes[sp_end_note_i])    

        return sp_end_notes

    def can_activate_sp(self):
        return self.sp_bar >= self.sp_bar.length / 2

    def add_sp_activation(self, sp_activation):
        self.sp_activations.append(sp_activation)

    def set_basic_sp_path(self):


        pos = 0
        chart_length = self.chart.length

        c_number = 0

        while pos < chart_length:
            
            if pos >= self.sp_end_notes[0]["position"]:
                self.sp_bar.set(self.sp_bar.number + (self.sp_bar.length / 4)) 
                c_number += 1
                self.sp_end_notes.remove(self.sp_end_notes[0])
                

            if self.can_activate_sp():
                sp_activation = {
                    "position": pos,
                    "length": self.sp_bar.number
                }
                self.sp_bar = 0
                self.num_phrases.append(c_number)
                c_number = 0
                self.add_sp_activation(sp_activation)

            pos += self.chart.resolution

            if not self.sp_end_notes:
                    break

    def create_sp_graph(self):
        return

