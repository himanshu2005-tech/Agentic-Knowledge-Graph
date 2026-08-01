# Auto-generated Code Vault for 'AStarPathfinding' [Python]

import heapq

class Node:
    def __init__(self, x, y, cost, parent=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class AStarPathfinding:
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal
        self.open_list = []
        self.closed_list = set()

    def is_valid(self, x, y):
        return 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]) and self.grid[x][y] != 1

    def heuristic(self, x, y):
        return abs(x - self.goal[0]) + abs(y - self.goal[1])

    def search(self):
        start_node = Node(self.start[0], self.start[1], 0)
        heapq.heappush(self.open_list, (start_node.cost + self.heuristic(start_node.x, start_node.y), start_node))

        while self.open_list:
            current_node = heapq.heappop(self.open_list)[1]

            if (current_node.x, current_node.y) == self.goal:
                path = []
                while current_node:
                    path.append((current_node.x, current_node.y))
                    current_node = current_node.parent
                return path[::-1]

            self.closed_list.add((current_node.x, current_node.y))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                x, y = current_node.x + dx, current_node.y + dy

                if self.is_valid(x, y) and (x, y) not in self.closed_list:
                    new_node = Node(x, y, current_node.cost + 1, current_node)
                    heapq.heappush(self.open_list, (new_node.cost + self.heuristic(new_node.x, new_node.y), new_node))

        return None

def main():
    grid = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0]
    ]
    start = (0, 0)
    goal = (4, 5)

    astar = AStarPathfinding(grid, start, goal)
    path = astar.search()

    if path:
        print("Path found:", path)
    else:
        print("No path found")

if __name__ == "__main__":
    main()
