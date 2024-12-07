import customtkinter as ctk
import random

# Configure customtkinter
ctk.set_appearance_mode("dark")  # Dark mode interface
ctk.set_default_color_theme("blue")  # Blue theme

# Grid dimensions
GRID_SIZE = 10
CELL_SIZE = 60
NUM_OBSTACLES = 15

# Colors
COLORS = {
    "grid": "#333333",
    "obstacle": "#8c8c8c",
    "start": "#27ae60",
    "end": "#e74c3c",
    "path": "#3498db",
    "user_path": "#f39c12"
}

class PipeGame:
    def __init__(self, root):
        """Initialize the PipeGame application."""
        self.root = root
        self.root.title("Pipe Connection Game")
        self.root.geometry(f"{GRID_SIZE * CELL_SIZE + 200}x{GRID_SIZE * CELL_SIZE + 150}")

        self.mode = "auto"  # Game mode: 'auto' or 'manual'

        # Frame for UI elements
        self.frame = ctk.CTkFrame(root, corner_radius=10)
        self.frame.pack(padx=20, pady=20)

        # Canvas for the grid
        self.canvas = ctk.CTkCanvas(self.frame, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="#2c3e50")
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Mode selection button
        self.mode_button = ctk.CTkOptionMenu(self.frame, values=["Auto Play", "Manual Play"],
                                             command=self.change_mode)
        self.mode_button.grid(row=1, column=0, padx=10, pady=10)
        self.mode_button.set("Auto Play")

        # Play button for auto mode
        self.play_button = ctk.CTkButton(self.frame, text="Play", command=self.run_hill_climbing)
        self.play_button.grid(row=1, column=1, padx=10, pady=10)

        # Reset button
        self.reset_button = ctk.CTkButton(self.frame, text="Reset", command=self.reset_game)
        self.reset_button.grid(row=1, column=2, padx=10, pady=10)

        self.win_label = None  # Display winning message

        self.setup_game()
        self.win = False  # Winning state
        self.visited = set()  # Track visited nodes

    def setup_game(self):
        """Set up the game by initializing the grid, obstacles, and start/end points."""
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.obstacles = set()
        self.start = None
        self.end = None
        self.path = []

        self.create_grid()
        self.randomize_start_end()
        self.path_root = self.generate_path()
        self.place_obstacles()

        if self.mode == "manual" and not self.win:
            self.canvas.bind("<Button-1>", self.handle_manual_click)

    def create_grid(self):
        """Draw the grid on the canvas."""
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1, y1 = i * CELL_SIZE, j * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#34495e", fill=COLORS["grid"])

    def randomize_start_end(self):
        """Randomly generate start and end points on the grid."""
        while True:
            self.start = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            self.end = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if self.start != self.end:
                break

        self.draw_cell(self.start, COLORS["start"])
        self.draw_cell(self.end, COLORS["end"])

    def place_obstacles(self):
        """Place obstacles on the grid, avoiding the path, start, and end points."""
        def is_valid_obstacle(x, y):
            return (x, y) not in self.path and (x, y) != self.start and (x, y) != self.end

        while len(self.obstacles) < NUM_OBSTACLES:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if is_valid_obstacle(x, y):
                self.obstacles.add((x, y))
                self.draw_cell((x, y), COLORS["obstacle"])

    def generate_path(self):
        """Generate a path between start and end points.

        Returns:
            list: A list of coordinates representing the path.
        """
        path = []
        x1, y1 = self.start
        x2, y2 = self.end
        if x1 < x2:
            path.extend((x, y1) for x in range(x1, x2 + 1))
        elif x1 > x2:
            path.extend((x, y1) for x in range(x1, x2 - 1, -1))
        if y1 < y2:
            path.extend((x2, y) for y in range(y1, y2 + 1) if (x2, y) not in path)
        elif y1 > y2:
            path.extend((x2, y) for y in range(y1, y2 - 1, -1) if (x2, y) not in path)
        return path

    def draw_cell(self, pos, color):
        """Draw a cell on the grid with the specified color."""
        x, y = pos
        self.canvas.create_rectangle(
            x * CELL_SIZE, y * CELL_SIZE,
            (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
            fill=color, outline="black", width=2
        )

    def run_hill_climbing(self):
        """Run the hill-climbing algorithm to find a path."""
        try:
            self.visited = set()
            if self.mode == "auto":
                self.hill_climbing(self.start, self.end)
            if self.path:
                for x, y in self.path:
                    if (x, y) == self.end or (x, y) == self.start:
                        continue
                    self.draw_cell((x, y), COLORS["path"])
                if self.end in self.path:
                    self.show_message("Win!")
                else:
                    self.show_message("No valid path found.")
            else:
                self.show_message("No valid path found.")
        except Exception as e:
            print(e)

    def hill_climbing(self, start, end):
        """Perform the hill-climbing algorithm.

        Args:
            start (tuple): The starting node.
            end (tuple): The target node.
        """
        current = start
        if start == self.start:
            self.path = [current]
        else:
            path = [current]

        while current != end:
            self.visited.add(current)
            neighbors = self.get_neighbors(current)
            neighbors = [n for n in neighbors if n not in self.obstacles and n not in self.visited]

            if not neighbors:
                return None

            next_node = min(neighbors, key=lambda n: self.heuristic(n, end))
            if self.heuristic(next_node, end) >= self.heuristic(current, end):
                result = self.handle_local_maximum(neighbors, end)
                if result is None:
                    return None
                if start == self.start:
                    self.path += result
                    return
                else:
                    path += result
                    return path
            if start == self.start:
                self.path.append(next_node)
                current = next_node
            else:
                path.append(next_node)
                current = next_node
        if start != self.start:
            return path

    def handle_local_maximum(self, neighbors, end):
        """Handle cases of local maxima in the hill-climbing algorithm.

        Args:
            neighbors (list): Neighboring nodes.
            end (tuple): The target node.

        Returns:
            list or None: A valid path or None if no path is found.
        """
        paths = []
        for neighbor in neighbors:
            temp_path = self.hill_climbing(neighbor, end)
            if temp_path is not None:
                paths.append(temp_path)
        if paths:
            return min(paths, key=len)  # Choose the shortest path
        return None

    def handle_manual_click(self, event):
        """Handle mouse clicks for manual path creation."""
        if self.start and self.end and not self.win:
            x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
            if (x, y) not in self.obstacles and (x, y) not in self.path:
                self.draw_cell((x, y), COLORS["user_path"])
                self.path.append((x, y))

                # Check if the user reached the end point
                if (x, y) == self.end:
                    self.win = True
                    self.show_message("Win!")
                    self.canvas.unbind("<Button-1>")  # Disable further drawing after winning

    def show_message(self, message):
        """Display a message to the user."""
        if hasattr(self, "win_label") and self.win_label:
            self.win_label.destroy()
        self.win_label = ctk.CTkLabel(self.frame, text=message, text_color="white", font=("Arial", 20))
        self.win_label.grid(row=2, column=0, columnspan=3, pady=10)

    def heuristic(self, node, end):
        """Calculate the heuristic value (Manhattan distance) between two points.

        Args:
            node (tuple): The current node.
            end (tuple): The target node.

        Returns:
            int: The Manhattan distance.
        """
        x1, y1 = node
        x2, y2 = end
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, node):
        """Get the valid neighbors of a node.

        Args:
            node (tuple): The current node.

        Returns:
            list: List of neighboring nodes.
        """
        x, y = node
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbors.append((nx, ny))
        return neighbors

    def change_mode(self, selected_mode):
        """Change the game mode between 'auto' and 'manual'.

        Args:
            selected_mode (str): The selected mode.
        """
        if selected_mode == "Auto Play":
            self.mode = "auto"
            self.canvas.unbind("<Button-1>")
        elif selected_mode == "Manual Play":
            self.mode = "manual"
        self.reset_game()

    def reset_game(self):
        """Reset the game to its initial state."""
        self.win = False  # Reset win state
        self.path = []
        self.visited = set()  # Clear visited nodes
        self.show_message(" ")
        self.setup_game()


# Run the game
root = ctk.CTk()
game = PipeGame(root)
root.mainloop()
