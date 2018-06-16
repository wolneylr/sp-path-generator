from song import Song, SP_Phrase, Note
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfile

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = tk.Frame(self, width=1280, height=720)
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

        self.str_sections = [line for line in self.str_chart if " = E " in line]

        for str_section in self.str_sections:
            start_index = str_section.find("section ") + len("section ") 
            self.song.add_section(str_section[start_index : len(str_section) - 1])

        self.str_notes = [line for line in self.str_chart if " = N " in line]

        for str_note in self.str_notes:
            note_list = str_note.split()
            if int(note_list[3]) < 5 or int(note_list[3]) == 7:
                note = Note(int(note_list[0]), int(note_list[3]), int(note_list[4]))
                self.song.add_note(note)

        self.str_sp_phrases = [line for line in self.str_chart if " = S 2 " in line]
        for str_sp_phrase in self.str_sp_phrases:
            sp_phrase_list = str_sp_phrase.split()
            sp_phrase = SP_Phrase(int(sp_phrase_list[0]), int(sp_phrase_list[4]))
            self.song.add_sp_phrase(sp_phrase)

        self.song_details_text = "Name: " + self.song.name + "\n"
        self.song_details_text += "Resolution: " + str(self.song.resolution) + "\n"
        self.song_details_text += "Total sections: " + str(len(self.song.sections)) + "\n"
        self.song_details_text += "Total SP Phrases: " + str(len(self.song.sp_phrases)) + "\n"
        self.song_details_text += "Total notes (unique): " + str(self.song.total_unique_notes()) + "\n"
        self.song_details_text += "Total notes: " + str(len(self.song.notes)) + "\n"
        self.song_details_text += "Base score: " + str(self.song.base_score(True)) + "\n"

        self.content = tk.Message(self, text=self.song_details_text, width=400)
        self.content.place(x=20, y=20)

        self.file_menu.entryconfig(1, state="normal")
        self.export_menu.entryconfig(0, state="normal")

    def save_file(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt")
        if file_name is None:
            return
        file_name.write(self.song_details_text)
        file_name.close()

    def export_sections(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt")
        if file_name is None:
            return

        for section in self.song.sections:
            file_name.write(section + "\n") 
        
        file_name.close()

    def create_widgets(self):
        self.menu_bar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.on_open)
        self.file_menu.add_command(label="Save as...", command=self.save_file)   
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.file_menu.entryconfig(1, state="disabled")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.quit)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="Sections", command=self.export_sections)
        self.export_menu.entryconfig(0, state="disabled")
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)

        self.config(menu=self.menu_bar)


app = Application()
app.mainloop()
