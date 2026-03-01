import math
import heapq
from collections import deque
from copy import deepcopy


# -----------------------------
# Task 6 Q1: Safety probabilities p(u,v)
# -----------------------------
P = {
    ("KTM", "JA"): 0.90,
    ("KTM", "JB"): 0.80,
    ("JA", "KTM"): 0.90,
    ("JA", "PH"): 0.95,
    ("JA", "BS"): 0.70,
    ("JB", "KTM"): 0.80,
    ("JB", "JA"): 0.60,
    ("JB", "BS"): 0.90,
    ("PH", "JA"): 0.95,
    ("PH", "BS"): 0.85,
    ("BS", "JA"): 0.70,
    ("BS", "JB"): 0.90,
    ("BS", "PH"): 0.85,
}

def build_graph_from_prob(P):
    """Convert probabilities to weights w(u,v)=-ln(p(u,v)) and build adjacency list."""
    graph = {}
    for (u, v), prob in P.items():
        w = -math.log(prob)
        graph.setdefault(u, []).append((v, w))
    return graph

def dijkstra_safest_path(P, start, goal):
    """
    Safest path = maximize product of probabilities.
    Transform to shortest path with w=-ln(p) and run Dijkstra.
    Returns: (path_list, safety_product, total_cost)
    """
    graph = build_graph_from_prob(P)

    dist = {start: 0.0}
    parent = {start: None}
    pq = [(0.0, start)]

    while pq:
        cur_dist, u = heapq.heappop(pq)
        if u == goal:
            break
        if cur_dist > dist.get(u, float("inf")):
            continue

        for v, w in graph.get(u, []):
            nd = cur_dist + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))

    if goal not in dist:
        return None, 0.0, float("inf")

    # Reconstruct path
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()

    # Compute safety product along path
    safety = 1.0
    for i in range(len(path) - 1):
        safety *= P[(path[i], path[i + 1])]

    return path, safety, dist[goal]


path, safety, cost = dijkstra_safest_path(P, "KTM", "BS")

print("Safest path:", " -> ".join(path))
print("Safety (product):", round(safety, 5))
print("Transformed cost (-ln product):", round(cost, 5))



def add_reverse_edges(capacity):
    """Ensure every edge u->v has a reverse edge v->u initialized to 0."""
    for u in list(capacity.keys()):
        for v in list(capacity[u].keys()):
            capacity.setdefault(v, {})
            capacity[v].setdefault(u, 0)

def edmonds_karp(capacity, source, sink):
    # Make sure reverse edges exist
    add_reverse_edges(capacity)

    flow = 0

    while True:
        parent = {source: None}
        queue = deque([source])

        # BFS to find augmenting path
        while queue and sink not in parent:
            u = queue.popleft()
            for v, cap_uv in capacity[u].items():
                if v not in parent and cap_uv > 0:
                    parent[v] = u
                    queue.append(v)

        # No augmenting path
        if sink not in parent:
            break

        # Find bottleneck (min residual capacity) along the path
        path_flow = float("inf")
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, capacity[u][v])
            v = u

        # Augment flow + update residual graph
        v = sink
        while v != source:
            u = parent[v]
            capacity[u][v] -= path_flow
            capacity[v][u] += path_flow
            v = u

        flow += path_flow

    return flow


# ---- DATASET (capacities) ----
capacity = {
    "KTM": {"JA": 10, "JB": 15},
    "JA": {"PH": 8, "BS": 5},
    "JB": {"JA": 4, "BS": 12},
    "PH": {"BS": 6},
    "BS": {}
}

# (optional) keep original safe
cap_copy = deepcopy(capacity)

maxflow = edmonds_karp(cap_copy, "KTM", "BS")
print("Maximum Flow:", maxflow)