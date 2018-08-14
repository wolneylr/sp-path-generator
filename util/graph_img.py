import networkx as nx
import plotly.graph_objs as go
import plotly.plotly as py

class Graph:
    def __init__(self, graph, pos, path_list):
        G = graph
        # pos = nx.get_node_attributes(G, 'pos')


        dmin = 1
        #ncenter = 0

        for n in pos:
            x, y = pos[n]
            d = (x - 0.5) ** 2 + (y - 0.5) ** 2
            if d < dmin:
                #ncenter = n
                dmin = d

        # p = nx.single_source_shortest_path_length(G, ncenter)


        edge_trace_x = []
        edge_trace_y = []
        edge_trace_text = []

        for node1, node2, data in G.edges(data=True):
            #x0, y0 = G.node[node1]['pos']
            #x1, y1 = G.node[node2]['pos']
            edge_trace_x += [pos[node1][0],pos[node2][0], None]
            edge_trace_y += [pos[node1][1],pos[node2][1], None] 
            #edge_trace_x += [x0, x1, None]
            #edge_trace_y += [y0, y1, None]
            edge_info = "score: " + str(data['score'])
            edge_trace_text.append(edge_info)

        edge_trace = go.Scatter(
            x = edge_trace_x,
            y = edge_trace_y,
            text = edge_trace_text,
            line = dict(width=0.5,color='#888'),
            hoverinfo = 'text',
            mode = 'lines')

        node_trace_x = [pos[node][0] for node in G.nodes()]
        node_trace_y = [pos[node][1] for node in G.nodes()]
        
        node_trace_marker_color = []
        node_trace_text = []

        for node in G.nodes():
            #x, y = G.node[node]['pos']
            #node_trace_x.append(x)
            #node_trace_y.append(y)

            node_trace_marker_color.append(G.degree[node])
            node_info = '# of connections: ' + str(G.degree[node])
            node_info += '<br>' + 'first_pos: ' + str(node[0])
            if len(node) > 1:
                node_info += '<br>' + 'last_pos: ' + str(node[1])
                node_info += '<br>' + 'activation_length: ' + str(node[2])
                node_info += '<br>' + 'activation_percentage: ' + str(node[3])
                node_info += '<br>' + 'max_score: ' + str(G.node[node]["max_score"])
            node_trace_text.append(node_info) 
           
        #print(str(G.nodes()))
        #print(str(G.edges()))
        #print(str(G.adj.items()))
            

        node_trace = go.Scatter(
            x = node_trace_x,
            y = node_trace_y,
            text = node_trace_text,
            mode = 'markers',
            hoverinfo ='text',
            marker = dict(
                showscale = True,
                # colorscale options
                # 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
                # Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
                colorscale = 'Greens',
                reversescale = True,
                color = node_trace_marker_color,
                size = 10,
                colorbar = dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)
            )
        )

        fig = go.Figure(
            data = [edge_trace, node_trace],
            layout = go.Layout(
                title = '<br>Network graph made with Python',
                titlefont = dict(size = 16),
                showlegend = False,
                hovermode = 'closest',
                margin = dict(b = 20,l = 5,r = 5,t = 40),
                annotations=[dict(
                    text=  "Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> \
                    https://plot.ly/ipython-notebooks/network-graphs/</a>",
                    showarrow = False,
                    xref = "paper", 
                    yref = "paper",
                    x = 0.005, 
                    y=-0.002 
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        '''
        x_path=[]
        y_path=[]

        index_list = []

        for node in path_list:
            index_list.append(list(G.nodes()).index(node))

        for index in index_list:
            x_path.extend([fig['data'][0]['x'][3 * index], fig['data'][0]['x'][3 * index + 1], None])
            y_path.extend([fig['data'][0]['y'][3 * index], fig['data'][0]['y'][3 * index + 1], None])
            
        colored_edges = dict(type = 'scatter', 
                    mode = 'line',
                        line = dict(width = 2, color = 'red'), 
                        x = x_path, 
                        y = y_path)


        data = [colored_edges] + list(fig['data'])
        fig = dict(data = data, layout=fig['layout'])
        '''

        py.plot(fig, filename='sp_graph')


def main():
    Graph(None, None, None)

if __name__ == "__main__":
    main()
