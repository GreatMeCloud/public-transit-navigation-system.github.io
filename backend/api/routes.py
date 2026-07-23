from fastapi import APIRouter
from services.routing_service import RoutingService

router = APIRouter()

routing_service = RoutingService()

@router.get("/route")
def get_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
):
    return routing_service.get_route(
    (start_lat, start_lon),
    (end_lat, end_lon),
    )