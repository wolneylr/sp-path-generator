import cairocffi as cairo
import math
from main import Application

WIDTH = 1024
MEASURE_OFFSET = 40
LINE_OFFSET = 125

class Chart_Img():

    star_points = ( 
        ( 0, 85 ), 
        ( 75, 75 ), 
        ( 100, 10 ), 
        ( 125, 75 ), 
        ( 200, 85 ),
        ( 150, 125 ), 
        ( 160, 190 ),
        ( 100, 150 ), 
        ( 40, 190 ),
        ( 50, 125 ),
        ( 0, 85 )
    )

    def __init__(self, song, chart):
        self.song = song
        self.chart = chart
        self.c_y = 0

        self.line_length = WIDTH - MEASURE_OFFSET * 2

        self.measure_to_line = self.line_length / (self.song.resolution * 24)

        height = self.calculate_height()

        self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, height)
        self.cr = cairo.Context(self.ims)

        self.cr.set_source_rgb(1, 1, 1)
        self.cr.rectangle(0, 0, WIDTH, height)
        self.cr.fill()

        self.cr.set_source_rgb(0, 0, 0)
        self.cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

        self.c_y += 30

        self.cr.set_font_size(12)
        self.cr.move_to(MEASURE_OFFSET / 4, self.c_y)    
        self.cr.show_text("Base Chart")

        self.cr.set_font_size(18)
        (_, _, width, _, _, _) = self.cr.text_extents(self.song.name)
        self.cr.move_to(WIDTH / 2 - width / 2, self.c_y)    
        self.cr.show_text(self.song.name)

        self.c_y += 20

        self.cr.set_font_size(12) 
        (_, _, width, _, _, _) = self.cr.text_extents(chart.difficulty)
        self.cr.move_to(WIDTH / 2 - width / 2, self.c_y)   
        self.cr.show_text(chart.difficulty)

        self.c_y += 80

        self.draw_measures()

    def calculate_height(self):
        height = 130

        c_ts = 0
        self.c_measure_length = 0
        c_length = 0
        self.c_x = MEASURE_OFFSET
        

        chart_length = self.chart.notes[len(self.chart.notes) - 1]["position"] \
            + self.chart.notes[len(self.chart.notes) - 1]["length"]

        while c_length <= chart_length:
            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length:
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"] 

            if (self.c_measure_length + measure_length) * self.measure_to_line > self.line_length:
                self.c_x = MEASURE_OFFSET
                height += LINE_OFFSET
                self.c_measure_length = 0

            self.c_x += measure_length * self.measure_to_line
            c_length += measure_length
            self.c_measure_length += measure_length

        return height + LINE_OFFSET * 3
        

        

    def draw_note(self, x, y, color, length, star):
        self.cr.set_source_rgb(0.7, 0.7, 0.7)

        if star:
            for i in range(10):
                self.cr.line_to(self.star_points[i][0] / 25 + x, self.star_points[i][1] / 25 + y)
        else:
            self.cr.arc(x, y, 3, 0, 2 * math.pi)
            
        self.cr.stroke_preserve()

        if color == "green":
            self.cr.set_source_rgb(0, 1, 0)
        elif color == "red":
            self.cr.set_source_rgb(1, 0, 0)
        elif color == "yellow":
            self.cr.set_source_rgb(1, 1, 0)
        elif color == "blue":
            self.cr.set_source_rgb(0, 0.3, 1)
        elif color == "orange":
            self.cr.set_source_rgb(1, 0.7, 0)

        self.cr.fill()

        if length > 0:
            self.cr.move_to(x, y)
            '''
            if (self.c_measure_length + self.song.resolution * self.song.time_signatures[c_ts + 1]["beats"]) * \
                self.measure_to_line > self.line_length:
            '''
            self.cr.line_to(x + length * self.measure_to_line, y) 
            self.cr.stroke()

        

    def draw_vert_line(self, color, x):
        self.cr.set_source_rgb(color, color, color)
        self.cr.move_to(x, self.c_y)
        self.cr.line_to(x, self.c_y + self.notes_offset * 4) 
        self.cr.stroke()

    def draw_measures(self): 

        c_length = 0
        c_bpm = 0
        c_ts = -1
        self.c_measure_length = 0
        self.c_x = MEASURE_OFFSET

        self.notes_offset = 15
        measure_num_offset = 5

        measure_num = 1
        self.line_num = 0

        self.line_length = WIDTH - MEASURE_OFFSET * 2
        self.line_lengths = []

        show_ts = False

        chart_length = self.chart.notes[len(self.chart.notes) - 1]["position"] \
            + self.chart.notes[len(self.chart.notes) - 1]["length"]

        notes = self.chart.notes

        self.cr.set_line_width(2)

        while c_length <= chart_length:
            if c_ts <  len(self.song.time_signatures) - 1:
                if self.song.time_signatures[c_ts + 1]["position"] == c_length: 
                    show_ts = True
                    c_ts += 1

            measure_length = self.song.resolution * self.song.time_signatures[c_ts]["beats"]     

            if (self.c_measure_length + measure_length) * self.measure_to_line > self.line_length:
                self.line_lengths.append(self.c_measure_length * self.measure_to_line)

                self.draw_vert_line(0.7, self.c_x)

                self.c_x = MEASURE_OFFSET
                self.c_y += LINE_OFFSET
                self.c_measure_length = 0

                self.line_num += 1

            if show_ts:
                self.cr.set_source_rgb(0.6, 0.6, 0.6)     
                self.cr.set_font_size(24)

                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 2)
                self.cr.show_text(str(self.song.time_signatures[c_ts]["beats"]))
                self.cr.move_to(self.c_x, self.c_y + self.notes_offset * 3)
                self.cr.show_text("4")

                show_ts = False
            
            for i in range(5):

                if i == 0 or i == 4:
                    self.cr.set_source_rgb(0.6, 0.6, 0.6)
                else:
                    self.cr.set_source_rgb(0.7, 0.7, 0.7)

                self.cr.move_to(self.c_x, self.c_y)
                self.cr.line_to(self.c_x + measure_length * self.measure_to_line, self.c_y) 
                self.cr.stroke()
                self.c_y += self.notes_offset

            self.c_y -= self.notes_offset * 5

            self.cr.set_source_rgb(0.8, 0.2, 0.2)     
            self.cr.set_font_size(9)

            self.cr.move_to(self.c_x, self.c_y - measure_num_offset)
            self.cr.show_text(str(measure_num))

            measure_num += 1  

            c_beat = self.song.resolution * self.measure_to_line     

            for i in range(self.song.time_signatures[c_ts]["beats"]):  
                if i == 0:
                    self.draw_vert_line(0.7, self.c_x + i * c_beat)
                else:
                    self.draw_vert_line(0.9, self.c_x + i * c_beat)   

            str_notes = ["green", "red", "yellow", "blue", "orange"]


            if len(notes) > 10:             
                while notes[0]["position"] < c_length + measure_length:               
                    note_pos = notes[0]["position"] * self.measure_to_line - sum(self.line_lengths)

                    self.draw_note(MEASURE_OFFSET + note_pos, self.c_y + notes[0]["number"] * self.notes_offset, \
                        str_notes[notes[0]["number"]], notes[0]["length"], False)

                    notes.remove(notes[0])    

            self.c_x += measure_length * self.measure_to_line
            c_length += measure_length
            self.c_measure_length += measure_length

        self.draw_vert_line(0.7, self.c_x)

        self.ims.write_to_png("chart.png")

def main():
    app = Application()
    app.read_chart("Chart Examples/mikeorlando.chart")

    Chart_Img(app.song, app.song.charts[0])


if __name__ == "__main__":
    main()