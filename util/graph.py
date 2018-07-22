import networkx as nx
import plotly.graph_objs as go
import plotly.plotly as py

G = nx.random_geometric_graph(15, 0.125)
pos = nx.get_node_attributes(G, 'pos')

dmin = 1
ncenter = 0

for n in pos:
    x, y = pos[n]
    d = (x - 0.5) ** 2 + (y - 0.5) ** 2
    if d < dmin:
        ncenter = n
        dmin = d

p = nx.single_source_shortest_path_length(G, ncenter)


edge_trace_x = []
edge_trace_y = []

for edge in G.edges():
    x0, y0 = G.node[edge[0]]['pos']
    x1, y1 = G.node[edge[1]]['pos']
    edge_trace_x += [x0, x1, None]
    edge_trace_y += [y0, y1, None]

edge_trace = go.Scatter3d(
    x = edge_trace_x,
    y = edge_trace_y,
    z = edge_trace_x,
    line = dict(width=0.5,color='#888'),
    hoverinfo = 'none',
    mode = 'lines')

node_trace_x = []
node_trace_y = []

for node in G.nodes():
    x, y = G.node[node]['pos']
    node_trace_x.append(x)
    node_trace_y.append(y)

node_trace_marker_color = []
node_trace_text = []

print(str(G.nodes()))
print(str(G.edges()))
print(str(G.adj.items()))

for node, adjacencies in G.adj.items():
    node_trace_marker_color.append(len(adjacencies))
    node_info = '# of connections: '+str(len(adjacencies))
    node_trace_text.append(node_info)

node_trace = go.Scatter3d(
    x = node_trace_x,
    y = node_trace_y,
    z = node_trace_x,
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

py.plot(fig, filename='networkx')
