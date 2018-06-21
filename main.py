from song import Song, Chart
#from chart_img import Chart_Img

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

from decimal import Decimal

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("600x450")
        self.grid_columnconfigure((0,1), weight=1)
        self.title("SPPathCreator")
        self.create_widgets()

    def create_chart_image(self):
        chart = self.song.charts[self.chart_diffs.index(self.chart_box.get())]

        #chart_img = Chart_Img(self.song.name, chart)
        #chart_img.draw_measures()

    def show_chart_info(self, event=None):  
        chart = self.song.charts[self.chart_diffs.index(self.chart_box.get())]

        self.spphrases_strvar.set(str(len(chart.sp_phrases)))
        self.uniquenotes_strvar.set(str(chart.total_unique_notes()))
        self.notes_strvar.set(len(chart.notes))
        self.basescore_strvar.set(round(chart.base_score(True, False), 3))
        self.baseavgmult_strvar.set(round(chart.avg_multiplier(), 3))

    def on_open(self):
        self.file_name = askopenfilename(filetypes=(('Chart files', '*.chart'), \
            ("All files", "*.*")))

        if self.file_name:
            print(self.file_name)
            self.read_chart(self.file_name)

    def read_chart(self, file_name):
        file_chart = open(file_name, "r")
        str_file = file_chart.read().splitlines()
        file_chart.close()

        song_parts = [line for line in str_file if '[' in line]

        for i in range(len(song_parts)):          
            start_index = str_file.index(song_parts[i]) + 2

            if i > len(song_parts) - 2:
                end_index = len(str_file) - 1       
            else:
                end_index = str_file.index(song_parts[i + 1]) - 1

            str_content = str_file[start_index : end_index]                        
                
            str_part = song_parts[i].strip('[]')

            if str_part == "Song":
                song_name = str([line for line in str_content if "Name = " in line])
                song_name = song_name[len("['  Name = \"") : len(song_name) - 3]

                song_resolution = str([line for line in str_content if "Resolution = " in line])
                song_resolution = song_resolution[len("['  Resolution = ") : \
                    len(song_resolution) - 2]
                self.song = Song(song_name, int(song_resolution))

            elif str_part == "SyncTrack":
                str_time_signatures = [line for line in str_content if " = TS " in line]

                for str_time_signature in str_time_signatures:
                    time_signature_list = str_time_signature.split()
                    time_signature =	{
                            "position": int(time_signature_list[0]),
                            "beats": int(time_signature_list[3])
                    }
                    self.song.add_time_signature(time_signature)   

                str_bpms = [line for line in str_content if " = B " in line]

                for str_bpm in str_bpms:
                    bpm_list = str_bpm.split()
                    bpm =	{
                            "position": int(bpm_list[0]),
                            "value": int(bpm_list[3])
                    }
                    self.song.add_bpm(bpm)   

            elif str_part == "Events":
                sections = [line for line in str_content if " = E " in line]

                for str_section in sections:
                    start_index = str_section.find("section ") + len("section ") 
                    self.song.add_section(str_section[start_index : len(str_section) - 1])

            elif str_part in self.song.DIFFICULTIES:
                chart = Chart(str_part, self.song.resolution)
                str_notes = [line for line in str_content if " = N " in line]
                for str_note in str_notes:
                    note_list = str_note.split()
                    if int(note_list[3]) < 5 or int(note_list[3]) == 7:
                        note =	{
                            "position": int(note_list[0]),
                            "number": int(note_list[3]),
                            "length": int(note_list[4])
                        }
                        chart.add_note(note)

                str_sp_phrases = [line for line in str_content if " = S 2 " in line]
                for str_sp_phrase in str_sp_phrases:
                    sp_phrase_list = str_sp_phrase.split()
                    sp_phrase =	{
                            "position": int(sp_phrase_list[0]),
                            "length": int(sp_phrase_list[4])
                    }
                    chart.add_sp_phrase(sp_phrase)   

                
                self.song.add_chart(chart)      

                
        self.name_strvar.set(self.song.name)
        self.res_strvar.set(str(self.song.resolution))
        self.totsections_strvar.set(str(len(self.song.sections)))

        self.chart_box["values"] = [chart.difficulty for chart in self.song.charts]
        self.chart_box.current(0)

        self.chart_diffs = [chart.difficulty for chart in self.song.charts]
        self.create_chart_image() 

        self.show_chart_info()
        self.chart_box.bind("<<ComboboxSelected>>", self.show_chart_info)    

        self.file_menu.entryconfig(1, state="normal")
        self.export_menu.entryconfig(0, state="normal")

    def save_file(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt",
            filetypes = (("Text files","*.txt"),("All files","*.*")))
        if file_name is None:
            return
        #file_name.write(song_details)
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

        self.baseavgmult_text = tk.StringVar()
        self.baseavgmult_text.set("Base Avg. Multiplier: ")
        self.baseavgmult_label = tk.Label(self, textvariable=self.baseavgmult_text, height=2)

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

        self.baseavgmult_strvar = tk.StringVar()
        self.baseavgmult_entry = tk.Entry(self, textvariable=self.baseavgmult_strvar,width=15,
            state="readonly")

        self.chart_box = tk.ttk.Combobox(self)
        
        self.name_label.grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)
        self.res_label.grid(row=1, column=0)
        self.res_entry.grid(row=1, column=1)
        self.totsections_label.grid(row=2, column=0)
        self.totsections_entry.grid(row=2, column=1)

        self.chart_label.grid(row=3, column=0)
        self.chart_box.grid(row=3, column=1)

        self.spphrases_label.grid(row=4, column=0)
        self.spphrases_entry.grid(row=4, column=1) 
        self.uniquenotes_label.grid(row=5, column=0)
        self.uniquenotes_entry.grid(row=5, column=1)
        self.notes_label.grid(row=6, column=0)
        self.notes_entry.grid(row=6, column=1)
        self.basescore_label.grid(row=7, column=0)
        self.basescore_entry.grid(row=7, column=1)
        self.baseavgmult_label.grid(row=8, column=0)
        self.baseavgmult_entry.grid(row=8, column=1)

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
