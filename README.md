# Navigation-system-for-public-transportation
A smart navigation system for public transportation that utilize real-world map data to optimize routes under simulated traffic conditions. The project explores graph algorithms, dynamic routing, ride-sharing, and efficient transportation planning.

## Contributors
- HenryHaiyang: Map front-end (the part that users can see and interact with)

- Tr4nQuang: Algorithm core (the brain of navigation)

- GreatMeCloud: Back-end and database (connecting the front-end and the algorithm)

## How to run
### please install:
``` 
pip install osmnx
```
```
pip install networkx
```

## Structure
Backend: OSMnx + NetworkX

Frontend: Undecided

asset/      → Icons/Styles

data/       → Files (raw/config/cache)

src/

  io/       → Data import/export (OSMnx)
  
  core/     → World (Graph + State) (NetworkX)
  
  algorithm → Pathfinding algorithms 
  
  view/     → Folium + UI + Interaction 

## Flow chart

```
OSMnx 
  ↓
io: import real-world map data
  ↓
core: build world map with nodes, etc.
  ↓
algorithm: pathfinding, etc.
  ↓
view: Display map & UI
```
