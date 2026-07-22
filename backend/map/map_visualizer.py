import os
import osmnx as ox

FILE_PATH = os.path.join("data", "map.graphml")

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
        return

    except ImportError:
        print("[!] Missing required libraries for interactive mapping.")
        print("[*] Please run in your terminal: pip install folium mapclassify geopandas matplotlib")
        print("[*] Falling back to static image...")
    except Exception as exc:
        print(f"[!] Could not generate interactive graph: {exc}")
        print("[*] Attempting static image fallback...")

    try:
        ox.plot_graph(G, edge_color="#444444", bgcolor="#111111", show=True)
    except ImportError:
        print("[!] matplotlib is not installed. Static graph plotting is not available.")
        print("[*] Install it via: pip install matplotlib")
    except Exception as exc:
        print(f"[!] Static plotting failed: {exc}")