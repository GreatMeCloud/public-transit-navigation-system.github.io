import os
import requests

# Import your engine (to make sure file routing_engine.py stay in the same folder)
from routing_engine import TaxiRouter

def get_osrm_route (orig_coord, dest_coord):
    """
    Get the route from OSRM API
    """
    lon1, lat1 = orig_coord[1], orig_coord[0]
    lon2, lat2 = dest_coord[1], dest_coord[0]

    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get (url, timeout=10)
        data = response.json()

        if data.get("code") == "Ok":
            route = data["routes"][0]

            # OSRM returns the distance (meters) and duration (seconds) of the route
            return {
                "status": "success",
                "distance_km": route["distance"] / 1000,  # Convert meters to kilometers
                "eta_minutes": route["duration"] / 60,    # Convert seconds to minutes
            }

        else:
            return {
                "status": "error",
                "message": data.get("code")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def compare_and_evaluate (my_result, api_result):
    """
    Compare and evaluate Correct / Incorrect base on the tolerance
    """

    print ("\n" + "=" * 50)
    print (" COMPARISON RESULTS ".center(50, "="))

    my_dist = my_result["distance_km"]
    my_eta = my_result["eta_minutes"]

    api_dist = api_result["distance_km"]
    api_eta = api_result["eta_minutes"]

    # calculate the absolute differences
    diff_dist = abs (my_dist - api_dist)
    diff_eta = abs (my_eta - api_eta)

    print (f"{'Specification':<15} | {'Your Result':<22} | {'OSRM API':<15}")
    print ("-" * 50)
    print (f"{'Distance (km)':<15} | {my_dist:>18.2f} km | {api_dist:>12.2f} km")
    print (f"{'ETA (minutes)':<15} | {my_eta:>18.1f} min | {api_eta:>12.1f} min")
    print ("-" * 50)

    print (f"\n[*] Distance difference: {diff_dist:.2f} km")
    print (f"[*] ETA difference: {diff_eta:.1f} minutes")

    # EVALUATION CRITERIA (Customizable)
    # If ETA difference is less than 3 minutes OR less than 10%, consider it correct
    eta_tolerance = 3.0  # minutes

    if diff_eta <= eta_tolerance:
        print ("\n>>> CONCLUSION: [ CORRECT ] (Accurate)")
        print (f">>> Feedback: Your algorith perfeorms very closely to the real-world system! The time difference is only {diff_eta:.1f} minutes.")

    else:
        print ("\n>>> CONCLUSION: [ INCORRECT ] (Inaccurate)")
        print (f">>> Feedback: Your algorithm has a significant difference from the real-world system. The time difference is {diff_eta:.1f} minutes, which exceeds the tolerance of {eta_tolerance:.1f} minutes.")

if __name__ == "__main__":
    # 1. Initialize the Engine
    MAP_FILE = os.path.join ("data", "map.graphml")

    try:
        router = TaxiRouter (MAP_FILE)
    except FileNotFoundError:
        print (f"[!] GraphML file not found at '{MAP_FILE}'. Please ensure the file exists.")
        exit(1)

    # 2. Define the coordinates for the test
    orig_coord = (43.784, -79.525)  # Vaughan, Canada
    dest_coord = (43.800, -79.500)

    # 3. Run your routing algorithm
    print ("[*] Running your routing algorithm...")
    my_result = router.get_route (orig_coord, dest_coord)

    # 4. Call the OSRM API
    print ("[*] Calling the OSRM API to get the data...")
    api_result = get_osrm_route (orig_coord, dest_coord)

    #5. Compare and evaluate the results
    if my_result["status"] == "success" and api_result["status"] == "success":
        compare_and_evaluate (my_result, api_result)

    else:
        print ("[!] Cannot compare results because one of two system cannot find the path")
