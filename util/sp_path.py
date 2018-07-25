import bisect
import math
import random
from decimal import ROUND_HALF_UP, Decimal

#import pylab as plt
import matplotlib.pyplot as plt
import networkx as nx

from .graph import Graph

#from networkx.drawing.nx_agraph import graphviz_layout

#import pygraphviz as pgv



class SP_Bar(object):
    def __init__(self, max_length):
        self.max_length = max_length
        self.set(0)

    def set(self, new_value):
        self.number = max(0, min(self.max_length, new_value))

    def calc_percentage(self):
        return self.number / self.max_length

    def can_activate(self):
        return self.number >= self.max_length / 2

class SP_Path:

    SP_BAR_BEATS = 32

    def __init__(self, chart):
        self.chart = chart
        self.sp_phrases = self.chart.sp_phrases

        self.sp_bar = SP_Bar(self.chart.resolution * self.SP_BAR_BEATS)

        self.add_sp_values()
        self.total_sp_value = sum([sp_phrase["value"] for sp_phrase in self.sp_phrases])   

        self.sp_end_notes = self.calc_sp_end_notes()

        self.pos_scores, self.sp_value_notes = self.calc_pos_scores(0, self.chart.length)

        self.max_num_activations = int(self.total_sp_value / (self.sp_bar.max_length / 2))

        '''
        sp_file = open("pos_scores.txt","w") 

        for i in range(len(self.pos_scores)):
            sp_file.write(str(i) + " = " + str(self.pos_scores[i]) + '\n') 
        
        sp_file.close() 
        '''
        
        print("sum of pos scores = " + str(sum(self.pos_scores)))
        print("sum of sp values = " + str(sum([sp_phrase["value"] for sp_phrase in self.sp_phrases])))
        print("max_num_activations = " + str(self.max_num_activations))
        # print("last pos sp value = " + str(self.pos_scores[len(self.pos_scores) - 1]["sp_value"]))

        self.max_score_lengths = []#self.calc_largest_scores(int(self.sp_bar.max_length / 2) if \
        #self.chart.length > int(self.sp_bar.max_length / 2) else self.chart.length, 0, len(self.pos_scores)) 

        '''
        self.phrase_sums = self.calc_phrase_sums(len(self.sp_phrases))  
        for phrase_sum in self.phrase_sums:
            print(str(phrase_sum))
        print("len(self.phrase_sums) = " + str(len(self.phrase_sums)))
        '''

        self.sp_activations = []
        self.num_phrases = []
        #self.set_basic_sp_path() 
        self.set_optimal_path()
        self.visualize_graph("plotly")

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
                for i in range(len(sustain_notes)):
                    if i >= len(sustain_notes):
                        break

                    if sustain_notes[i]["length"] == 0:
                        sustain_notes.remove(sustain_notes[i])       

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

    """
        Return the index where to insert item x in list a, assuming a is sorted in descending order.

        The return value i is such that all e in a[:i] have e >= x, and all e in
        a[i:] have e < x.  So if x already appears in the list, a.insert(x) will
        insert just after the rightmost x already there.

        Optional args lo (default 0) and hi (default len(a)) bound the
        slice of a to be searched.

        Essentially, the function returns number of elements in a which are >= than x.
        > a = [8, 6, 5, 4, 2]
        > reverse_bisect_right(a, 5)
        3
        > a[:reverse_bisect_right(a, 5)]
        [8, 6, 5]
    """
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
    def calc_largest_scores(self, length, start, end):
        positions = self.pos_scores

        num_scores = 1

        overlapping_lengths = False

        prev_seq_score = 0

        n_length = (end - start) if (end - start) < length else length

        for i in range(start, start + n_length):
            prev_seq_score += positions[i]

        start_i_final = start

        #end_i_final = n_length - 1

        max_score = {
            "score": prev_seq_score,
            "position": start_i_final,
            #"length": (end_i_final - start_i_final + 1)
            "length": length
        }

        max_scores = [max_score]

        c_score = 0

        for i in range(start + length, end):
            c_score = prev_seq_score + positions[i] - positions[i - length]
            
            max_scores_scores = [max_score["score"] for max_score in max_scores]

            score_index = self.reverse_bisect_right(max_scores_scores, c_score)

            #end_i_final = i
            start_i_final = i - length

            c_max_score = {
                "score": c_score,
                "position": start_i_final,
                #"length": (end_i_final - start_i_final + 1)
                "length": length
            }

            insert_length = True
            
            # Only insert length if length's starting position is bigger than first activation position
            if len(self.sp_end_notes) > 1:
                if (i - length + 1) < self.sp_end_notes[1]["position"]:
                    insert_length = False

            if not overlapping_lengths and insert_length:
                for j in range(len(max_scores)):
                    # Checks if current max score length overlaps with max score length from array
                    if c_max_score["position"] >= max_scores[j]["position"] and \
                    c_max_score["position"] < max_scores[j]["position"] + max_scores[j]["length"]:
                        if j >= score_index:
                            max_scores.remove(max_scores[j])     
                        else:
                            insert_length = False
                        break                 

            if insert_length:
                max_scores.insert(score_index, c_max_score)

                if len(max_scores) > num_scores:
                    max_scores.remove(max_scores[num_scores])

            prev_seq_score = c_score
        '''
        # Sorts max score list by position
        max_scores = sorted(max_scores, key=lambda k: k["position"])
        
        for max_score in max_scores:
            print(str(max_score))

        print("len(max_scores) = " + str(len(max_scores)))
        print("len(scores) = " + str(len(positions)))
        '''
        

        return max_scores

    def calc_sp_end_notes(self):
        sp_end_notes = []

        notes_pos = [note["position"] for note in self.chart.notes]
    
        for s in range(len(self.sp_phrases)):
            sp_end_note_i = bisect.bisect_right(notes_pos, self.sp_phrases[s]["position"] + \
            self.sp_phrases[s]["length"] - 1) - 1

            sp_end_note_i = sp_end_note_i if sp_end_note_i < len(self.chart.notes) else len(self.chart.notes) - 1

            sp_end_notes.append(self.chart.notes[sp_end_note_i])    

        return sp_end_notes

    def can_activate_sp(self):
        return self.sp_bar >= self.sp_bar.max_length / 2

    def add_sp_activation(self, sp_activation):
        self.sp_activations.append(sp_activation)

    def set_basic_path(self):


        pos = 0
        chart_length = self.chart.length

        c_number = 0

        while pos < chart_length:
            
            if pos >= self.sp_end_notes[0]["position"]:
                self.sp_bar.set(self.sp_bar.number + (self.sp_bar.max_length / 4)) 
                c_number += 1
                self.sp_end_notes.remove(self.sp_end_notes[0])
                

            if self.can_activate_sp():
                sp_activation = {
                    "position": pos,
                    "length": self.sp_bar.number
                }
                self.sp_bar = 0
                self.num_phrases.append(c_number)
                c_number = 0
                self.add_sp_activation(sp_activation)

            pos += self.chart.resolution

            if not self.sp_end_notes:
                    break

    def set_optimal_path(self):
        '''
        for note in self.sp_value_notes:
            print(str(note))
        '''

        print("len(sp_value_notes) = " + str(len(self.sp_value_notes)))

        sp_value_notes_pos = [sp["position"] for sp in self.sp_value_notes]

        self.sp_graph = nx.DiGraph()
        first_pos_node = (0,)
        self.first_node = first_pos_node
        last_pos_node = (self.chart.length,)
        self.sp_graph.add_node(first_pos_node, pos = [0, 0.5])
        self.sp_graph.add_node(last_pos_node, pos = [1, 0.5])

        current_nodes = [first_pos_node]

        while current_nodes:
            source_node = list(current_nodes[0])

            if current_nodes[0] is first_pos_node:
                source_node_pos = source_node[0]
            else:
                source_node_pos = source_node[1] + source_node[2]

            node_list = [source_node]
            start_index = bisect.bisect(sp_value_notes_pos, source_node_pos)
            first_activation = True
            self.sp_bar.set(0)      
            for i in range(start_index, len(self.sp_value_notes)):  
                sp_increase = 0

                if self.sp_value_notes[i]["end_note"]:
                    sp_increase += self.sp_bar.max_length / 4

                sp_increase += self.sp_value_notes[i]["length"]

                self.sp_bar.set(self.sp_bar.number + sp_increase)            

                if self.sp_bar.can_activate():  
                    activation_length = self.sp_bar.number  

                    first_pos = self.sp_value_notes[i]["position"] + self.sp_value_notes[i]["length"] \
                    - (activation_length - self.sp_bar.max_length / 2)

                    if i == len(self.sp_value_notes) - 1:
                        last_pos = self.chart.length - self.sp_bar.number   
                    else:
                        last_pos = self.sp_value_notes[i + 1]["position"] - 1       

                    if first_activation:                                           
                            first_activation = False
                    else:
                        first_pos -= self.sp_bar.number
                        last_node = node_list[len(node_list) - 1]                      

                        if first_pos < last_node[1]:
                            last_node[1] = first_pos - 1

                    
                    activation_list = [first_pos, last_pos, int(activation_length)]
                    node_list.append(activation_list)

            node_list.remove(source_node)
            source_node = tuple(source_node)

            if node_list:
                for node_to_add in node_list:
                    node_to_add = tuple(node_to_add)
                    nodes_list = list(self.sp_graph.nodes())

                    node_index = nodes_list.index(node_to_add) if \
                    node_to_add in nodes_list else []

                    if not node_index:
                        current_nodes.append(node_to_add)
                        self.sp_graph.add_node(node_to_add, \
                        pos = [random.uniform(0.2, 0.8), random.uniform(0.3, 0.7)])
                    self.sp_graph.add_edge(source_node, node_to_add)
            else:
                self.sp_graph.add_edge(source_node, last_pos_node)

            current_nodes.remove(current_nodes[0])

        
        print(nx.info(self.sp_graph))
       

        for node in self.sp_graph.nodes():
            if node not in [first_pos_node, last_pos_node]:
                max_score = self.calc_largest_scores(int(node[2]) if \
                self.chart.length > int(node[2]) else self.chart.length, \
                int(node[0]), int(node[1]))
                self.sp_graph.node[node]["max_score"] = max_score[0]


        for edge in self.sp_graph.edges():
            if edge[0] is first_pos_node:
                max_score = 0
            else:
                max_score = self.sp_graph.node[edge[0]]["max_score"]["score"]

            self.sp_graph.add_edge(edge[0], edge[1], score = max_score)     
            
        self.path_node_list = nx.algorithms.dag.dag_longest_path(self.sp_graph, weight = "score")  

        print("path_node_list = " + str(self.path_node_list)) 

        #paths = nx.all_simple_paths(self.sp_graph, source=first_pos_node, target=last_pos_node)

        '''
        for path in paths:
            print(path)
        '''

        #print("len(paths) = " + str(len(list(paths))))


        for node in self.path_node_list:
            if node not in [first_pos_node, last_pos_node]:
                self.add_sp_activation(self.sp_graph.node[node]["max_score"])   
        

    def visualize_graph(self, viz):
        if viz == "gephi":
            G = nx.path_graph(len(self.sp_graph.nodes()))    
            '''
            for i, node in enumerate(self.sp_graph.nodes(data=True)):
                G.node[i]["viz"] = {"size": self.sp_graph.degree[node]}
                G.node[i]["position"] = \
                {"x": data['pos'][0], \
                "y": data['pos'][1]}
                G.node[i]["color"] = \
                {"r": 0, "g": 0, "b": self.sp_graph.degree[node]}
                G.node[i]["label"] = self.sp_graph.node[node]
            '''

            

            nx.write_gexf(G, "sp_graph.gexf")

        elif viz == "plotly":
            pos = self.large_hierarchy_pos(self.sp_graph, self.first_node)
            Graph(self.sp_graph, pos, self.path_node_list)
        elif viz == "matplotlib":
            graph_pos = nx.shell_layout(self.sp_graph)

            nx.draw_networkx_nodes(self.sp_graph, graph_pos, node_size=100, node_color='blue', alpha=0.75)
            nx.draw_networkx_edges(self.sp_graph, graph_pos, width=0.25, alpha=1, edge_color='green')
            nx.draw_networkx_labels(self.sp_graph, graph_pos, font_size=6, font_family='sans-serif')

            edge_labels = nx.get_edge_attributes(self.sp_graph,'score')
            nx.draw_networkx_edge_labels(self.sp_graph, graph_pos, edge_labels = edge_labels, \
            font_size=4, font_family='sans-serif')


            plt.show()
        elif viz == "pydot":
            p = nx.drawing.nx_pydot.to_pydot(self.sp_graph)
            p.write_png('sp_graph.png')
        '''
        nx.draw(self.sp_graph, with_labels = True)      

        # set defaults
        self.sp_graph.graph['graph'] = {'rankdir':'TD'}
        self.sp_graph.graph['node'] = {'shape':'circle'}
        self.sp_graph.graph['edges'] = {'arrowsize':'4.0'}
        
        agraph = nx.drawing.nx_agraph.to_agraph(self.sp_graph)
        print(agraph)
        agraph.layout('dot')
        agraph.draw('graph.png')

        plt.show()
        '''

        '''
        pos = nx.spectral_layout(self.sp_graph, scale = 4)

        nx.draw(self.sp_graph, pos, font_size = 8, with_labels = True)
        plt.show()

        '''
        #pos = graphviz_layout(self.sp_graph, prog='dot')

    def hierarchy_pos(self, G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):
        '''If there is a cycle that is reachable from root, then result will not be a hierarchy.

        G: the graph
        root: the root node of current branch
        width: horizontal space allocated for this branch - avoids overlap with other branches
        vert_gap: gap between levels of hierarchy
        vert_loc: vertical location of root
        xcenter: horizontal location of root
        '''        
        def h_recur(G, root, width=1, vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, 
                    pos = None, parent = None, parsed = [] ):
            if(root not in parsed):
                parsed.append(root)
                if pos == None:
                    pos = {root:(xcenter,vert_loc)}
                else:
                    pos[root] = (xcenter, vert_loc)
                neighbors = list(G.neighbors(root))
                #if parent != None:
                #    neighbors.remove(parent)
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

    # burubum's solution for large trees
    def large_hierarchy_pos(self, G, root, levels=None, width=1, height=1):
        '''If there is a cycle that is reachable from root, then this will see infinite recursion.
        G: the graph
        root: the root node
        levels: a dictionary
                key: level number (starting from 0)
                value: number of nodes in this level
        width: horizontal space allocated for drawing
        height: vertical space allocated for drawing'''
        TOTAL = "total"
        CURRENT = "current"
        def make_levels(levels, node=root, currentLevel=0, parent=None):
            """Compute the number of nodes for each level
            """
            if not currentLevel in levels:
                levels[currentLevel] = {TOTAL : 0, CURRENT : 0}
            levels[currentLevel][TOTAL] += 1
            neighbors = G.neighbors(node)
            #if parent is not None:
            #    neighbors.remove(parent)
            for neighbor in neighbors:
                levels =  make_levels(levels, neighbor, currentLevel + 1, node)
            return levels

        def make_pos(pos, node=root, currentLevel=0, parent=None, vert_loc=0):
            dx = 1/levels[currentLevel][TOTAL]
            left = dx/2
            pos[node] = ((left + dx*levels[currentLevel][CURRENT])*width, vert_loc)
            levels[currentLevel][CURRENT] += 1
            neighbors = G.neighbors(node)
            #if parent is not None:
            #    neighbors.remove(parent)
            for neighbor in neighbors:
                pos = make_pos(pos, neighbor, currentLevel + 1, node, vert_loc-vert_gap)
            return pos
        if levels is None:
            levels = make_levels({})
        else:
            levels = {l:{TOTAL: levels[l], CURRENT:0} for l in levels}
        vert_gap = height / (max([l for l in levels])+1)
        return make_pos({})