import bisect

class SP_Path:

    SP_BAR_BEATS = 32

    def __init__(self, chart):
        self.chart = chart
        self.sp_activations = []
        self.sp_end_notes = []

        self.sp_bar = 0
        self.sp_bar_length = self.chart.resolution * self.SP_BAR_BEATS

        self.num_phrases = []

        self.add_sp_end_notes()
        self.set_basic_sp_path()

    def add_sp_end_notes(self):
        sp_phrases = self.chart.sp_phrases

        notes_pos = [note["position"] for note in self.chart.notes]
    
        for s in range(len(sp_phrases)):
            self.sp_end_notes.append(self.chart.notes[bisect.bisect_right(
            notes_pos, sp_phrases[s]["position"] + sp_phrases[s]["length"] - 1)])    

    def can_activate_sp(self):
        return self.sp_bar >= self.sp_bar_length / 2

    def add_sp_activation(self, sp_activation):
        self.sp_activations.append(sp_activation)

    def set_basic_sp_path(self):

        pos = 0
        chart_length = self.chart.calc_chart_length()

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

