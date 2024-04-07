from typing import List, Tuple, Dict, Any


# def remove_duplicates(l: List) -> List:
#     return list(set(l))


def dijkstra(graph: Dict[Any, Dict[Any, int]], source: Any) -> Dict[Any, Tuple[int, Any]]:
    """
    Returns a dictionary of shortest distances from the source node to all other nodes in the graph.
    The dictionary also contains the parent node for each node, which can be used to reconstruct the
    shortest path from the source node to a specific destination node.

    :param graph: The weighted graph represented as a dictionary of dictionaries. The keys of the
                  outer dictionary represent the nodes in the graph, and the inner dictionaries
                  represent the edges emanating from each node. The keys of the inner dictionaries
                  represent the destination nodes of the edges, and the values represent the weights
                  of the edges.
    :param source: The source node from which to compute the shortest distances.
    :return: A dictionary of shortest distances from the source node to all other nodes in the graph,
             along with the parent node for each node.
    """
    distances = {node: float("inf") for node in graph}
    distances[source] = 0
    parents = {node: None for node in graph}

    unvisited = set(graph)
    while unvisited:
        current = min(unvisited, key=lambda x: distances[x])
        unvisited.remove(current)

        for neighbor, weight in graph[current].items():
            if weight + distances[current] < distances[neighbor]:
                distances[neighbor] = weight + distances[current]
                parents[neighbor] = current
    return distances, parents


# Create a weighted graph as a dictionary of dictionaries
graph = {
    "A": {"B": 2, "C": 4},
    "B": {"C": 1, "D": 3},
    "C": {"D": 4},
    "D": {"E": 2},
    "E": {}
}

# Compute the shortest distances from node "A" to all other nodes
distances, parents = dijkstra(graph, "A")

# Print the distances from node "A" to all other nodes
print(distances)

# Print the parent nodes for each node
print(parents)

#    # Where((distances, neighbor, weight, distances[neighbor]), Where(neighbor == 'C', LoopIterationTimes(30)))
