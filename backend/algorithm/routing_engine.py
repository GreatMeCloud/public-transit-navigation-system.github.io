import os

import networkx as nx

import osmnx as ox

import folium


def configure_osmnx():
    """Configure OSMnx settings compatibly across versions."""
    try:
        ox.config(use_cache=True, log_console=True)
    except AttributeError:
        # older OSMnx exposes settings namespace
        try:
            ox.settings.use_cache = True
            ox.settings.log_console = True
        except Exception:
            # best-effort fallback; continue without raising
            pass


configure_osmnx()


# GraphML file inside backend/map/data (use absolute path)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE_PATH = os.path.join(BASE_DIR, "map", "data", "map.graphml")



def prepare_graph_for_routing (G):

    """
    
    Prepare the graph for routing by adding edge speeds and travel times.
    Accepts a networkx graph or a GraphML file path.
    
    """

    if isinstance(G, str):
        if not os.path.exists(G):
            raise FileNotFoundError(f"GraphML file not found at '{G}'")
        G = ox.load_graphml(G)

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

    # Calculate the Euclidean distance between the two nodes
    dy = u_data['y'] - v_data['y']
    dx = u_data['x'] - v_data['x']
    distance = (dx ** 2 + dy ** 2) ** 0.5



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

    # 1.a If the original coordinates are very far from their snapped nodes,
    # the destination may be outside the loaded graph. Detect that and return
    # a sentinel so callers can choose to use an external router (OSRM).
    def haversine_km(a, b):
        from math import radians, sin, cos, asin, sqrt
        lat1, lon1 = a
        lat2, lon2 = b
        R = 6371.0
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)
        x = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
        return 2*R*asin(min(1, sqrt(x)))

    orig_snap = (G.nodes[orig_node]["y"], G.nodes[orig_node]["x"])  # (lat, lon)
    dest_snap = (G.nodes[dest_node]["y"], G.nodes[dest_node]["x"])  # (lat, lon)

    # threshold (km) beyond which we consider a coordinate outside the graph
    OUTSIDE_THRESHOLD_KM = 50.0
    dist_orig = haversine_km(origin_coord, orig_snap)
    dist_dest = haversine_km(dest_coord, dest_snap)

    if dist_orig > OUTSIDE_THRESHOLD_KM or dist_dest > OUTSIDE_THRESHOLD_KM:
        print(f"[!] One or both coordinates are far outside the loaded graph (orig: {dist_orig:.1f} km, dest: {dist_dest:.1f} km).")
        return {
            "status": "outside_graph",
            "origin_coord": origin_coord,
            "dest_coord": dest_coord,
            "orig_snap": orig_snap,
            "dest_snap": dest_snap,
            "orig_node": orig_node,
            "dest_node": dest_node,
        }



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



def draw_route_on_map(G, route_nodes):

    """
    
    Draw the route accurately on a folium map by extracting edge geometries.
    
    """

    if not route_nodes or len(route_nodes) < 2:

        print("[!] Not enough nodes to draw a route (start and end might be the same).")

        return None


    print("[*] Drawing the route on the interaction map...")


    try:

        # 1. Get the exact coordinates for the start and end points
        
        start_coord = (G.nodes[route_nodes[0]]['y'], G.nodes[route_nodes[0]]['x'])

        end_coord = (G.nodes[route_nodes[-1]]['y'], G.nodes[route_nodes[-1]]['x'])
        

        # Initialize map
        
        m = folium.Map(location=start_coord, zoom_start=13)
        

        # 2. Extract the actual physical road curves (geometries) from the graph
        
        route_lines = []

        for i in range(len(route_nodes) - 1):

            u = route_nodes[i]

            v = route_nodes[i + 1]
            

            # OSMnx graphs can have multiple paths between the exact same nodes. 
            
            # We grab the edge data and pick the one with the shortest travel time.
            
            edge_data = G.get_edge_data(u, v)

            if edge_data:

                best_edge = min(edge_data.values(), key=lambda x: x.get('travel_time', float('inf')))
                

                # If the road curves, OSMnx stores a LineString geometry
                
                if 'geometry' in best_edge:

                    # Extract the coordinates from the LineString
                    
                    coords = [(lat, lon) for lon, lat in best_edge['geometry'].coords]

                    route_lines.extend(coords)


                else:

                    # If it's a perfectly straight road, just connect the two nodes
                    
                    route_lines.extend([

                        (G.nodes[u]['y'], G.nodes[u]['x']),

                        (G.nodes[v]['y'], G.nodes[v]['x'])

                    ])


        # 3. Draw the full route line
        
        if route_lines:

            folium.PolyLine(route_lines, color="#3388ff", weight=5, opacity=0.8).add_to(m)

        
        # 4. Add clear markers for Start and Destination
        
        folium.Marker(start_coord, popup="Start", icon=folium.Icon(color="green", icon="play")).add_to(m)

        folium.Marker(end_coord, popup="Destination", icon=folium.Icon(color="red", icon="stop")).add_to(m)

        
        # 5. FORCE the map to zoom correctly so the entire route is visible!

        m.fit_bounds([start_coord, end_coord])

        
        # Save and open

        output_file = "route_map.html"

        m.save(output_file)

        print(f"[+] Successfully created the map! Please open '{output_file}' in your browser.")

        
        import webbrowser

        webbrowser.open('file://' + os.path.realpath(output_file))

        
    except Exception as e:

        print(f"[!] Failed to draw the route on the map: {e}")



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

    origin_coord = (43.784, -79.525)  # Vaughan, Ontario, Canada

    dest_coord = (43.800, -79.500)  # Vaughan, Ontario, Canada



    route = find_route(G, origin_coord, dest_coord)



    # 4. Draw the route on the map

    draw_route_on_map(G, route)

    

