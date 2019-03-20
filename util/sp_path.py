import bisect
import math
from decimal import ROUND_HALF_UP, Decimal

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from .graph_img import Graph

class SP_Bar(object):
    def __init__(self, chart):
        self.max_length = chart.resolution * 32
        self.set(0)

    def set(self, new_value):
        self.number = max(0, min(self.max_length, new_value))

    def calc_percentage(self):
        return self.number / self.max_length * 100

    def is_sp_ready(self):
        return self.number >= self.max_length / 2

class SP_Path:

    VIZ_GRAPH = False

    def __init__(self, chart):
        self.chart = chart
        self.name = self.chart.name
        self.sp_phrases = self.chart.sp_phrases

        self.squeeze_length = self.chart.resolution / 64

        self.sp_bar = SP_Bar(self.chart)

        self.sp_end_notes = self.calc_sp_end_notes()

        self.pos_scores, self.sp_value_notes = self.calc_pos_scores(0, self.chart.length)

        self.sp_activations = self.calc_optimal_path()

        self.num_phrases = self.add_num_phrases()

        if self.VIZ_GRAPH:
            pos = self.hierarchy_pos(self.sp_graph, self.first_node)
            Graph(self.sp_graph, pos, self.path_node_list)

    def add_sp_values(self): 
        notes_pos = [note["position"] for note in self.chart.notes]

        upper_pos_i = 0

        for i in range(len(self.sp_phrases)):
            sp_value = 0

            lower_pos = self.sp_phrases[i]["position"]
            
            lower_pos_i = bisect.bisect_left(notes_pos, lower_pos, lo=upper_pos_i)

            upper_pos = lower_pos + self.sp_phrases[i]["length"] - 1
            upper_pos_i = bisect.bisect_right(notes_pos, upper_pos, lo=lower_pos_i)

            sp_notes = self.chart.notes[lower_pos_i:upper_pos_i]

            sp_value += self.sp_bar.max_length / 4

            for j in range(len(sp_notes)):
                if self.chart.is_unique_note(sp_notes[j]):     
                    sp_value += sp_notes[j]["length"]           

            self.sp_phrases[i]["value"] = int(sp_value)

    def calc_pos_scores(self, start, end): 

        pos_scores = []
        sp_value_notes = []

        c_length = start 
    
        pos_length = 1

        c_multiplier = 1

        notes = self.chart.notes
        n = 0
        sustain_notes = []

        pos_in_phrase = False

        sp_end_notes_pos = [note["position"] for note in self.sp_end_notes]

        while c_length <= end:
            c_length += pos_length

            pos_score = 0

            if sustain_notes:
                for i in range(len(sustain_notes)):
                    length_score = self.chart.NOTE_SCORE / 2 * c_multiplier / self.chart.resolution

                    sustain_notes[i]["length"] -= pos_length          

                    pos_score += length_score          

                    if sustain_notes[i]["length"] == 0:
                        tail_length = sustain_notes[i]["og_length"] / self.chart.resolution
                        tail_length /= 4
                        pos_score += tail_length

                        #pos_score = int(Decimal(pos_score).quantize(0, ROUND_HALF_UP))
                # Removes notes with empty length
                i = 0
                while i < len(sustain_notes):
                    
                    if sustain_notes[i]["length"] == 0:  
                        sustain_notes.remove(sustain_notes[i])   
                    else:
                        i += 1
                        

            if n < len(notes): 
                while notes[n]["position"] < c_length:    

                    add_sp_note = False
                    is_end_note = False

                    if c_multiplier < 4:
                        c_multiplier = self.chart.calc_note_multiplier(self.chart.calc_unote_index(notes[n])) 

                    pos_score += self.chart.NOTE_SCORE * c_multiplier  

                    self.chart.sp, pos_in_phrase = self.chart.pos_in_section(self.chart.sp, 
                        self.chart.sp_phrases, notes[n]["position"])   

                    if notes[n]["length"] > 0 and self.chart.is_unique_note(notes[n]):  

                        sustain_note =	{
                            "length": notes[n]["length"],
                            "og_length": notes[n]["length"],
                            "in_phrase": pos_in_phrase and (len(sustain_notes) == 0)
                        } 

                        if sustain_note["in_phrase"]:
                           add_sp_note = True


                        sustain_notes.append(sustain_note)    

                    if notes[n]["position"] in sp_end_notes_pos and self.chart.is_unique_note(notes[n]):                       
                        add_sp_note = True
                        is_end_note = True

                    if add_sp_note:
                        notes[n]["end_note"] = is_end_note
                        sp_value_notes.append(notes[n])
                        

                    n += 1
                    
                    if n == len(notes):
                        break
                        
            pos_scores.append(pos_score) 
        
        self.chart.sp = 0
        return pos_scores, sp_value_notes

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
    def calc_largest_score(self, length, start, end):
        c_score = 0

        n_length = min(length, self.chart.length - start)

        for i in range(start, start + n_length):
            c_score += self.pos_scores[i]

        max_score = {
            "score": c_score,
            "position": start,
            "length": length
        }

        if length >= self.chart.length - start:
            return max_score 

        for i in range(start + n_length, end + n_length):
            if i > self.chart.length - 1:
                break

            c_score += self.pos_scores[i] - self.pos_scores[i - length]

            if c_score > max_score["score"]:
                max_score["score"] = c_score
                max_score["position"] =  i - length + 1
        
        return max_score

    def calc_sp_end_notes(self):
        sp_end_notes = []

        notes_pos = [note["position"] for note in self.chart.notes]
    
        for s in range(len(self.sp_phrases)):
            sp_end_note_i = bisect.bisect_right(notes_pos, self.sp_phrases[s]["position"] + \
            self.sp_phrases[s]["length"] - 1) - 1

            sp_end_note_i = sp_end_note_i if sp_end_note_i < len(self.chart.notes) else len(self.chart.notes) - 1

            sp_end_notes.append(self.chart.notes[sp_end_note_i])    

        return sp_end_notes  

    def calc_optimal_path(self):

        sp_value_notes_pos = [sp["position"] for sp in self.sp_value_notes]

        self.sp_graph = nx.DiGraph()

        first_pos_node = (0,)
        self.first_node = first_pos_node
        last_pos_node = (self.chart.length,)
        
        self.sp_graph.add_node(first_pos_node, pos = [0, 0.5])
        self.sp_graph.add_node(last_pos_node, pos = [1, 0.5])

        current_nodes = [first_pos_node]

        sp_bar_activation = SP_Bar(self.chart) 

        while current_nodes:
            source_list = list(current_nodes[0])

            if current_nodes[0] is first_pos_node:
                source_list_pos = source_list[0]
            else:
                source_list_pos = source_list[1] + source_list[2]

            child_nodes_list = [source_list]

            new_activation = True
            first_activation = True
            sustain_ready = False

            self.sp_bar.set(0)   

            i = bisect.bisect(sp_value_notes_pos, source_list_pos)
            j = 0

            while i < len(self.sp_value_notes):

                if new_activation:
                    sp_increase = 0
                    
                    if self.sp_value_notes[i]["end_note"]:
                        sp_increase += self.sp_bar.max_length / 4            

                    self.sp_bar.set(self.sp_bar.number + sp_increase)  

                    if self.sp_bar.number + self.sp_value_notes[i]["length"] >= self.sp_bar.max_length / 2 \
                    and not self.sp_bar.is_sp_ready():
                        sustain_ready = True

                    self.sp_bar.set(self.sp_bar.number + self.sp_value_notes[i]["length"])   

                if self.sp_bar.is_sp_ready():  
                    activation_length = self.sp_bar.number + self.squeeze_length   

                    sp_bar_activation.set(activation_length) 
                                                 
                    if first_activation:                                 
                        first_pos = self.sp_value_notes[i]["position"]

                        if sustain_ready:
                            first_pos += self.sp_value_notes[i]["length"] - \
                            (activation_length - self.sp_bar.max_length / 2)
                            sustain_ready = False

                        first_activation = False
                    else:
                        first_pos = child_nodes_list[len(child_nodes_list) - 1][1] + 1        

                    if i == len(self.sp_value_notes) - 1:
                        last_pos = self.chart.length - self.sp_bar.number  
                        i += 1 
                    else:         
                        if new_activation:                                  
                            new_activation = False

                        j = i + 1

                        while self.sp_value_notes[j]["position"] <= first_pos + activation_length:
                            if self.sp_value_notes[j]["end_note"]:
                                sp_increase = self.sp_bar.max_length / 4
                                sp_bar_number = sp_bar_activation.number
                                sp_bar_activation.set(sp_bar_activation.number + sp_increase) 
                                activation_length += sp_bar_activation.number - sp_bar_number
                    
                            activation_length += self.sp_value_notes[j]["length"]
                            j += 1

                            if j == len(self.sp_value_notes):
                                break

                        if j == len(self.sp_value_notes):
                            if first_pos + activation_length > self.chart.length:
                                activation_length = self.chart.length - first_pos

                            last_pos = self.sp_value_notes[i + 1]["position"] - 1
                            i += 1 
                            new_activation = True
                        else:
                            last_pos = self.sp_value_notes[j]["position"] - activation_length - 1      

                            if last_pos >= self.sp_value_notes[i + 1]["position"]:
                                last_pos = self.sp_value_notes[i + 1]["position"] - 1
                                i += 1
                                new_activation = True

                    activation_list = [
                        first_pos, last_pos, 
                        int(activation_length), 
                        self.sp_bar.calc_percentage()
                    ]

                    child_nodes_list.append(activation_list)
                else:
                    i += 1                       
                    
            child_nodes_list.remove(source_list)
            source_tuple = tuple(source_list)

            if child_nodes_list:
                for node_to_add in child_nodes_list:
                    node_to_add = tuple(node_to_add)
                    nodes_list = list(self.sp_graph.nodes())

                    node_index = nodes_list.index(node_to_add) if \
                    node_to_add in nodes_list else []

                    if not node_index:
                        current_nodes.append(node_to_add)
                        self.sp_graph.add_node(node_to_add)
                    self.sp_graph.add_edge(source_tuple, node_to_add)
            else:
                self.sp_graph.add_edge(source_tuple, last_pos_node)

            current_nodes.remove(current_nodes[0])

        nx.set_name(self.sp_graph, self.name)
        print(nx.info(self.sp_graph))   

        for node in self.sp_graph.nodes():
            if node not in [first_pos_node, last_pos_node]:
                max_score = self.calc_largest_score(int(node[2]) if \
                self.chart.length > int(node[2]) else self.chart.length, \
                int(node[0]), int(node[1]))
                self.sp_graph.node[node]["max_score"] = max_score


        for edge in self.sp_graph.edges():
            if edge[0] is first_pos_node:
                max_score = 0
            else:
                max_score = self.sp_graph.node[edge[0]]["max_score"]["score"]

            self.sp_graph.add_edge(edge[0], edge[1], score = max_score)     
            
        self.path_node_list = nx.algorithms.dag.dag_longest_path(self.sp_graph, weight = "score")  

        self.path_node_list.remove(first_pos_node)
        self.path_node_list.remove(last_pos_node)

        print("path_node_list = " + str(self.path_node_list)) 

        sp_activations = []

        for node in self.path_node_list:
            print(str(self.sp_graph.node[node]["max_score"]))
            sp_activations.append(self.sp_graph.node[node]["max_score"])

        return sp_activations

    def add_num_phrases(self):
        num_phrases = []

        sp_end_notes_pos = [note["position"] for note in self.sp_end_notes]

        sp_end_notes = 0     
        overlapping_end_notes = 0
        sp_end_notes_i = 0

        for i in range(len(self.sp_activations)):
            if i > 0:
                sp_end_notes_i += sp_end_notes + overlapping_end_notes

            sp_end_notes = bisect.bisect(sp_end_notes_pos, self.sp_activations[i]["position"])
            
            overlapping_end_notes = bisect.bisect(sp_end_notes_pos, self.sp_activations[i]["position"] \
            + self.sp_activations[i]["length"]) - sp_end_notes

            sp_end_notes -= sp_end_notes_i

            num_phrases.append((sp_end_notes, overlapping_end_notes))

        return num_phrases

    def hierarchy_pos(self, G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

        def h_recur(G, root, width=1, vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, 
                    pos = None, parent = None, parsed = []):
            if(root not in parsed):
                parsed.append(root)

                if pos == None:
                    pos = {root:(xcenter,vert_loc)}
                else:
                    pos[root] = (xcenter, vert_loc)

                neighbors = list(G.neighbors(root))

                if len(neighbors) != 0:
                    dx = width/len(neighbors) 
                    nextx = xcenter - width/2 - dx/2
                    for neighbor in neighbors:
                        nextx += dx
                        pos = h_recur(G,neighbor, width = dx, vert_gap = vert_gap, 
                                            vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                            parent = root, parsed = parsed)
            return pos

        return h_recur(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5)
