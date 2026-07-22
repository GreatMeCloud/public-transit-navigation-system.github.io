import os
import osmnx as ox

def configure_osmnx():
    """Configure OSMnx settings based on the installed version."""
    try:
        ox.config(use_cache=True, log_console=True)
    except AttributeError:
        ox.settings.use_cache = True
        ox.settings.log_console = True

configure_osmnx()

FILE_PATH = os.path.join("data", "map.graphml")
AREA_NAME = "Vaughan, Ontario, Canada" 

def acquire_map_data():
    """Download map data from the internet and save it to a file"""
    print(f"[*] Downloading road network data for: {AREA_NAME}...")
    # network_type='drive' filters out pedestrian paths, keeping only drivable roads
    G = ox.graph_from_place(AREA_NAME, network_type="drive")
    
    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)

    # Save the graph to a graphml file
    ox.save_graphml(G, filepath=FILE_PATH)
    print(f"[+] Map successfully saved to: {FILE_PATH}")
    return G

def load_local_map():
    """Load the map from a local file if it exists"""
    if not os.path.exists(FILE_PATH):
        return acquire_map_data()
    
    print(f"[*] Loading map from local file: {FILE_PATH}...")
    return ox.load_graphml(FILE_PATH)

def inspect_graph(G):
    """Analyze basic parameters of the map graph"""
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)
    
    print("\n" + "="*40)
    print(" GRAPH INFORMATION ".center(40, "="))
    print(f"- Number of nodes (intersections): {num_nodes}")
    print(f"- Number of edges (street segments): {num_edges}")
    
    # Extract a random node to view its data structure
    sample_node = list(G.nodes(data=True))[0]
    print(f"- Sample Node Structure: ID {sample_node[0]} -> {sample_node[1]}")
    
    # Extract a random edge
    sample_edge = list(G.edges(data=True))[0]
    print(f"- Sample Edge Structure: From {sample_edge[0]} to {sample_edge[1]} ->")
    print(f"  + Street name: {sample_edge[2].get('name', 'Unnamed')}")
    print(f"  + Length: {sample_edge[2].get('length')} meters")
    print(f"  + Max speed: {sample_edge[2].get('maxspeed', 'No limit')}")
    print("="*40 + "\n")

def visualize_graph(G):
    """Draw an interactive map of the street network"""
    print("[*] Generating interactive map...")
    try:
        # For OSMnx 2.x and newer, use GeoPandas explore()
        try:
            nodes, edges = ox.convert.graph_to_gdfs(G)
        except AttributeError:
            # OSMnx 1.x fallback
            nodes, edges = ox.graph_to_gdfs(G)
        
        # Create interactive map using folium via geopandas explore()
        # You can change tiles to "CartoDB positron" for a light theme
        m = edges.explore(color="cyan", weight=2, tiles="CartoDB dark_matter")
        
        html_path = os.path.join(os.path.dirname(FILE_PATH), "interactive_map.html")
        m.save(html_path)
        print(f"[+] Interactive map successfully saved to: {html_path}")
        
        # Automatically open it in the default web browser
        import webbrowser
        webbrowser.open('file://' + os.path.realpath(html_path))
        
    except ImportError:
        print("[!] Missing required libraries for interactive mapping.")
        print("[*] Please run in your terminal: pip install folium mapclassify geopandas")
        print("[*] Falling back to static image...")
        ox.plot_graph(G, edge_color="#444444", bgcolor="#111111", show=True)
    except Exception as exc:
        print(f"[!] Could not generate interactive graph: {exc}")

if __name__ == "__main__":
    # 1. Load/Download the map
    G = load_local_map()
    
    # 2. Check the internal data structure
    inspect_graph(G)
    
    # 3. Display the interactive network
    visualize_graph(G)
