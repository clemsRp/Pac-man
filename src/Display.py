import pyray as pr

class Display:
    def __init__(self, maze: list[list[int]]):
        self.maze = maze
        self.pacman_x = 400
        self.screen_width = 3840
        self.screen_height = 2160
        self.pacman_y = 300
        self.radius = 20

    def draw_maze(self):
        

    def create_window(self):
        pr.init_window(self.screen_width, self.screen_height, "Pac-Man")
        pr.set_target_fps(60)

    def handle_events(self):
        if pr.is_key_down(pr.KeyboardKey.KEY_RIGHT):
            self.pacman_x += 5
        if pr.is_key_down(pr.KeyboardKey.KEY_LEFT):
            self.pacman_x -= 5
        if pr.is_key_down(pr.KeyboardKey.KEY_UP):
            self.pacman_y -= 5
        if pr.is_key_down(pr.KeyboardKey.KEY_DOWN):
            self.pacman_y += 5

    def render_loop(self):
        while not pr.window_should_close():
                
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)
            pr.draw_rectangle(100, 100, 600, 50, pr.DARKBLUE)
            pr.draw_circle(400, 200, 5.0, pr.WHITE)

            self.handle_events()
        
            pr.draw_circle(int(self.pacman_x),
                           int(self.pacman_y),
                           self.radius,
                           pr.YELLOW)

            pr.draw_text("Score: 42", 10, 10, 20, pr.RAYWHITE)
            
            pr.end_drawing()

    def close_window():
        pr.close_window()