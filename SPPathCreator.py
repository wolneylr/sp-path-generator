import math
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfile

class Song:

    NOTE_SCORE = 50
    MY_HEART_SCORE = 78762
    BROKED_SCORE = 61950
    KILLING_SCORE = 393643

    def __init__(self, name, resolution=192):
        self.name = name if name != "" else "Unknown"
        self.notes = []
        self.sp_phrases = []
        self.measure_length = resolution * 4

    def add_note(self, note):
        self.notes.append(note)

    def add_sp_phrase(self, sp_phrase):
        self.sp_phrases.append(sp_phrase)

    def total_chords(self):
        notes_count = 0

        for note in range(0, len(self.notes)):
            if note == 0:
                notes_count += 1
            elif self.notes[note]["position"] != self.notes[note - 1]["position"]:
                notes_count += 1

        return notes_count

    def base_score(self, note_length):
        score = 0
        multiplier = 1
        unique_note_index = 0

        for note in range(0, len(self.notes)):
            unique_note = False

            if note == 0:
                unique_note = True
            elif self.notes[note]["position"] != self.notes[note - 1]["position"]:
                unique_note = True

            if unique_note is True:
                unique_note_index += 1
                if unique_note_index > 30:
                    multiplier = 4
                else:
                    multiplier = math.floor(unique_note_index / 10) + 1

            score += self.NOTE_SCORE * multiplier

            if note_length is True and self.notes[note]["length"] > 0 and unique_note is True:
                score += self.NOTE_SCORE * 2 * multiplier * self.notes[note]["length"] / self.measure_length

            """
            if note < len(self.notes) - 1:# and unique_note_index < 500:
                if self.notes[note]["position"] != self.notes[note + 1]["position"]:
                    print(str(unique_note_index) + " - " + str(score))
                    """

        return score

    def avg_multiplier(self):
        song_length = self.notes[len(self.notes) - 1]["position"] + \
         self.notes[len(self.notes) - 1]["length"]

        sum_multiplier = 0
        multiplier = 1

        for position in range(0, song_length):
            if position > 30:
                multiplier = 4
            else:
                multiplier = math.floor(position / 10) + 1

            sum_multiplier += multiplier

        return sum_multiplier / song_length



class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = tk.Frame(self, width=480, height=360)
        self.frame.pack()
        self.title("SPPathCreator")
        #self.iconbitmap("gh1.ico")
        self.create_widgets()

    def on_open(self):
        self.file_name = askopenfilename(filetypes=(('Chart files', '*.chart'), \
            ("All files", "*.*")))

        if self.file_name:
            self.read_chart(self.file_name)



    def read_chart(self, file_name):
        self.file_chart = open(file_name, "r")
        self.str_chart = self.file_chart.read().splitlines()
        self.file_chart.close()

        self.song_name = str([line for line in self.str_chart if "Name = " in line])
        self.song_name = self.song_name[len("['  Name = \"") : len(self.song_name) - 3]

        self.song_resolution = str([line for line in self.str_chart if "Resolution = " in line])
        self.song_resolution = self.song_resolution[len("['  Resolution = ") : \
            len(self.song_resolution) - 2]

        self.song = Song(self.song_name, int(self.song_resolution))

        self.str_notes = [line for line in self.str_chart if " = N " in line]

        for str_note in self.str_notes:
            note_list = str_note.split()
            note = {}
            if int(note_list[3]) < 5 or int(note_list[3]) == 7:
                note_list.pop(1)
                note_list.pop(1)
                note["position"] = int(note_list[0])
                note["number"] = int(note_list[1])
                note["length"] = int(note_list[2])
                self.song.add_note(note)

        self.str_sp_phrases = [line for line in self.str_chart if " = S 2 " in line]

        
        for str_sp_phrase in self.str_sp_phrases:
            sp_phrase_list = str_sp_phrase.split()
            sp_phrase = {}
            sp_phrase_list.pop(1)
            sp_phrase_list.pop(1)
            sp_phrase_list.pop(1)
            sp_phrase["position"] = int(note_list[0])
            sp_phrase["length"] = int(note_list[1])

            self.song.add_sp_phrase(sp_phrase)

        self.song_details_text = "Name: " + self.song.name + "\n"
        self.song_details_text += "Resolution: " + self.song_resolution + "\n"
        self.song_details_text += "SP Phrases: " + str(len(self.song.sp_phrases)) + "\n"
        self.song_details_text += "Total notes (chords): " + str(self.song.total_chords()) + "\n"
        self.song_details_text += "Total notes: " + str(len(self.song.notes)) + "\n"
        self.song_details_text += "Base score: " + str(self.song.base_score(True)) + "\n"
        #self.song_details_text += "Score: " + str(self.song.base_score(True) -
        # self.song.MY_HEART_SCORE) + "\n"

        self.content = tk.Message(self, text=self.song_details_text, width=400)
        self.content.place(x=0, y=0)

        self.file_menu.entryconfig(1, state="normal")

    def save_file(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt")
        if file_name is None:
            return
        file_name.write(self.song_details_text)
        file_name.close()

    def create_widgets(self):

        self.menu_bar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.on_open)
        self.file_menu.add_command(label="Save as...", command=self.save_file)

        self.file_menu.add_separator()

        self.file_menu.add_command(label="Exit", command=self.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.quit)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.config(menu=self.menu_bar)

        self.file_menu.entryconfig(1, state="disabled")



app = Application()
app.mainloop()
