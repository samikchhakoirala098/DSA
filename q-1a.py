
from math import gcd
from collections import defaultdict

def max_points_on_line(points):
    n = len(points)
    if n <= 2:
        return n

    best = 1
    for i in range(n):
        slopes = defaultdict(int)
        dup = 1
        local = 0

        x1, y1 = points[i]
        for j in range(i + 1, n):
            x2, y2 = points[j]
            dx, dy = x2 - x1, y2 - y1

            if dx == 0 and dy == 0:
                dup += 1
                continue

            g = gcd(abs(dx), abs(dy))
            dx //= g
            dy //= g

            # normalise sign
            if dx < 0:
                dx, dy = -dx, -dy
            if dx == 0:
                dy = 1
            if dy == 0:
                dx = 1

            slopes[(dy, dx)] += 1
            local = max(local, slopes[(dy, dx)])

        best = max(best, local + dup)

    return best

print(max_points_on_line([[1,1],[2,2],[3,3]]))  # 3
print(max_points_on_line([[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]))  # 4
print(max_points_on_line([[0,0],[0,0],[1,1]]))  # 3 (duplicates)
print(max_points_on_line([[1,0],[2,0],[3,0],[4,1]]))  # 3 (horizontal)
