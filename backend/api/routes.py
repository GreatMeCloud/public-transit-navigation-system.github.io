from fastapi import APIRouter
from services.routing_service import RoutingService

#Each file has its own router
router = APIRouter() #Create a router object
#will add "app.include_router(router)" to main.py 

routing_service = RoutingService() #Create RoutingService object

@router.get("/route") #Decorator
#When someone is accessing to the /route page, the following codes will be excuted

#Define a function to handle the request
def get_route(
    #arguments
    start_lat: float, #Start latitude
    start_lon: float, #Start longitude
    end_lat: float, #End latitude
    end_lon: float, #End longitude
):
    return routing_service.get_route(
    (start_lat, start_lon),
    (end_lat, end_lon),
    )