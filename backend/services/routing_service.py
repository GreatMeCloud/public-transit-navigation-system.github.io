from map.map_loader import load_local_map
from algorithm.routing_engine import (
    prepare_graph_for_routing,
    find_route,
    draw_route_on_map,
)

class RoutingService:

    def __init__(self):

        G = load_local_map() #NetworkX Graph that contains nodes and edges

        self.graph = prepare_graph_for_routing(G) #Preprocessing

    def get_route(self, origin, destination): #argument origin and destination are tuples that store latitude and longitude 
        
        route_nodes = find_route(
            self.graph,
            origin,
            destination,
        ) #Get nodes numbers

        #TEST
        #Display map
        #draw_route_on_map(self.G, route_nodes)

        #If there's no route
        if route_nodes is None:
            return {
                "success": False,
                "message": "No route found."
            }

        coordinates = []

        #Path traversal
        for node in route_nodes:
            #Add coordinates of the node
            coordinates.append({
                "lat": self.graph.nodes[node]["y"],
                "lon": self.graph.nodes[node]["x"],
            })

        return {
            "success": True,
            "coordinates": coordinates,
        }