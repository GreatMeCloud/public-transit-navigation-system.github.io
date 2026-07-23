from map.map_loader import load_local_map
from algorithm.routing_engine import (
    prepare_graph_for_routing,
    find_route,
)

class RoutingService:

    def __init__(self):

        G = load_local_map()

        self.graph = prepare_graph_for_routing(G)

    def get_route(self, origin, destination):

        route_nodes = find_route(
            self.graph,
            origin,
            destination,
        )

        if route_nodes is None:
            return {
                "success": False,
                "message": "No route found."
            }

        coordinates = []

        for node in route_nodes:
            coordinates.append({
                "lat": self.graph.nodes[node]["y"],
                "lon": self.graph.nodes[node]["x"],
            })

        return {
            "success": True,
            "coordinates": coordinates,
        }