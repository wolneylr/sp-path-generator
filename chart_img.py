import math
from decimal import Decimal, ROUND_HALF_UP

import cairocffi as cairo

from main import Application

class Chart_Img():

    WIDTH = 1024
    MEASURE_OFFSET = 40
    MEASURE_HEIGHT = 125
    EPSILON = 0.001
    NOTE_RADIUS = 3
    STAR_SCALE = 30
    MAX_LINES = 200
    MAX_HEIGHT = MEASURE_HEIGHT * MAX_LINES

    STAR_POINTS = ((0, 85), (75, 75), (100, 10),
        (125, 75), (200, 85), (150, 125), (160, 190),
        (100, 150), (40, 190), (50, 125), (0, 85))

    NOTE_COLORS = [
        [0, 0.9, 0], 
        [1, 0, 0], 
        [1, 1, 0],
        [0, 0.3, 1],
        [1, 0.7, 0],
        [1, 0, 1]
    ]

    SP_PHRASE_COLOR = [0, 0.7, 0]
    SP_PHRASE_ALPHA = 0.4

    SOLO_SECTION_COLOR = [0.7, 0.7, 0]
    SOLO_SECTION_ALPHA = 0.4

    SP_ACTIVATION_COLOR = [0, 0, 1]
    SP_ACTIVATION_ALPHA = 0.4

    def __init__(self, song, chart):
        self.song = song
        self.chart = chart
        self.c_y = 0

        self.chart.add_sp_path()

        self.chart.add_solo_end_notes()

        self.notes = self.chart.notes

        self.chart_length = self.notes[len(self.notes) - 1]["position"] + \
        self.notes[len(self.notes) - 1]["length"]

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2

        self.m2l = self.line_length / (self.song.resolution * 24)

        self.height = self.calculate_height()

        self.num_pages = math.floor(self.height / self.MAX_HEIGHT) + 1

        self.imss = []
        self.crs = []   
        self.c_cr = 0

        for page in range(self.num_pages):         
                     
            if self.height < self.MAX_HEIGHT:
                page_height = self.height + (110 if page == 0 else 60)
            else:
                page_height = self.MAX_HEIGHT + (110 if page == 0 else 60)

            self.imss.append(cairo.ImageSurface(cairo.FORMAT_ARGB32, self.WIDTH, page_height))
            self.crs.append(cairo.Context(self.imss[page]))

            self.crs[page].set_source_rgb(1, 1, 1)  
            self.crs[page].rectangle(0, 0, self.WIDTH, page_height)
            self.crs[page].fill()

            self.crs[page].set_source_rgb(0, 0, 0)
            self.crs[page].select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

            self.height -= self.MAX_HEIGHT

        self.c_y += 30

        str_charter = "Charter: " + self.song.charter
        self.crs[0].set_font_size(12)
        (_, _, width, _, _, _) = self.crs[0].text_extents(str_charter)
        self.crs[0].move_to(self.MEASURE_OFFSET / 4, self.c_y)    
        self.crs[0].show_text(str_charter)

        self.crs[0].set_font_size(18)
        (_, _, width, _, _, _) = self.crs[0].text_extents(self.song.name)
        self.crs[0].move_to(self.WIDTH / 2 - width / 2, self.c_y)    
        self.crs[0].show_text(self.song.name)

        self.crs[0].set_font_size(12) 
        str_path = "Path: " + "-".join([str(num) for num in self.chart.sp_path.num_phrases])
        (_, _, width, _, _, _) = self.crs[0].text_extents(str_path)

        if width > self.WIDTH / 3:
            self.crs[0].move_to(self.WIDTH - self.WIDTH / 3 - self.MEASURE_OFFSET / 4, self.c_y)   
        else: 
            self.crs[0].move_to(self.WIDTH - width - self.MEASURE_OFFSET / 4, self.c_y)     
        
        self.crs[0].show_text(str_path)

        self.c_y += 20 
        (_, _, width, _, _, _) = self.crs[0].text_extents(song.DIFFICULTIES[chart.difficulty])
        self.crs[0].move_to(self.WIDTH / 2 - width / 2, self.c_y)   
        self.crs[0].show_text(song.DIFFICULTIES[chart.difficulty])

        est_score = "Est. Score: " + str(math.floor(self.chart.calculate_score(0, len(self.chart.notes), 
            self.song.time_signatures, True)))
        (_, _, width, _, _, _) = self.crs[0].text_extents(est_score)
        self.crs[0].move_to(self.WIDTH - width - self.MEASURE_OFFSET / 4, self.c_y)   
        self.crs[0].show_text(est_score)

        self.c_y += 60

        self.draw_chart(False)
        self.draw_chart(True)

        if __name__ == "__main__":
            for page in range(self.num_pages):
                self.imss[page].write_to_png("assets/Chart Images/" + self.song.name.lower().replace(" ", "") + \
                    (str(page + 1) if self.num_pages > 1 else "") + ".png")

    def calculate_height(self):
        height = 0

        c_ts = 0
        c_length = 0

        self.c_x = self.MEASURE_OFFSET      
        self.c_measure_length = 0

        while c_length <= self.chart_length:
            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length:
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"] 

            if (self.c_measure_length + measure_length) * self.m2l > self.line_length:
                self.c_x = self.MEASURE_OFFSET
                height += self.MEASURE_HEIGHT
                self.c_measure_length = 0

            self.c_x += measure_length * self.m2l
            c_length += measure_length
            self.c_measure_length += measure_length

        return height + self.MEASURE_HEIGHT

    def draw_note(self, x, y, color, star):
        
        if color == 7:
            color = 5

        self.crs[self.c_cr].set_source_rgb(0.7, 0.7, 0.7)

        if star:
            # Open note
            if color == 5:
                for i in range(10):
                    self.crs[self.c_cr].line_to(self.STAR_POINTS[i][0] / (self.STAR_SCALE + 5) + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / (self.STAR_SCALE + 5) + y - self.NOTE_RADIUS - 2 * self.notes_offset)   
                self.crs[self.c_cr].stroke_preserve()    
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], 
                self.NOTE_COLORS[color][2])
                self.crs[self.c_cr].fill()

                self.crs[self.c_cr].set_source_rgb(0.7, 0.7, 0.7)
                for i in range(10):
                    self.crs[self.c_cr].line_to(self.STAR_POINTS[i][0] / (self.STAR_SCALE + 5) + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / (self.STAR_SCALE + 5) + y - self.NOTE_RADIUS + 2 * self.notes_offset)  
                self.crs[self.c_cr].stroke_preserve()      
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], 
                self.NOTE_COLORS[color][2])
                self.crs[self.c_cr].fill()

                self.crs[self.c_cr].rectangle(x - (self.NOTE_RADIUS - self.NOTE_RADIUS / 3), 
                y - 2 * self.notes_offset, self.NOTE_RADIUS + self.NOTE_RADIUS / 3, 4 * self.notes_offset)
            else:
                for i in range(10):
                    self.crs[self.c_cr].line_to(self.STAR_POINTS[i][0] / self.STAR_SCALE + x - self.NOTE_RADIUS, 
                    self.STAR_POINTS[i][1] / self.STAR_SCALE + y - self.NOTE_RADIUS)   
                self.crs[self.c_cr].stroke_preserve()      
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], 
                self.NOTE_COLORS[color][2])
        else:
            # Open note
            if color == 5:          
                self.crs[self.c_cr].arc(x, y - 2 * self.notes_offset, 
                self.NOTE_RADIUS - self.NOTE_RADIUS / 3, 0, 2 * math.pi)
                self.crs[self.c_cr].stroke_preserve()
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1],
                 self.NOTE_COLORS[color][2])
                self.crs[self.c_cr].fill()

                self.crs[self.c_cr].set_source_rgb(0.7, 0.7, 0.7)
                self.crs[self.c_cr].arc(x, y + 2 * self.notes_offset, 
                self.NOTE_RADIUS - self.NOTE_RADIUS / 3, 0, 2 * math.pi)
                self.crs[self.c_cr].stroke_preserve()
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], 
                self.NOTE_COLORS[color][2])
                self.crs[self.c_cr].fill()
                
                self.crs[self.c_cr].rectangle(x - (self.NOTE_RADIUS - self.NOTE_RADIUS / 3), 
                y - 2 * self.notes_offset, self.NOTE_RADIUS + self.NOTE_RADIUS / 3, 4 * self.notes_offset)
            else:
                self.crs[self.c_cr].arc(x, y, self.NOTE_RADIUS, 0, 2 * math.pi)
                self.crs[self.c_cr].stroke_preserve()      
                self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[color][0], self.NOTE_COLORS[color][1], 
                self.NOTE_COLORS[color][2])
                '''
                self.crs[self.c_cr].fill()
                self.crs[self.c_cr].arc(x, y, self.NOTE_RADIUS / 3, 0, 2 * math.pi)
                self.crs[self.c_cr].stroke_preserve()      
                self.crs[self.c_cr].set_source_rgb(0.8, 0.8, 0.8)
                '''

        self.crs[self.c_cr].fill()

    def draw_vert_line(self, color, x):
        self.crs[self.c_cr].set_source_rgb(color, color, color)
        self.crs[self.c_cr].move_to(x, self.c_y)
        self.crs[self.c_cr].line_to(x, self.c_y + self.notes_offset * 4) 
        self.crs[self.c_cr].stroke()

    def draw_remaining_section(self, length, color, alpha):
        if length == 0:
            return length

        self.crs[self.c_cr].set_source_rgba(color[0], color[1], color[2], alpha)

        if length > self.measure_length * self.m2l:
            self.crs[self.c_cr].rectangle(self.c_x, self.c_y, self.measure_length * self.m2l, 4 * self.notes_offset)
            length -= self.measure_length * self.m2l               
        else:
            self.crs[self.c_cr].rectangle(self.c_x, self.c_y, length, 4 * self.notes_offset) 
            length = 0

        self.crs[self.c_cr].fill()      
        self.crs[self.c_cr].set_source_rgba(0.7, 0.7, 0.7, 1)  

        return length

    def draw_section(self, sections, i, length, color, alpha):
        if i < len(sections):
            while sections[i]["position"] < self.c_length:  
                line_pos = sections[i]["position"] * self.m2l - sum(self.line_lengths)

                x = self.MEASURE_OFFSET + line_pos

                self.crs[self.c_cr].move_to(x, self.c_y)

                length_pos = x + sections[i]["length"] * self.m2l

                measure_pos = self.MEASURE_OFFSET + self.c_length * self.m2l - sum(self.line_lengths)
                    
                self.crs[self.c_cr].set_source_rgba(color[0], color[1], color[2], alpha)

                if length_pos > measure_pos:             
                    self.crs[self.c_cr].rectangle(x, self.c_y, measure_pos - x, 4 * self.notes_offset) 
                    length = length_pos - measure_pos
                else:
                    self.crs[self.c_cr].rectangle(x, self.c_y, length_pos - x, 4 * self.notes_offset)            

                self.crs[self.c_cr].fill()      
                self.crs[self.c_cr].set_source_rgba(0.7, 0.7, 0.7, 1)   


                i += 1

                if i == len(sections):
                    break       

        return i, length   

    def draw_chart(self, draw_notes): 

        self.c_length = 0
        c_ts = -1
        
        self.c_measure_length = 0
        self.c_x = self.MEASURE_OFFSET
        self.c_y = 110

        self.notes_offset = 15
        measure_num_offset = 5

        measure_num = 0
        self.line_num = 0

        self.line_length = self.WIDTH - self.MEASURE_OFFSET * 2
        self.line_lengths = []

        show_ts = False

        n = 0
        sustain_notes = []

        bpms = self.song.bpms
        b = 0

        sections = self.song.sections
        s = 0

        sp_phrases = self.chart.sp_phrases
        sp = 0
        sp_phrase_length = 0

        solo_sections = self.chart.solo_sections
        sl = 0    
        solo_section_length = 0
      
        sp_activations = self.chart.sp_path.sp_activations
        sa = 0    
        sp_activation_length = 0

        c_score = 0
        c_solo_score = 0
        c_multiplier = 1

        for cr in self.crs:
            cr.set_line_width(2)

        self.c_cr = 0
        self.c_y = 110

        while self.c_length <= self.chart_length:

            measure_num += 1  
            measure_score = 0      
            
            # Checks if time signature changes
            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == self.c_length: 
                    show_ts = True
                    c_ts += 1

            self.measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"]             
            # Go to next line if the line length reaches the max line length
            if (self.c_measure_length + self.measure_length) * self.m2l - self.line_length > self.EPSILON:  
                self.line_lengths.append(self.c_measure_length * self.m2l)
                
                if not draw_notes:
                    self.draw_vert_line(0.7, self.c_x)

                self.c_x = self.MEASURE_OFFSET
                self.c_y += self.MEASURE_HEIGHT
                self.c_measure_length = 0

                self.line_num += 1       

                # Go to next page if the number of lines reaches the max number of lines per page
                if self.line_num % self.MAX_LINES == 0:
                    self.c_cr += 1
                    self.c_y = 60

            self.c_length += self.measure_length
            self.c_measure_length += self.measure_length         

            if not draw_notes: 
                # Draws the time signature if it changes
                if show_ts:
                    self.crs[self.c_cr].select_font_face("Arial Black", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    self.crs[self.c_cr].set_source_rgb(0.8, 0.8, 0.8)     
                    self.crs[self.c_cr].set_font_size(24)

                    self.crs[self.c_cr].move_to(self.c_x, self.c_y + self.notes_offset * 2)
                    self.crs[self.c_cr].show_text(str(self.song.time_signatures[c_ts]["beats"]))
                    self.crs[self.c_cr].move_to(self.c_x, self.c_y + self.notes_offset * 3.2)
                    self.crs[self.c_cr].show_text("4")

                    show_ts = False

                # Draws the measure number
                self.crs[self.c_cr].select_font_face("Calibri", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                self.crs[self.c_cr].set_source_rgb(0.8, 0.2, 0.2)    
                self.crs[self.c_cr].set_font_size(9)
                self.crs[self.c_cr].move_to(self.c_x, self.c_y - measure_num_offset)
                self.crs[self.c_cr].show_text(str(measure_num))                            

                # Draws the vertical lines         
                c_beat = self.song.resolution * self.m2l  
                for i in range(self.song.time_signatures[c_ts]["beats"]):  
                    if i == 0:
                        self.draw_vert_line(0.7, self.c_x + i * c_beat)
                    else:
                        self.draw_vert_line(0.9, self.c_x + i * c_beat)   

                # Draws the horizontal lines
                for i in range(5):
                    if i == 0 or i == 4:
                        self.crs[self.c_cr].set_source_rgb(0.6, 0.6, 0.6)
                    else:
                        self.crs[self.c_cr].set_source_rgb(0.7, 0.7, 0.7)

                    self.crs[self.c_cr].move_to(self.c_x, self.c_y)
                    self.crs[self.c_cr].line_to(self.c_x + self.measure_length * self.m2l, self.c_y) 
                    self.crs[self.c_cr].stroke()
                    self.c_y += self.notes_offset

                self.c_y -= self.notes_offset * 5

                # Draws bpms in measure
                self.crs[self.c_cr].set_source_rgb(0, 0, 0)   
                self.crs[self.c_cr].set_font_size(9)  
                if b < len(bpms):
                    while bpms[b]["position"] < self.c_length:  
                        bpm_pos = bpms[b]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + bpm_pos

                        self.crs[self.c_cr].move_to(x, self.c_y - measure_num_offset * 3)

                        str_bpm = "t=" + str(bpms[b]["value"])
                        self.crs[self.c_cr].show_text(str_bpm)

                        b += 1

                        if b == len(bpms):
                            break  

                # Draws sections in measure 
                self.crs[self.c_cr].set_font_size(11)  
                if s < len(sections):
                    while sections[s]["position"] < self.c_length:  
                        section_pos = sections[s]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + section_pos

                        self.crs[self.c_cr].move_to(x, self.c_y - measure_num_offset * 5)

                        self.crs[self.c_cr].show_text(sections[s]["name"])

                        s += 1

                        if s == len(sections):
                            break  

                # Draws remaining star power phrase length from last measure
                sp_phrase_length = self.draw_remaining_section(sp_phrase_length, 
                self.SP_PHRASE_COLOR, self.SP_PHRASE_ALPHA)      
                # Draws remaining solo section length from last measure
                solo_section_length = self.draw_remaining_section(solo_section_length, 
                self.SOLO_SECTION_COLOR, self.SOLO_SECTION_ALPHA)
                # Draws remaining sp activation length from last measure
                sp_activation_length = self.draw_remaining_section(sp_activation_length, 
                self.SP_ACTIVATION_COLOR, self.SP_ACTIVATION_ALPHA)

                # Draws star power phrases in measure 
                sp, sp_phrase_length = self.draw_section(sp_phrases, sp, sp_phrase_length,
                self.SP_PHRASE_COLOR, self.SP_PHRASE_ALPHA)
                # Draws solo sections in measure 
                sl, solo_section_length = self.draw_section(solo_sections, sl, solo_section_length,
                self.SOLO_SECTION_COLOR, self.SOLO_SECTION_ALPHA)
                # Draws sp activations in measure 
                sa, sp_activation_length = self.draw_section(sp_activations, sa, sp_activation_length,
                self.SP_ACTIVATION_COLOR, self.SP_ACTIVATION_ALPHA)
            else:   
                # Draws remaining note length from last measure
                if sustain_notes:
                    for i in range(len(sustain_notes)):

                        num = sustain_notes[i]["number"]

                        self.crs[self.c_cr].set_source_rgb(self.NOTE_COLORS[num][0], self.NOTE_COLORS[num][1], \
                            self.NOTE_COLORS[num][2])
                        self.crs[self.c_cr].move_to(self.c_x, self.c_y + num * self.notes_offset)

                        if sustain_notes[i]["length"] > self.measure_length:
                            line_length = self.measure_length * self.m2l
                            # Open note
                            if num == 5:
                                self.crs[self.c_cr].set_source_rgba(1, 0, 1, 0.5)
                                self.crs[self.c_cr].rectangle(self.c_x, self.c_y, line_length, 4 * self.notes_offset) 
                                self.crs[self.c_cr].fill()      
                                self.crs[self.c_cr].set_source_rgba(1, 0, 1, 1)   
                            else:
                                self.crs[self.c_cr].line_to(self.c_x + line_length, self.c_y + num * self.notes_offset) 
                                self.crs[self.c_cr].stroke()   

                            if self.chart.is_unique_note(sustain_notes[i]):    
                                length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * self.measure_length / self.song.resolution
                                length_score = int(math.ceil(length_score))
                                # length_score = round(length_score)
                                # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                                measure_score += length_score
                                c_score += length_score

                            sustain_notes[i]["length"] -= self.measure_length       

                        else:
                            line_length = sustain_notes[i]["length"] * self.m2l
                            # Open note
                            if num == 5:
                                self.crs[self.c_cr].set_source_rgba(1, 0, 1, 0.5)
                                self.crs[self.c_cr].rectangle(self.c_x, self.c_y, line_length, 4 * \
                                    self.notes_offset) 
                                self.crs[self.c_cr].fill()
                                self.crs[self.c_cr].set_source_rgba(1, 0, 1, 1)   
                            else:
                                self.crs[self.c_cr].line_to(self.c_x + line_length, self.c_y + num * \
                                    self.notes_offset) 
                                self.crs[self.c_cr].stroke()

                            if self.chart.is_unique_note(sustain_notes[i]):    
                                length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * \
                                    sustain_notes[i]["length"] / self.song.resolution
                                length_score = int(math.ceil(length_score))
                                # length_score = round(length_score)
                                # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                                measure_score += length_score
                                c_score += length_score

                            sustain_notes[i]["length"] = 0           
                        
                    # Removes notes with empty length
                    for i in range(len(sustain_notes)):
                        if i >= len(sustain_notes):
                            break

                        if sustain_notes[i]["length"] == 0:
                            sustain_notes.remove(sustain_notes[i])
                
                # Draws notes in measure  
                measure_pos = self.MEASURE_OFFSET + self.c_length * self.m2l - sum(self.line_lengths)     

                if n < len(self.notes): 
                    while self.notes[n]["position"] < self.c_length:               
                        note_line_pos = self.notes[n]["position"] * self.m2l - sum(self.line_lengths)

                        x = self.MEASURE_OFFSET + note_line_pos
                        y = self.c_y + (2 if self.notes[n]["number"] == 7 else self.notes[n]["number"]) * self.notes_offset 

                        self.chart.sp, pos_in_phrase = self.chart.pos_in_section(self.chart.sp, 
                        self.chart.sp_phrases, self.notes[n]["position"])

                        self.crs[self.c_cr].move_to(x, y)
                        self.draw_note(x, y, self.notes[n]["number"], pos_in_phrase)               

                        if c_multiplier < 4:
                            c_multiplier = self.chart.calc_note_multiplier(self.chart.calc_unote_index(self.notes[n]))

                        # Score
                        measure_score += self.chart.NOTE_SCORE * c_multiplier
                        c_score += self.chart.NOTE_SCORE * c_multiplier

                        self.chart.sl, pos_in_solo = self.chart.pos_in_section(self.chart.sl, 
                        self.chart.solo_sections, self.notes[n]["position"])
                        self.chart.sa, pos_in_path = self.chart.pos_in_section(self.chart.sa, 
                        self.chart.sp_path.sp_activations, self.notes[n]["position"])

                        if pos_in_solo:
                            c_solo_score += self.chart.NOTE_SCORE * c_multiplier / 2

                            if self.notes[n] in self.chart.solo_end_notes:
                                measure_score += c_solo_score
                                c_score += c_solo_score
                                c_solo_score = 0                  

                        if pos_in_path:
                            measure_score += self.chart.NOTE_SCORE * c_multiplier
                            c_score += self.chart.NOTE_SCORE * c_multiplier

                        if self.notes[n]["length"] > 0: 
                            self.crs[self.c_cr].move_to(x, y)                                     

                            length_pos = x + self.notes[n]["length"] * self.m2l                             
                            
                            if length_pos > measure_pos:
                                # Open note
                                if self.notes[n]["number"] == 7:
                                    self.crs[self.c_cr].set_source_rgba(1, 0, 1, 0.5)
                                    self.crs[self.c_cr].rectangle(x, self.c_y, measure_pos - x, 4 * self.notes_offset) 
                                    self.crs[self.c_cr].fill()      
                                    self.crs[self.c_cr].set_source_rgba(1, 0, 1, 1)     
                                else:
                                    self.crs[self.c_cr].line_to(measure_pos, y) 
                                    self.crs[self.c_cr].stroke()

                                if self.chart.is_unique_note(self.notes[n]):     
                                    note_measure_length = (measure_pos - x) / self.m2l

                                    length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * \
                                    note_measure_length / self.song.resolution      

                                    length_score = int(math.ceil(length_score))
                                    # length_score = round(length_score)
                                    # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                                    measure_score += length_score
                                    c_score += length_score    

                                self.notes[n]["length"] -= note_measure_length

                                sustain_notes.append(self.notes[n])                           
                                
                            else:
                                # Open note
                                if self.notes[n]["number"] == 7:
                                    self.crs[self.c_cr].set_source_rgba(1, 0, 1, 0.5)
                                    self.crs[self.c_cr].rectangle(x, self.c_y, length_pos - x, 4 * self.notes_offset) 
                                    self.crs[self.c_cr].fill()
                                    self.crs[self.c_cr].set_source_rgba(1, 0, 1, 1)   
                                else:
                                    self.crs[self.c_cr].line_to(length_pos, y)   
                                    self.crs[self.c_cr].stroke()  

                                if self.chart.is_unique_note(self.notes[n]):     
                                    length_score = self.chart.NOTE_SCORE / 2 * c_multiplier * self.notes[n]["length"] \
                                        / self.song.resolution 
                                    
                                    length_score = int(math.ceil(length_score))
                                    # length_score = round(length_score)
                                    # length_score = int(Decimal(length_score).quantize(0, ROUND_HALF_UP))

                                    measure_score += length_score
                                    c_score += length_score
                              
                        n += 1

                        if n == len(self.notes):
                            break     
                    
                # Draws measure score
                self.crs[self.c_cr].set_source_rgb(0.5, 0.5, 0.5)  
                str_measure_score = str(math.floor(measure_score))
                (_, _, width, _, _, _) = self.crs[self.c_cr].text_extents(str_measure_score)
                self.crs[self.c_cr].move_to(measure_pos - width, self.c_y + 5 * self.notes_offset)   
                self.crs[self.c_cr].show_text(str_measure_score)   
                # Draws current score
                self.crs[self.c_cr].set_source_rgb(self.SP_PHRASE_COLOR[0], self.SP_PHRASE_COLOR[1], self.SP_PHRASE_COLOR[2])  
                str_c_score = str(math.floor(c_score))
                (_, _, width, _, _, _) = self.crs[self.c_cr].text_extents(str_c_score)
                self.crs[self.c_cr].move_to(measure_pos - width, self.c_y + 5.75 * self.notes_offset)   
                self.crs[self.c_cr].show_text(str_c_score)   

            self.c_x += self.measure_length * self.m2l 

        if not draw_notes:
            self.draw_vert_line(0.8, self.c_x)


def main():
    app = Application()
    app.read_chart_file("E:/WOLNEY JR/Guitar Hero/Songs/Yenlow73's Setlist/Dire Straits - Your Latest Trick (Live)/notes.chart")
    #app.read_chart_file("assets/Chart Examples/ttfaf.chart")

    Chart_Img(app.song, app.song.charts[0])


if __name__ == "__main__":
    main()
