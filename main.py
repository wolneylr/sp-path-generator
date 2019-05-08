import math
import tkinter as tk
from decimal import Decimal
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

import matplotlib.pyplot as plt

from chart_img import Chart_Img
from util.chart import Chart
from util.song import Song


class Application(tk.Tk):
    chart_image = None
    drawing = False
    def __init__(self):
        tk.Tk.__init__(self)
        #self.geometry("1080x720")
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_columnconfigure(1, minsize=1056)
        self.grid_rowconfigure(0, minsize=580)
        self.title("SP Path Generator")
        self.create_widgets()

    def show_chart_info(self, event=None):
        chart = self.song.charts[self.chart_box.current()]
        self.spphrases_strvar.set(str(len(chart.sp_phrases)))
        self.uniquenotes_strvar.set(str(chart.total_unique_notes()))
        self.notes_strvar.set(len(chart.notes))
        self.basescore_strvar.set(round(chart.calculate_score(0, len(chart.notes))))
        self.baseavgmult_strvar.set(round(chart.avg_multiplier(), 3))

    def on_open(self):
        self.file_name = askopenfilename(filetypes=(('Chart files', '*.chart'),("All files", "*.*")))

        if self.file_name:
            self.read_chart(self.file_name)

    # Experimental feature, still has some bugs
    def remove_beats(self, beat_length, num_beats, offset):

        for i in range(len(self.song_parts)): 
            str_part = self.song_parts[i].strip('[]')

            if str_part in self.song.DIFFICULTIES or str_part in ["SyncTrack", "Events"]:
                j = self.str_file.index(self.song_parts[i]) + 2

                if i > len(self.song_parts) - 2:
                    end_index = len(self.str_file) - 1       
                else:
                    end_index = self.str_file.index(self.song_parts[i + 1]) - 1

                c_length = offset
                beat_num = 0
                measure_num = 0

                num_beat_skips = 0
                beat_skip = True
            
                last_note = self.str_file[end_index - 1].split()

                part_length = int(last_note[0]) + \
                (int((last_note[4] if last_note[2] in ['N', 'S'] else 0)) if str_part in self.song.DIFFICULTIES else 0)

                line_list = self.str_file[j].split()

                while c_length <= part_length:
                    if line_list[0] == '}':
                        break 

                    beat_num += 1

                    c_length += beat_length    

                    if (beat_num - 1) % num_beats > 0:
                        if not beat_skip:
                            beat_skip = True
                            num_beat_skips += 1 
                    else:
                        if beat_skip:
                            beat_skip = False  
                            measure_num += 1     

                    while int(line_list[0]) < c_length:  
                        self.str_file.remove(self.str_file[j])     
 
                        if not beat_skip:  
                            line =	{
                                "position": int(line_list[0]),
                                "number": self.str_file[j][(len(line_list[0]) + 2):] if line_list[2] == "E"
                                else line_list[3],
                                "length": line_list[4] if line_list[2] in ["N", "S"] else ""
                            }

                            line["position"] -= beat_length * num_beat_skips 

                            if line_list[2] == "E":
                                str_line = "  " + str(line["position"]) + line["number"]
                            else:
                                str_line = "  " + str(line["position"]) + " = " + line_list[2] + \
                                " " + line["number"] 

                                if line["length"]:
                                    str_line += " " + line["length"]

                            self.str_file.insert(j, str_line)

                            j += 1     
                            
                        line_list = self.str_file[j].split()       

                        if line_list[0] == '}':
                            break   
        self.read_chart(False)

    def plot_bpm(self):
        plt.style.use('classic')
        plt.plot([bpm["position"] for bpm in self.song.bpms], [bpm["value"] for bpm in self.song.bpms], 
        color='green', linestyle='solid', marker='o', markerfacecolor='green', markersize=3)
        plt.xlabel("Position")
        plt.ylabel("BPM")
        plt.grid(True)
        plt.show()
    
    def read_chart(self, from_file):   
        if from_file: 
            file_chart = open(from_file, "r")
            self.str_file = file_chart.read().splitlines()
            file_chart.close()

        self.song_parts = [line for line in self.str_file if '[' in line]

        for i in range(len(self.song_parts)):  
            start_index = self.str_file.index(self.song_parts[i]) + 2

            if i == len(self.song_parts) - 1:
                end_index = len(self.str_file) - 1       
            else:
                end_index = self.str_file.index(self.song_parts[i + 1]) - 1

            str_content = self.str_file[start_index : end_index]                        
                
            str_part = self.song_parts[i].strip('[]')

            if "Song" in str_part:
                song_name = str([line for line in str_content if "Name = " in line])
                song_name = song_name[len("['  Name = \"") : len(song_name) - 3]

                song_charter = str([line for line in str_content if "Charter = " in line])
                song_charter = song_charter[len("['  Charter = \"") : len(song_charter) - 3]

                song_resolution = str([line for line in str_content if "Resolution = " in line])
                song_resolution = song_resolution[len("['  Resolution = ") : \
                    len(song_resolution) - 2]
                self.song = Song(song_name, song_charter, int(song_resolution))

            elif "SyncTrack" in str_part:
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
                        "value": math.trunc(int(round(int(bpm_list[3]) / 1000))) 
                    }
                    self.song.add_bpm(bpm)   

            elif "Events" in str_part:
                sections = [line for line in str_content if " = E \"section " in line]

                for str_section in sections:
                    section_list = str_section.split()
                    start_index = str_section.find("section ") + len("section ") 
                    section = {
                        "position": int(section_list[0]),
                        "name": str_section[start_index : len(str_section) - 1]
                    }
                    self.song.add_section(section)

            elif str_part in self.song.DIFFICULTIES:
                chart = Chart(self.song.name, str_part, self.song.resolution, self.song.time_signatures)
                str_notes = []
                str_sp_phrases = []
                str_solo_sections = []

                for line in str_content:
                    if " = N " in line:
                        str_notes.append(line)
                    elif " = S 2" in line:
                        str_sp_phrases.append(line)
                    elif " = E solo" in line:
                        str_solo_sections.append(line)

                for str_note in str_notes:
                    note_list = str_note.split()
                    if int(note_list[3]) < 5 or int(note_list[3]) == 7:
                        note =	{
                            "position": int(note_list[0]),
                            "number": int(note_list[3]),
                            "length": int(note_list[4])
                        }
                        chart.add_note(note)

                for str_sp_phrase in str_sp_phrases:
                    sp_phrase_list = str_sp_phrase.split()
                    sp_phrase =	{
                        "position": int(sp_phrase_list[0]),
                        "length": int(sp_phrase_list[4]),
                        "value": 0
                    }
                    chart.add_sp_phrase(sp_phrase)   

                solo_section_pos = 0
                for str_solo_section in str_solo_sections:
                    solo_section_list = str_solo_section.split()
                    if solo_section_list[3] == "solo":
                        solo_section_pos = int(solo_section_list[0])
                    elif solo_section_list[3] == "soloend":
                        solo_section =	{
                            "position": solo_section_pos,
                            "length": int(solo_section_list[0]) - solo_section_pos
                        }
                        chart.add_solo_section(solo_section)   

                chart.length = chart.calc_chart_length()
                self.song.add_chart(chart)  
         
        self.name_strvar.set(self.song.name)
        self.res_strvar.set(str(self.song.resolution))
        self.totsections_strvar.set(str(len(self.song.sections)))

        self.chart_box["values"] = [self.song.DIFFICULTIES[chart.difficulty] for chart in self.song.charts]
        self.chart_box.current(0)

        self.path_box["values"] = ["None", "Optimal"]
        self.path_box.current(0)

        self.show_chart_info()
        self.chart_box.bind("<<ComboboxSelected>>", self.show_chart_info)   

        self.file_menu.entryconfig(1, state="normal")
        self.song_menu.entryconfig(0, state="normal")
        self.export_menu.entryconfig(0, state="normal")

        self.generate_button.config(state="normal")
        

    def save_file(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt",
            filetypes=(('Chart files', '*.chart'),("All files", "*.*")))
        if file_name is None:
            return
        #file_name.write(song_details)
        for line in self.str_file:
            file_name.write(line + "\n")
        file_name.close()

    def export_sections(self):
        file_name = asksaveasfile(mode='w', defaultextension=".txt", 
        filetypes = (("Text files","*.txt"),("All files","*.*")),
        initialfile=self.song.name.lower().replace(" ", "") + "sections")
        if file_name is None:
            return

        for section in self.song.sections:
            file_name.write(section["name"] + "\n") 
        
        file_name.close()

    def export_chart(self):
        self.file_name = asksaveasfile(mode='a', defaultextension=".png", 
        filetypes = (("PNG files","*.png"),("All files","*.*")), initialfile=self.song.name.lower().replace(" ", ""))

        if self.file_name is None:
            return
        
        for page in range(self.chart_image.num_pages):
            self.chart_image.imss[page].write_to_png(self.file_name.name + (str(page + 1) 
            if self.chart_image.num_pages > 1 else ""))
        
        self.file_name.close()

    def create_widgets(self):
        self.menu_bar = tk.Menu(self)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open", command=self.on_open)
        self.file_menu.add_command(label="Save as...", command=self.save_file)   
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.file_menu.entryconfig(1, state="disabled")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.song_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.song_menu.add_command(label="BPM Analysis", command=self.plot_bpm)
        self.song_menu.entryconfig(0, state="disabled")
        self.menu_bar.add_cascade(label="Song", menu=self.song_menu)

        self.chart_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.chart_menu.add_command(label="Remove Beats", command=
        lambda: self.remove_beats(self.song.resolution * 2, 2, self.song.resolution * 2))
        self.chart_menu.entryconfig(0, state="disabled")
        self.menu_bar.add_cascade(label="Chart", menu=self.chart_menu)

        self.export_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.export_menu.add_command(label="Sections", command=self.export_sections)
        self.export_menu.add_command(label="Chart Image", command=self.export_chart)
        self.export_menu.entryconfig(0, state="disabled")
        self.export_menu.entryconfig(1, state="disabled")
        self.menu_bar.add_cascade(label="Export", menu=self.export_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.quit)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.config(menu=self.menu_bar)

        self.info_frame = ttk.LabelFrame(self, text="Info", relief=tk.RIDGE)
        self.info_frame.grid(row=0, column=0, sticky="news")

        self.name_text = tk.StringVar()
        self.name_text.set("Name")
        self.name_label = tk.Label(self.info_frame, textvariable=self.name_text)

        self.res_text = tk.StringVar()
        self.res_text.set("Resolution")
        self.res_label = tk.Label(self.info_frame, textvariable=self.res_text)

        self.totsections_text = tk.StringVar()
        self.totsections_text.set("Total Sections")
        self.totsections_label = tk.Label(self.info_frame, textvariable=self.totsections_text)

        self.spphrases_text = tk.StringVar()
        self.spphrases_text.set("Total SP Phrases")
        self.spphrases_label = tk.Label(self.info_frame, textvariable=self.spphrases_text)

        self.uniquenotes_text = tk.StringVar()
        self.uniquenotes_text.set("Total Notes (unique)")
        self.uniquenotes_label = tk.Label(self.info_frame, textvariable=self.uniquenotes_text)

        self.notes_text = tk.StringVar()
        self.notes_text.set("Total Notes")
        self.notes_label = tk.Label(self.info_frame, textvariable=self.notes_text)

        self.basescore_text = tk.StringVar()
        self.basescore_text.set("Base Score")
        self.basescore_label = tk.Label(self.info_frame, textvariable=self.basescore_text)

        self.baseavgmult_text = tk.StringVar()
        self.baseavgmult_text.set("Base Avg. Multiplier")
        self.baseavgmult_label = tk.Label(self.info_frame, textvariable=self.baseavgmult_text)

        self.name_strvar = tk.StringVar()
        self.name_entry = tk.Entry(self.info_frame, textvariable=self.name_strvar,width=50,state="readonly")      

        self.res_strvar = tk.StringVar()
        self.res_entry = tk.Entry(self.info_frame, textvariable=self.res_strvar,width=12,state="readonly")  

        self.totsections_strvar = tk.StringVar()
        self.totsections_entry = tk.Entry(self.info_frame, textvariable=self.totsections_strvar,width=12,
        state="readonly")

        self.spphrases_strvar = tk.StringVar()
        self.spphrases_entry = tk.Entry(self.info_frame, textvariable=self.spphrases_strvar,width=12,
            state="readonly")
        
        self.uniquenotes_strvar = tk.StringVar()
        self.uniquenotes_entry = tk.Entry(self.info_frame, textvariable=self.uniquenotes_strvar,width=12,
            state="readonly")

        self.notes_strvar = tk.StringVar()
        self.notes_entry = tk.Entry(self.info_frame, textvariable=self.notes_strvar,width=12,
            state="readonly")

        self.basescore_strvar = tk.StringVar()
        self.basescore_entry = tk.Entry(self.info_frame, textvariable=self.basescore_strvar,width=12,
            state="readonly")

        self.baseavgmult_strvar = tk.StringVar()
        self.baseavgmult_entry = tk.Entry(self.info_frame, textvariable=self.baseavgmult_strvar,width=12,
            state="readonly")
        
        self.name_label.grid(row=0, sticky="w")
        self.name_entry.grid(row=1, sticky="w")
        self.res_label.grid(row=2, sticky="w")
        self.res_entry.grid(row=3, sticky="w")
        self.totsections_label.grid(row=4, sticky="w")
        self.totsections_entry.grid(row=5, sticky="w")
        self.spphrases_label.grid(row=6, sticky="w")
        self.spphrases_entry.grid(row=7, sticky="w") 
        self.uniquenotes_label.grid(row=8, sticky="w")
        self.uniquenotes_entry.grid(row=9, sticky="w")
        self.notes_label.grid(row=10, sticky="w")
        self.notes_entry.grid(row=11, sticky="w")
        self.basescore_label.grid(row=12, sticky="w")
        self.basescore_entry.grid(row=13, sticky="w")
        self.baseavgmult_label.grid(row=14, sticky="w")
        self.baseavgmult_entry.grid(row=15, sticky="w")

        self.options_frame = ttk.LabelFrame(self, text="Options")
        self.options_frame.grid(row=1, column=0, sticky="news")

        self.chart_text = tk.StringVar()
        self.chart_text.set("Chart")
        self.chart_label = tk.Label(self.options_frame, textvariable=self.chart_text)

        self.path_text = tk.StringVar()
        self.path_text.set("Path")
        self.path_label = tk.Label(self.options_frame, textvariable=self.path_text)

        self.chart_box = tk.ttk.Combobox(self.options_frame)
        self.path_box = tk.ttk.Combobox(self.options_frame)

        self.dark_mode_button = ttk.Checkbutton(self.options_frame, text="Dark Mode")
        self.dark_mode_button.state(['!disabled','selected'])

        self.generate_button = tk.Button(self.options_frame, text="Generate", 
        command=self.generate_chart_image, state="disabled")

        self.progress_bar = ttk.Progressbar(self.options_frame, orient ="horizontal",
        length = 150, mode ="determinate")

        self.chart_label.grid(row=0, sticky="w")
        self.chart_box.grid(row=1, sticky="w")
        self.path_label.grid(row=2, sticky="w")
        self.path_box.grid(row=3, sticky="w")
        self.dark_mode_button.grid(row=4, sticky="w")
        self.generate_button.grid(row=5, sticky="w")
        self.progress_bar.grid(row=6, sticky="w")

        self.img_frame = ttk.LabelFrame(self, text="Chart Preview")
        self.img_frame.grid(row=0, column=1, sticky="news", rowspan=2)

        self.frame_image = tk.Frame(self.img_frame)
        self.frame_image.pack(expand=True, fill="both")
        self.frame_image.grid_rowconfigure(0, weight = 1)
        self.frame_image.grid_columnconfigure(0, weight = 1)

        #self.xscrollbar = tk.Scrollbar(self.frame_image, orient=tk.HORIZONTAL)
        #self.xscrollbar.grid(row=1, column=0, sticky="ew")

        self.yscrollbar = tk.Scrollbar(self.frame_image)
        self.yscrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas = tk.Canvas(self.frame_image)
        #self.canvas.configxscrollcommand=self.xscrollbar.set)
        self.canvas.config(yscrollcommand=self.yscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="news")

        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        #self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar.config(command=self.canvas.yview)    

        self.frame_image.pack()

    def generate_chart_image(self):
        self.chart = self.song.charts[self.chart_box.current()]
        self.chart_image = Chart_Img(self.song, self.chart)

        self.chart_image.sp_path = self.path_box.current()
        self.chart_image.dark_mode = self.dark_mode_button.instate(['selected'])
         
        self.chart_image.draw_pages()

        self.progress_bar.config(maximum=self.chart_image.chart_length)
        self.drawing = True
        self.read_position()

        self.chart_image.draw_top_info()
        self.chart_image.draw_chart(False)
        self.chart_image.draw_chart(True)
        self.chart_image.draw_bottom_info()

        self.drawing = False

        self.file_name = "assets/Chart Images/" + self.song.name.lower().replace(" ", "") + ".png"

        self.chart_image.imss[0].write_to_png(self.file_name)

        self.img = tk.PhotoImage(file=self.file_name)
        self.canvas.create_image(0,0,image=self.img, anchor="nw")
        self.canvas.config(scrollregion=(0, 0, self.chart_image.WIDTH, self.chart_image.first_page_height))

        self.chart_menu.entryconfig(0, state="normal")
        self.export_menu.entryconfig(1, state="normal")

    def read_position(self):     
        if self.drawing:
            c_length = self.chart_image.c_length
            chart_length = self.chart_image.chart_length
            bar_length = c_length if c_length < chart_length else chart_length
            self.progress_bar.config(value=bar_length)
            self.after(100, self.read_position)
        


def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
