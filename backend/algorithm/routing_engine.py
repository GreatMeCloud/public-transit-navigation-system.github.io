import os
import networkx as nx
import osmnx as ox
import folium

# Set up osmnx configuration
try:
    ox.config(log_console=True, use_cache=False)
except AttributeError:
    print("OSMnx configuration failed. Please ensure you have the correct version of OSMnx installed.")
    ox.settings.use_cache = True
    ox.settings.log_console = False

FILE_PATH = os.path.join ("data", "map.graphml")

def prepare_graph_for_routing (G):
    """
    Prepare the graph for routing by adding edge speeds and travel times
    """

    # Add edge speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G

def heuristic_time (u, v, graph):
    """
    Calculate the heuristic time between two nodes
    """

    u_data = graph.nodes[u]
    v_data = graph.nodes[v]

    # Calculate the Euclidean distance between the two nodes
    distance = ox.distance.euclidean_dist_vec(u_data['y'], u_data['x'], v_data['y'], v_data['x'])

    # Assume an average speed of 80 km/h (22.22 m/s)
    max_speed_mps = 22.22  # m/s

    # Calculate the heuristic time in seconds
    estimated_time = distance / max_speed_mps

    return estimated_time

def find_route (G, origin_coord, dest_coord):
    """
    Find the shortest route between two coordinates using A* algorithm
    """

    print (f"[*] Pickup coordinates: {origin_coord}")
    print (f"[*] Destination coordinates: {dest_coord}")

    # 1. Pull the GPS coordinates of the user to the nearest nodes in the graph
    orig_node = ox.distance.nearest_nodes(G, origin_coord[1], origin_coord[0])
    dest_node = ox.distance.nearest_nodes(G, dest_coord[1], dest_coord[0])

    # 2. Use try_except to handle cases where no path is found
    try:
        print ("[*] Calculating the path of A* algorithm...")

        # Caution: Weight should be 'travel_time' to consider travel time instead of distance
        route_nodes = nx.astar_path(
            G,
            orig_node,
            dest_node,
            heuristic=lambda u, v: heuristic_time(u, v, G),
            weight='travel_time'
        )

        # 3. Calculating the Estimated Time (ETA)
        total_time = nx.classes.function.path_weight (G, route_nodes, weight='travel_time')
        total_length = nx.classes.function.path_weight (G, route_nodes, weight='length')

        print ("\n" + "=" * 40)
        print (" ROUTING RESULTS ".center(40, "="))
        print (f"- Route passing through: {len(route_nodes)} nodes")
        print (f"- Distance: {total_length / 1000:.2f} km")
        print (f"- Estimated Time of Arrival (ETA): {total_time / 60:.1f} minutes")
        print ("=" * 40 + "\n")

        return route_nodes

    except nx.NetworkXNoPath:
        print ("[!] No path found between the specified coordinates.")
        return None

def draw_route_on_map (G, route_nodes):
    """
    Draw the route on a folium map
    """

    if route_nodes is None:
        print ("[!] No route to draw on the map.")
        return None

    print ("[*] Drawing the route on the interaction map...")

    try:
        # Using the default drawing route of OSMnx by Folium
        m = ox.plot_route_folium (G, route_nodes, route_color="red", weight=5, opacity=0.8)

        output_file = "route_map.html"
        m.save (output_file)
        print (f"[+] Successfully created the map! Please open the file '{output_file}' in your browser to view the route.")

        # Auto open the map in the default web browser
        import webbrowser
        webbrowser.open ('file://' + os.path.realpath(output_file))

    except Exception as e:
        print (f"[!] Failed to draw the route on the map: {e}")

if __name__ == "__main__":
    # 1. Load the graph from the GraphML file
    if not os.path.exists(FILE_PATH):
        print (f"[!] GraphML file not found at '{FILE_PATH}'. Please ensure the file exists.")
        exit(1)

    G = ox.load_graphml(FILE_PATH)

    # 2. Prepare the graph for routing
    G = prepare_graph_for_routing(G)

    # 3. Run the algorithm to find the route between two coordinates
    # Example coordinates (latitude, longitude)
    origin_coord = (37.7749, -122.4194)  # San Francisco, CA
    dest_coord = (37.8044, -122.2711)  # Oakland, CA

    route = find_route(G, origin_coord, dest_coord)

    # 4. Draw the route on the map
    draw_route_on_map(G, route)
    
