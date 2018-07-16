import math
import bisect

class SP_Path:

    SP_BAR_BEATS = 32

    def __init__(self, chart):
        self.chart = chart
        self.sp_phrases = self.chart.sp_phrases
        self.num_activations = int(len(self.sp_phrases) / 2)     

        self.sp_bar = 0
        self.sp_bar_length = self.chart.resolution * self.SP_BAR_BEATS

        self.sp_end_notes = []
        self.add_sp_end_notes()

        self.beat_scores = []
        #self.add_beat_scores()

        self.pos_scores = []
        self.add_pos_scores()

        self.max_score_lengths = self.calc_largest_scores(self.pos_scores, 
        int(self.sp_bar_length / 2), self.num_activations, 1)   

        self.sp_activations = []
        self.num_phrases = []
        #self.set_basic_sp_path()

    def add_pos_scores(self): 

        c_length = 0
    
        pos_length = 1

        chart_length = self.chart.length

        c_multiplier = 1

        notes = self.chart.notes
        n = 0
        sustain_lengths = []

        pos_score = 0

        while c_length <= chart_length:
            c_length += pos_length

            pos_score = 0

            if sustain_lengths:
                for i in range(len(sustain_lengths)):
                    length_score = self.chart.NOTE_SCORE / 2 * c_multiplier / self.chart.resolution

                    sustain_lengths[i] -= pos_length          

                    pos_score += length_score 

                    if sustain_lengths[i] == 0:
                        pos_score = int(math.ceil(pos_score))
                # Removes notes with empty length
                for i in range(len(sustain_lengths)):
                    if i >= len(sustain_lengths):
                        break

                    if sustain_lengths[i] == 0:
                        sustain_lengths.remove(sustain_lengths[i])       

            if n < len(notes): 
                while notes[n]["position"] < c_length:    

                    if c_multiplier < 4:
                        c_multiplier = self.chart.calc_note_multiplier(self.chart.calc_unote_index(notes[n])) 

                    pos_score += self.chart.NOTE_SCORE * c_multiplier  

                    if notes[n]["length"] > 0 and self.chart.is_unique_note(notes[n]):  
                        length_score = self.chart.NOTE_SCORE / 2 * c_multiplier / self.chart.resolution      

                        pos_score += length_score 

                        if notes[n]["length"] == pos_length:  
                            pos_score = int(math.ceil(pos_score))                         

                    n += 1
                    
                    if n == len(notes):
                        break
                        
                self.pos_scores.append(pos_score) 

    def add_beat_scores(self): 

            c_length = 0
        
            beat_length = self.chart.resolution

            chart_length = self.chart.length

            c_multiplier = 1

            notes = self.chart.notes
            n = 0
            sustain_lengths = []

            beat_score = 0

            while c_length <= chart_length:
                c_length += beat_length

                beat_score = 0

                if sustain_lengths:
                    for i in range(len(sustain_lengths)):
                        if sustain_lengths[i] > beat_length:
                        
                            length_score = self.chart.NOTE_SCORE / 2 * c_multiplier
                            length_score = int(math.ceil(length_score))
                            # length_score = round(length_score)
                            # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))         

                            sustain_lengths[i] -= beat_length       

                        else:    
                            length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * \
                                sustain_lengths[i] / beat_length
                            length_score = int(math.ceil(length_score))
                            # length_score = round(length_score)
                            # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                            sustain_lengths[i] = 0   

                        beat_score += length_score 
                    # Removes notes with empty length
                    for i in range(len(sustain_lengths)):
                        if i >= len(sustain_lengths):
                            break

                        if sustain_lengths[i] == 0:
                            sustain_lengths.remove(sustain_lengths[i])       

                if n < len(notes): 
                    while notes[n]["position"] < c_length:    

                        if c_multiplier < 4:
                            c_multiplier = self.chart.calc_note_multiplier(self.chart.calc_unote_index(notes[n])) 

                        beat_score += self.chart.NOTE_SCORE * c_multiplier  

                        if notes[n]["length"] > 0 and self.chart.is_unique_note(notes[n]):                         
                            if notes[n]["length"] > beat_length:
                                length_score = self.chart.NOTE_SCORE / 2 * c_multiplier     
                                length_score = int(math.ceil(length_score))
                                # length_score = round(length_score)
                                # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                                sustain_note_length = notes[n]["length"]

                                sustain_note_length -= beat_length

                                sustain_lengths.append(sustain_note_length)                           
                                
                            else:
                                length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * \
                                notes[n]["length"] / beat_length
                                
                                length_score = int(math.ceil(length_score))
                                # length_score = round(length_score)
                                # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                            beat_score += length_score 

                        n += 1
                        
                        if n == len(notes):
                            break
                            
                    self.beat_scores.append(beat_score) 

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
    def calc_largest_scores(self, scores, length, num_scores, distance):
        overlapping_lengths = False

        prev_seq_score = 0

        for i in range(length):
            prev_seq_score += scores[i]

        start_i_final = 0

        end_i_final = length - 1

        max_score = {
            "score": prev_seq_score,
            "position": start_i_final * distance,
            "length": (end_i_final - start_i_final + 1) * distance
        }

        max_scores = [max_score]

        c_score = 0

        for i in range(length, len(scores)):
            c_score = prev_seq_score + scores[i] - scores[i - length]
            
            max_scores_scores = [max_score["score"] for max_score in max_scores]

            score_index = self.reverse_bisect_right(max_scores_scores, c_score)

            end_i_final = i
            start_i_final = i - length + 1

            c_max_score = {
                "score": c_score,
                "position": start_i_final * distance,
                "length": (end_i_final - start_i_final + 1) * distance
            }

            insert_length = True
            
            # Only insert length if length's starting position is bigger than first activation position
            if len(self.sp_end_notes) > 1:
                if (i - length + 1) * distance < self.sp_end_notes[1]["position"]:
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
        print("len(scores) = " + str(len(scores)))

        return max_scores

    def add_sp_end_notes(self):

        notes_pos = [note["position"] for note in self.chart.notes]
    
        for s in range(len(self.sp_phrases)):
            self.sp_end_notes.append(self.chart.notes[bisect.bisect_right(
            notes_pos, self.sp_phrases[s]["position"] + self.sp_phrases[s]["length"] - 1)])    

    def can_activate_sp(self):
        return self.sp_bar >= self.sp_bar_length / 2

    def add_sp_activation(self, sp_activation):
        self.sp_activations.append(sp_activation)

    def set_basic_sp_path(self):

        pos = 0
        chart_length = self.chart.length

        c_number = 0

        while pos < chart_length:
            
            if pos >= self.sp_end_notes[0]["position"]:
                self.sp_bar += self.chart.resolution * self.SP_BAR_BEATS / 4
                c_number += 1
                self.sp_end_notes.remove(self.sp_end_notes[0])
                

            if self.can_activate_sp():
                sp_activation = {
                    "position": pos,
                    "length": self.sp_bar
                }
                self.sp_bar = 0
                self.num_phrases.append(c_number)
                c_number = 0
                self.add_sp_activation(sp_activation)

            pos += self.chart.resolution

            if not self.sp_end_notes:
                    break

