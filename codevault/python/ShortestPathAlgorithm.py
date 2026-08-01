# Auto-generated Code Vault for 'ShortestPathAlgorithm' [Python]

import sys
import heapq

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def add_node(self, node):
        self.nodes.add(node)
        if node not in self.edges:
            self.edges[node] = []

    def add_edge(self, node1, node2, weight):
        self.edges[node1].append((node2, weight))
        self.edges[node2].append((node1, weight))  # comment this line for directed graph

    def dijkstra(self, start_node):
        distances = {node: sys.maxsize for node in self.nodes}
        distances[start_node] = 0
        priority_queue = [(0, start_node)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.edges[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))

        return distances


def main():
    graph = Graph()
    nodes = ['A', 'B', 'C', 'D', 'E', 'F']
    edges = [
        ('A', 'B', 4),
        ('A', 'C', 2),
        ('B', 'C', 5),
        ('B', 'D', 10),
        ('C', 'E', 3),
        ('E', 'D', 4),
        ('D', 'F', 11)
    ]

    for node in nodes:
        graph.add_node(node)

    for node1, node2, weight in edges:
        graph.add_edge(node1, node2, weight)

    distances = graph.dijkstra('A')
    print("Shortest distance from node 'A' to node 'F':", distances['F'])


if __name__ == "__main__":
    main()
