import networkx as nx
import plotly.graph_objects as go
import kspice

project_path = "C:/K-Spice Test Projects/DemoProject"

timeline = "Tutorial"
mdlFile = "KSpiceTutorial Model"
prmFile = "KSpiceTutorial Model"
valFile = "KSpiceTutorial Model"

# instanciate the simulator object
sim = kspice.Simulator(project_path)

# open the project and load the timeline
tl = sim.activate_timeline(timeline)
tl.load(mdlFile, prmFile, valFile)

# initialize the timeline
tl.initialize()
selected_app = tl.applications[0].name

# Create an empty graph
graph = nx.Graph()


# get all blocks on first application (Process Model)
block_names = tl.get_block_names(selected_app)
blocks = tl.get_blocks(selected_app, block_names)

# browse all blocks and add edges to the graph
for block in blocks:
    for connection in block.input_connections:
        graph.add_edge(connection.source_block, connection.destination_block)
        
# visualize the graph
def plot_graph(graph):

    # Step 2: Set positions for each node using NetworkX's layout algorithms
    pos = nx.spring_layout(graph)  # Spring layout positions

    # Step 3: Extract edges and nodes with their positions for Plotly
    edge_x = []
    edge_y = []

    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Extract node positions and labels
    node_x = []
    node_y = []
    node_text = []

    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f'Node {node}')  # Custom label for each node

    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    # Set node color based on degree (number of connections)
    node_adjacencies = []
    for node in graph.adjacency():
        node_adjacencies.append(len(node[1]))

    node_trace.marker.color = node_adjacencies

    # Step 4: Create the final Plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='NetworkX Graph with Plotly Visualization',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig.show()

plot_graph(graph)
print("end")