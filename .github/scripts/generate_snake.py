import os
import requests
from bs4 import BeautifulSoup
import random
import heapq

def fetch_grid(username):
    url = f'https://github.com/users/{username}/contributions'
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to fetch contributions")
    soup = BeautifulSoup(r.text, 'html.parser')
    tbody = soup.find('tbody')
    if not tbody:
        raise Exception("No tbody found")
    rows = tbody.find_all('tr')
    
    grid = []
    for r_idx, row in enumerate(rows):
        cells = row.find_all('td', class_='ContributionCalendar-day')
        row_data = []
        for cell in cells:
            level = cell.get('data-level')
            if level is not None:
                row_data.append(int(level))
        if row_data:
            grid.append(row_data)
    return grid

def astar(start, goal, grid):
    rows = len(grid)
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            break
            
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_node = (current[0] + dx, current[1] + dy)
            x, y = next_node
            if 0 <= y < rows and 0 <= x < len(grid[y]):
                if grid[y][x] == 0:
                    new_cost = cost_so_far[current] + 1
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + heuristic(goal, next_node)
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current
                        
    if goal not in came_from:
        return []
        
    path = []
    curr = goal
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

def generate_svg():
    username = "SRC9060"
    grid = fetch_grid(username)
    if not grid or len(grid) != 7:
        raise Exception("Invalid grid dimensions")
        
    rows = len(grid)
    cols = max(len(r) for r in grid)
    
    cell_size = 10
    gap = 4
    step_size = cell_size + gap
    width = cols * step_size + gap
    height = rows * step_size + gap
    
    colors = {
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353"
    }
    
    empty_cells = [(x, y) for y in range(rows) for x in range(len(grid[y])) if grid[y][x] == 0]
    
    if not empty_cells:
        raise Exception("No empty cells to navigate")
        
    current = random.choice(empty_cells)
    path = [current]
    
    food_keyframes = []
    
    for _ in range(6):
        candidates = [c for c in empty_cells if abs(c[0]-current[0]) + abs(c[1]-current[1]) > 15]
        if not candidates:
            candidates = empty_cells
        target = random.choice(candidates)
        subpath = astar(current, target, grid)
        if subpath:
            start_step = len(path) - 1 # starts appearing when snake leaves previous target
            path.extend(subpath)
            end_step = len(path) - 1 # eaten at this step
            food_keyframes.append({
                "x": target[0],
                "y": target[1],
                "start": max(0, start_step),
                "end": end_step
            })
            current = target
            
    if path:
        subpath = astar(current, path[0], grid)
        if subpath:
            start_step = len(path) - 1
            path.extend(subpath)
            end_step = len(path) - 1
            food_keyframes.append({
                "x": path[0][0],
                "y": path[0][1],
                "start": start_step,
                "end": end_step
            })

    snake_length = 6
    num_frames = len(path)
    if num_frames == 0:
        raise Exception("No path could be generated")
        
    padded_path = [path[0]] * snake_length + path
    
    css = ""
    for seg_idx in range(snake_length):
        css += f"@keyframes move-seg-{seg_idx} {{\n"
        for i in range(num_frames):
            percent = (i / max(1, num_frames - 1)) * 100
            pos_index = i + (snake_length - 1 - seg_idx)
            px = padded_path[pos_index][0] * step_size + gap
            py = padded_path[pos_index][1] * step_size + gap
            css += f"  {percent:.2f}% {{ transform: translate({px}px, {py}px); }}\n"
        css += "}\n"
        
    css += "@keyframes move-food {\n"
    for i, frame in enumerate(food_keyframes):
        start_pct = (frame["start"] / max(1, num_frames - 1)) * 100
        end_pct = (frame["end"] / max(1, num_frames - 1)) * 100
        px = frame["x"] * step_size + gap
        py = frame["y"] * step_size + gap
        
        if i == 0 and start_pct > 0:
            css += f"  0% {{ opacity: 0; transform: translate(0px, 0px); }}\n"
            
        css += f"  {start_pct:.2f}% {{ transform: translate({px}px, {py}px); opacity: 1; }}\n"
        css += f"  {end_pct - 0.01:.2f}% {{ transform: translate({px}px, {py}px); opacity: 1; }}\n"
        css += f"  {end_pct:.2f}% {{ opacity: 0; }}\n"
    css += "}\n"
        
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<style>
.bg {{ fill: #0d1117; }}
.cell {{ rx: 2; ry: 2; width: {cell_size}px; height: {cell_size}px; }}
{css}
</style>
<rect width="100%" height="100%" class="bg" />
<g id="grid">
'''
    for y in range(rows):
        for x in range(len(grid[y])):
            lvl = grid[y][x]
            px = x * step_size + gap
            py = y * step_size + gap
            svg += f'<rect class="cell" x="{px}" y="{py}" fill="{colors[lvl]}" />\n'
            
    svg += '</g>\n<g id="snake">\n'
    
    dur = max(5, num_frames * 0.1)
    svg += f'<rect class="cell" x="0" y="0" fill="#e2b3ff" style="animation: move-food {dur}s linear infinite; opacity: 0; rx: 5; ry: 5;" />\n'
    
    snake_colors = ["#00ffff", "#00e0ff", "#00c0ff", "#00a0ff", "#0080ff", "#0060ff"]
    for seg_idx in range(snake_length):
        svg += f'<rect class="cell" x="0" y="0" fill="{snake_colors[seg_idx]}" style="animation: move-seg-{seg_idx} {dur}s linear infinite;" />\n'
        
    svg += '</g>\n</svg>'
    
    os.makedirs("dist", exist_ok=True)
    with open("dist/contribution-snake.svg", "w") as f:
        f.write(svg)
    print(f"Generated successfully: dist/contribution-snake.svg with {num_frames} frames.")

if __name__ == "__main__":
    generate_svg()
