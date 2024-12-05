import customtkinter as ctk
import random

# Cấu hình customtkinter
ctk.set_appearance_mode("dark")  # Giao diện tối
ctk.set_default_color_theme("blue")  # Chủ đề màu xanh

# Kích thước lưới
GRID_SIZE = 10
CELL_SIZE = 60
NUM_OBSTACLES = 15

# Màu sắc
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
        self.root = root
        self.root.title("Game Kết Nối Đường Ống")
        self.root.geometry(f"{GRID_SIZE * CELL_SIZE + 200}x{GRID_SIZE * CELL_SIZE + 150}")

        # Biến chế độ chơi
        self.mode = "auto"  # 'auto', 'manual'

        # Khung hiển thị
        self.frame = ctk.CTkFrame(root, corner_radius=10)
        self.frame.pack(padx=20, pady=20)

        # Canvas lưới
        self.canvas = ctk.CTkCanvas(self.frame, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="#2c3e50")
        self.canvas.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Nút chế độ chơi
        self.mode_button = ctk.CTkOptionMenu(self.frame, values=["Máy tự chơi", "Người chơi tự chơi"],
                                            command=self.change_mode)
        self.mode_button.grid(row=1, column=0, padx=10, pady=10)
        self.mode_button.set("Máy tự chơi")

        # Nút bắt đầu cho chế độ máy
        self.play_button = ctk.CTkButton(self.frame, text="Chơi", command=self.run_hill_climbing)
        self.play_button.grid(row=1, column=1, padx=10, pady=10)

        # Nút chơi lạikKK
        self.reset_button = ctk.CTkButton(self.frame, text="Chơi lại", command=self.reset_game)
        self.reset_button.grid(row=1, column=2, padx=10, pady=10)

        # Khởi tạo biến trạng thái
        self.setup_game()

        # Trạng thái chiến thắng
        self.win = False

        # Đã ghé thăm
        self.visited = set()

        # Biến hiển thị trạng thái thắng
        self.win_label = None  # Khởi tạo win_label với giá trị None

    def setup_game(self):
        # Lưu trạng thái lưới
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
        # Xóa nội dung canvas
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1, y1 = i * CELL_SIZE, j * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#34495e", fill=COLORS["grid"])

    def place_obstacles(self):
        def is_valid_obstacle(x, y):
            # Kiểm tra xem vị trí (x, y) có nằm trên đường đi hợp lệ hay không
            if (x, y) in self.path or (x, y) == self.start or (x, y) == self.end:
                return False
            return True
        # Đặt chướng ngại vật
        while len(self.obstacles) < NUM_OBSTACLES:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.obstacles and is_valid_obstacle(x, y):
                self.obstacles.add((x, y))
                self.draw_cell((x, y), COLORS["obstacle"])

    def randomize_start_end(self):
        # Chọn điểm bắt đầu và kết thúc ngẫu nhiên
        while True:
            self.start = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            self.end = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
            if self.start != self.end and self.start not in self.obstacles and self.end not in self.obstacles:
                break

        self.draw_cell(self.start, COLORS["start"])
        self.draw_cell(self.end, COLORS["end"])

    def generate_path(self):
        path = []
        x1, y1 = self.start
        x2, y2 = self.end
        if x1 < x2:
            for x in range(x1, x2 + 1):
                path.append((x, y1))
        elif x1 > x2:
            for x in range(x1, x2 - 1, -1):
                path.append((x, y1))
        if y1 < y2:
            for y in range(y1, y2 + 1):
                if (x2, y) not in path:
                    path.append((x2, y))
        elif y1 > y2:
            for y in range(y1, y2 - 1, -1):
                if (x2, y) not in path:
                    path.append((x2, y))
        return path

    def draw_cell(self, pos, color):
        x, y = pos
        self.canvas.create_rectangle(x * CELL_SIZE, y * CELL_SIZE,
                                     (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                                     fill=color, outline="black", width=2)

    def run_hill_climbing(self):
        try:
            self.visited=set()
            if self.mode == "auto":
                self.hill_climbing(self.start, self.end)
            if self.path:
                for x, y in self.path:
                    if (x, y) == self.end or (x,y)==self.start:
                        continue
                    self.draw_cell((x, y), COLORS["path"])
                if self.end in self.path:
                    self.show_message("Win!")
                else:
                    self.show_message("Không tìm được đường đi.")
            else:
                self.show_message("Không tìm được đường đi.")
        except Exception as e:
            print(e)

    def hill_climbing(self, start, end):
        #Kiểm tra sử dụng biến nhớ path nào
        current = start
        if(start==self.start):
            self.path = [current]
        else: path=[current]

        #Thực hiện thuật toán leo đồi
        while current != end:
            self.visited.add(current)
            neighbors = self.get_neighbors(current)
            neighbors = [n for n in neighbors if n not in self.obstacles and n not in self.visited]

            if not neighbors:
                return None

            next_node = min(neighbors, key=lambda n: self.heuristic(n, end))
            if self.heuristic(next_node, end) >= self.heuristic(current, end):
                #Tối ưu cục bộ
                res=self.handle_max_local(neighbors,end)
                if(res is None):
                    return None
                if(start==self.start):
                    self.path=self.path+res
                    return
                else:
                    path=path+res
                    return path
            if(start==self.start):
                self.path.append(next_node)
                current = next_node
            else:
                path.append(next_node)
                current = next_node
        if(start!=self.start):
            return path

    def handle_max_local(self,neighbros,end):
        list_path=[]
        for i in range(len(neighbros)):
            temp_path=self.hill_climbing(neighbros[i],end)
            if(temp_path!=None):
                list_path.append(temp_path)
        if list_path:
            return min(list_path, key=len)  # Chọn path ngắn nhất
        return None

    def handle_manual_click(self, event):
        if self.start and self.end and not self.win:
            x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
            if (x, y) not in self.obstacles and (x, y) not in self.path:
                self.draw_cell((x, y), COLORS["user_path"])
                self.path.append((x, y))

                # Kiểm tra nếu đã chạm đến điểm kết thúc
                if (x, y) == self.end:
                    self.win = True
                    self.show_message("Win!")
                    self.canvas.unbind("<Button-1>")  # Ngừng việc vẽ đường khi thắng

    def show_message(self, message):
        if hasattr(self, "win_label") and self.win_label:
            self.win_label.destroy()
        # Tạo label mới và lưu trữ trong self.win_label
        self.win_label = ctk.CTkLabel(self.frame, text=message, text_color="white", font=("Arial", 20))
        self.win_label.grid(row=2, column=0, columnspan=3, pady=10)

    def heuristic(self, node, end):
        x1, y1 = node
        x2, y2 = end
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbors.append((nx, ny))
        return neighbors

    def change_mode(self, selected_mode):
        if selected_mode == "Máy tự chơi":
            self.mode = "auto"
            self.canvas.unbind("<Button-1>")
        elif selected_mode == "Người chơi tự chơi":
            self.mode = "manual"
        self.reset_game()

    def reset_game(self):
        # Khởi tạo lại trò chơi
        self.win = False  # Đặt lại trạng thái chiến thắng về False
        self.path = []
        self.visited=set() # Xóa đường đi của người chơi
        self.show_message(" ")
        self.setup_game()


# Chạy game
root = ctk.CTk()
game = PipeGame(root)
root.mainloop()
