from heapq import heappop as pop
from heapq import heappush as push

from .Constants import DELTA


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Return the Manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(
    came_from: dict[tuple[int, int], tuple[int, int]], end: tuple[int, int]
) -> list[tuple[int, int]]:
    """Reconstruct the path from start to the end."""
    node = end
    path: list[tuple[int, int]] = [node]
    while node in came_from:
        path.append(came_from[node])
        node = came_from[node]
    path.reverse()
    return path


def find_path(
    maze: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
    best_only=True
) -> list[list[tuple[int, int]]]:
    """Find the shortest path from start to end in the maze.
    start and end not necessarily
    the start and end of the maze, but any two cells.
    """

    def astar(maze: list[list[int]],
              start: tuple[int, int],
              end: tuple[int, int],
              result: list[tuple[int, int]] | None = None,
              ) -> list[tuple[int, int]]:
        if result is None:
            result = []
        last_path: set[tuple[int, int]] = set(result)
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score = {start: 0}
        queue: list[tuple[int, tuple[int, int]]] = []
        push(queue, (manhattan(start, end), start))
        while queue:
            best: tuple[int, tuple[int, int]] = pop(queue)
            node: tuple[int, int] = best[1]
            if node == end and not reconstruct_path(came_from, end) == result:
                return reconstruct_path(came_from, end)

            for i in range(4):
                mask: int = 1 << i
                if maze[node[0]][node[1]] & mask:
                    delta = DELTA[mask]
                    next_node: tuple[int, int] = (
                        node[0] + delta[0],
                        node[1] + delta[1],
                    )
                    if not (
                        0 <= next_node[0] < len(maze)
                        and 0 <= next_node[1] < len(maze[0])
                    ):
                        continue
                    penalty: int = 10000 * (next_node in last_path)
                    new_g = g_score[node] + 1 + penalty

                    if next_node not in g_score or new_g < g_score[next_node]:
                        g_score[next_node] = new_g
                        came_from[next_node] = node
                        f_score = new_g + manhattan(next_node, end)
                        push(queue, (f_score, next_node))
        return []
    paths: list[list[tuple[int, int]]] = []
    result1: list[tuple[int, int]] = astar(maze, start, end)
    result2: list[tuple[int, int]]
    if not best_only:
        result2 = astar(maze, start, end, result=result1)
    else:
        result2 = []
    paths = [result1, result2]
    return paths
