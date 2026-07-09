# 👉source: https://osmnx.readthedocs.io/en/stable/index.html

# load specific OSM data for a given area

import osmnx as ox

def load_osm_data(position):
    north, south, east, west = position
    
    try:
        #graph object representing the road network in the specified bounding box
        graph = ox.graph_from_bbox(
            (north, south, east, west),
            network_type="drive"
        )
        return graph

    except Exception as e:
        print(f"Failed to load OSM data: {e}")
        return None

def save_osm_data(G, filename):
    try:
        ox.save_graphml(G, filename)
        print(f"Graph saved to {filename}")
    except Exception as e:
        print(f"Failed to save OSM data: {e}")

def load_graph(filename):
    try:
        graph = ox.load_graphml(filename)
        print(f"Graph loaded from {filename}")
        return graph
    except Exception as e:
        print(f"Failed to load graph: {e}")
        return None
