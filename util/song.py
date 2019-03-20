import math
import bisect

class Song:

    DIFFICULTIES = {
        "ExpertSingle": "Expert Guitar", 
        "HardSingle": "Hard Guitar", 
        "MediumSingle": "Medium Guitar", 
        "EasySingle": "Easy Guitar",
        "ExpertDoubleBass": "Expert Bass",
        "HardDoubleBass": "Hard Bass", 
        "MediumDoubleBass": "Medium Bass", 
        "EasyDoubleBass": "Easy Bass",
        "ExpertDoubleRhythm": "Expert Rhythm",
        "HardDoubleRhythm": "Hard Rhythm", 
        "MediumDoubleRhythm": "Medium Rhythm", 
        "EasyDoubleRhythm": "Easy Rhythm",
        "ExpertKeyboard": "Expert Keys", 
        "HardKeyboard": "Hard Keys", 
        "MediumKeyboard": "Medium Keys", 
        "EasyKeyboard": "Easy Keys",
        "ExpertDrums": "Expert Drums",
        "HardDrums": "Hard Drums", 
        "MediumDrums": "Medium Drums", 
        "EasyDrums": "Easy Drums"
    }

    def __init__(self, name, charter, resolution=192):
        self.name = name if name else "Unknown"
        self.charter = charter if charter else "Unknown Charter"
        self.resolution = resolution 
        self.bpms = []
        self.time_signatures = []
        self.sections = []
        self.charts = []


    def add_section(self, section):
        self.sections.append(section)

    def add_bpm(self, bpm):
        self.bpms.append(bpm)

    def add_time_signature(self, time_signature):
        self.time_signatures.append(time_signature)

    def add_chart(self, chart):
        self.charts.append(chart)