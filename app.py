from song import Song, SP_Phrase, Chart, Note
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from decimal import Decimal

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("600x450")
        self.grid_columnconfigure((0,1), weight=1)
        #self.frame = tk.Frame(self, width=1280, height=720)
        #self.frame.pack()
        #self.main_pane = tk.PanedWindow(self)
        #self.main_pane.pack(fill=tk.BOTH, expand=1)
        self.title("SPPathCreator")
        #self.iconbitmap("gh1.ico")
        self.create_widgets()

    def show_chart_info(self, event=None):
        chart_diffs = [chart.difficulty for chart in self.song.charts]
        i = chart_diffs.index(self.chart_box.get())
        chart = self.song.charts[i]

        self.spphrases_strvar.set(str(len(chart.sp_phrases)))
        self.uniquenotes_strvar.set(str(chart.total_unique_notes()))
        self.notes_strvar.set(len(chart.notes))
        self.basescore_strvar.set(round(chart.base_score(True), 3))

    def on_open(self):
        self.file_name = askopenfilename(filetypes=(('Chart files', '*.chart'), \
            ("All files", "*.*")))

        if self.file_name:
            self.read_chart(self.file_name)

    def read_chart(self, file_name):
        self.file_chart = open(file_name, "r")
        self.str_file = self.file_chart.read().splitlines()
        self.file_chart.close()

        self.song_parts = [line for line in self.str_file if '[' in line]

        for i in range(0, len(self.song_parts)):          
            start_index = self.str_file.index(self.song_parts[i])

            if i > len(self.song_parts) - 2:
                end_index = len(self.str_file)       
            else:
                end_index = self.str_file.index(self.song_parts[i + 1])

            str_content = self.str_file[start_index + 2 : end_index - 1]        
                
            str_part = self.song_parts[i].strip('[]')

            if str_part == "Song":
                self.song_name = str([line for line in str_content if "Name = " in line])
                self.song_name = self.song_name[len("['  Name = \"") : len(self.song_name) - 3]

                self.song_resolution = str([line for line in self.str_file if "Resolution = " in line])
                self.song_resolution = self.song_resolution[len("['  Resolution = ") : \
                    len(self.song_resolution) - 2]
                self.song = Song(self.song_name, int(self.song_resolution))

            elif str_part == "Events":
                self.sections = [line for line in self.str_file if " = E " in line]

                for str_section in self.sections:
                    start_index = str_section.find("section ") + len("section ") 
                    self.song.add_section(str_section[start_index : len(str_section) - 1])

            elif str_part in self.song.DIFFICULTIES:
                self.chart = Chart(str_part, self.song.resolution)

                self.str_notes = [line for line in str_content if " = N " in line]
                for str_note in self.str_notes:
                    note_list = str_note.split()
                    if int(note_list[3]) < 5 or int(note_list[3]) == 7:
                        note = Note(int(note_list[0]), int(note_list[3]), int(note_list[4]))
                        self.chart.add_note(note)

                self.str_sp_phrases = [line for line in str_content if " = S 2 " in line]
                for str_sp_phrase in self.str_sp_phrases:
                    sp_phrase_list = str_sp_phrase.split()
                    sp_phrase = SP_Phrase(int(sp_phrase_list[0]), int(sp_phrase_list[4]))
                    self.chart.add_sp_phrase(sp_phrase)   

                self.song.add_chart(self.chart)       

        self.name_strvar.set(self.song.name)
        self.res_strvar.set(str(self.song.resolution))
        self.totsections_strvar.set(str(len(self.song.sections)))

        self.chart_box["values"] = [chart.difficulty for chart in self.song.charts]
        self.chart_box.current(0)

        self.show_chart_info()
        self.chart_box.bind("<<ComboboxSelected>>", self.show_chart_info)

        self.file_menu.entryconfig(1, state="normal")
        self.export_menu.entryconfig(0, state="normal")

    def save_file(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt",
            filetypes = (("Text files","*.txt"),("All files","*.*")))
        if file_name is None:
            return
        #file_name.write(self.song_details)
        file_name.close()

    def export_sections(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt", 
        filetypes = (("Text files","*.txt"),("All files","*.*")))
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

        self.name_text = tk.StringVar()
        self.name_text.set("Name: ")
        self.name_label = tk.Label(self, textvariable=self.name_text, height=2)

        self.res_text = tk.StringVar()
        self.res_text.set("Resolution: ")
        self.res_label = tk.Label(self, textvariable=self.res_text, height=2)

        self.totsections_text = tk.StringVar()
        self.totsections_text.set("Total Sections: ")
        self.totsections_label = tk.Label(self, textvariable=self.totsections_text, height=2)

        self.spphrases_text = tk.StringVar()
        self.spphrases_text.set("Total SP Phrases: ")
        self.spphrases_label = tk.Label(self, textvariable=self.spphrases_text, height=2)

        self.uniquenotes_text = tk.StringVar()
        self.uniquenotes_text.set("Total Notes (unique): ")
        self.uniquenotes_label = tk.Label(self, textvariable=self.uniquenotes_text, height=2)

        self.notes_text = tk.StringVar()
        self.notes_text.set("Total Notes: ")
        self.notes_label = tk.Label(self, textvariable=self.notes_text, height=2)

        self.basescore_text = tk.StringVar()
        self.basescore_text.set("Base Score: ")
        self.basescore_label = tk.Label(self, textvariable=self.basescore_text, height=2)

        self.chart_text = tk.StringVar()
        self.chart_text.set("Chart: ")
        self.chart_label = tk.Label(self, textvariable=self.chart_text, height=2)

        

        self.name_strvar = tk.StringVar()
        self.name_entry = tk.Entry(self, textvariable=self.name_strvar,width=30,state="readonly")      

        self.res_strvar = tk.StringVar()
        self.res_entry = tk.Entry(self, textvariable=self.res_strvar,width=7,state="readonly")  

        self.totsections_strvar = tk.StringVar()
        self.totsections_entry = tk.Entry(self, textvariable=self.totsections_strvar,width=7,
            state="readonly")

        self.spphrases_strvar = tk.StringVar()
        self.spphrases_entry = tk.Entry(self, textvariable=self.spphrases_strvar,width=7,
            state="readonly")
        
        self.uniquenotes_strvar = tk.StringVar()
        self.uniquenotes_entry = tk.Entry(self, textvariable=self.uniquenotes_strvar,width=7,
            state="readonly")

        self.notes_strvar = tk.StringVar()
        self.notes_entry = tk.Entry(self, textvariable=self.notes_strvar,width=7,
            state="readonly")

        self.basescore_strvar = tk.StringVar()
        self.basescore_entry = tk.Entry(self, textvariable=self.basescore_strvar,width=15,
            state="readonly")

        self.chart_box = tk.ttk.Combobox(self)
        
        self.name_label.grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)
        self.res_label.grid(row=1, column=0)
        self.res_entry.grid(row=1, column=1)
        self.totsections_label.grid(row=2, column=0)
        self.totsections_entry.grid(row=2, column=1)

        self.chart_label.grid(row=0, column=2)
        self.chart_box.grid(row=0, column=3)

        self.spphrases_label.grid(row=1, column=2)
        self.spphrases_entry.grid(row=1, column=3) 
        self.uniquenotes_label.grid(row=2, column=2)
        self.uniquenotes_entry.grid(row=2, column=3)
        self.notes_label.grid(row=3, column=2)
        self.notes_entry.grid(row=3, column=3)
        self.basescore_label.grid(row=4, column=2)
        self.basescore_entry.grid(row=4, column=3)

app = Application()
app.mainloop()
