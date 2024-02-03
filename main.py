import tkinter as tk
from tkinter import messagebox
import random
import math
import time
import struct

CELL_SIZE        = 36         # px. scales well with font rn
BG_COLOR         = "#222222"  # darker gray
UNCLICKED_COLOR  = "#d77f37"  # orange
CLICKED_COLOR    = "#222222"  # clicked/empty spaces background
NUMBER_COLORS    = "#e3e3e3"  # white for numbers
TEMP_BLANK_COLOR = "#aaaaaa"  # temporary blank color for visualization
IMPOSSIBLE_COLOR = "#503333"  # bright red for impossible moves



class Minesweeper:
    def __init__(self, master):
        self.start_time = None  
        self.game_active = False
        self.master = master
        self.master.configure(bg=BG_COLOR)
        self.buttons = []
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.first_click = True
        self.temp_blanks = set()
        self.show_menu()

    def show_menu(self):
        self.menu_frame = tk.Frame(self.master, bg=BG_COLOR)
        self.menu_frame.pack(padx=10, pady=10, fill="both", expand=True)

        title_label = tk.Label(self.menu_frame, text="Select Difficulty", bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))

        modes = [("Beginner", 9, 9, 10), ("Intermediate", 16, 16, 40), ("Expert", 30, 16, 99)]
        buttons_frame = tk.Frame(self.menu_frame, bg=BG_COLOR)
        buttons_frame.pack()

        for index, mode in enumerate(modes):
            btn = tk.Button(buttons_frame, text=mode[0], bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                            font=("Arial", 12, "bold"), relief="flat",
                            command=lambda m=mode: self.start_game(*m[1:]))
            btn.grid(row=0, column=index, padx=5, pady=5)

        # other title
        other_label = tk.Label(self.menu_frame, text="Other", bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", 12, "bold"))
        other_label.pack(pady=(20, 5))

        highscores_btn = tk.Button(self.menu_frame, text="Highscores", bg=UNCLICKED_COLOR, fg=NUMBER_COLORS,
                                    font=("Arial", 12, "bold"), relief="flat",
                                    command=self.show_highscores)
        highscores_btn.pack(pady=(5, 5))

    def format_time(self, seconds):
        """Converts time in seconds to a formatted string."""
        total_seconds = float(seconds)
        hours = int(total_seconds) // 3600
        minutes = (int(total_seconds) % 3600) // 60
        seconds = total_seconds % 60 
        formatted_time = ""
        if hours > 0:
            formatted_time += f"{hours}h "
        if minutes > 0 or hours > 0:  # if hours, include minutes
            formatted_time += f"{minutes}m "
        formatted_time += f"{seconds:.2f}s"
        return formatted_time

    def show_highscores(self):
        highscores_window = tk.Toplevel(self.master, bg=BG_COLOR)
        highscores_window.title("Highscores")
        highscores_window.resizable(False, False)

        difficulties = {
            "Beginner": "9x9 - 10 Mines",
            "Intermediate": "16x16 - 40 Mines",
            "Expert": "30x16 - 99 Mines"
        }

        highscores_frame = tk.Frame(highscores_window, bg=BG_COLOR)
        highscores_frame.pack(pady=(10, 5))

        for index, difficulty in enumerate(difficulties.keys()):
            tk.Label(highscores_frame, text=difficulty, bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", 16, "bold")).grid(row=0, column=index, padx=20)

        records = []
        try:
            with open("minesweeper.wins", "rb") as file:
                while True:
                    length_bytes = file.read(4)  # 4 bytes for unsigned int
                    if not length_bytes:
                        break  # End of file
                    length = struct.unpack('I', length_bytes)[0]
                    mode_bytes = file.read(length)
                    mode = mode_bytes.decode('utf-8')
                    time_taken_bytes = file.read(4)  # 4 bytes for float
                    time_taken = struct.unpack('f', time_taken_bytes)[0]
                    records.append((mode, time_taken))
        except FileNotFoundError:
            pass

        records.sort(key=lambda x: float(x[1]))

        records_by_difficulty = {difficulty: [] for difficulty in difficulties.keys()}
        for record in records:
            for difficulty, format in difficulties.items():
                if format in record[0]:
                    records_by_difficulty[difficulty].append(record)
                    break

        for index, (difficulty, records) in enumerate(records_by_difficulty.items()):
            if not records:  # Check if there are no records for the difficulty
                tk.Label(highscores_frame, text="No scores set!", bg=BG_COLOR, fg=NUMBER_COLORS).grid(row=1, column=index, padx=20)
                continue  # Skip to the next difficulty
            top_records = records[:5]
            for row, record in enumerate(top_records, start=1):
                formatted_time = self.format_time(record[1])
                tk.Label(highscores_frame, text=formatted_time, bg=BG_COLOR, fg=NUMBER_COLORS).grid(row=row, column=index, padx=20)

        highscores_window.update_idletasks()

        window_width = highscores_window.winfo_width()
        window_height = highscores_window.winfo_height()

        screen_width = highscores_window.winfo_screenwidth()
        screen_height = highscores_window.winfo_screenheight()

        # we're moving it 450 pixels to the right here because on a 1920x1080 monitor,
        # the highscores interface will be pretty close next to the menu, just makes stuff cleaner :)
        center_x = int((screen_width - window_width) / 2) + 450
        center_y = int((screen_height - window_height) / 2)

        highscores_window.geometry(f'+{center_x}+{center_y}')


    def start_game(self, width, height, mines):
        global GRID_WIDTH, GRID_HEIGHT, MINES_COUNT
        GRID_WIDTH, GRID_HEIGHT, MINES_COUNT = width, height, mines
        self.menu_frame.destroy()  # remove menu after starting
        self.buttons = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.create_widgets()



    def create_widgets(self):
        # Flag Counter Frame and Label
        self.info_frame = tk.Frame(self.master, bg=BG_COLOR, height=CELL_SIZE)
        self.info_frame.grid(row=0, column=0, columnspan=GRID_WIDTH, sticky="nsew")
        
        self.flag_counter_label = tk.Label(self.info_frame, text=f"Flagged: 0/{MINES_COUNT}", bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", int(CELL_SIZE/2.5)))
        self.flag_counter_label.pack(side="left", padx=(10, 0))
        
        # Time Elapsed Label
        self.time_elapsed_label = tk.Label(self.info_frame, text="Time: 0s", bg=BG_COLOR, fg=NUMBER_COLORS, font=("Arial", int(CELL_SIZE/2.5)))
        self.time_elapsed_label.pack(side="right", padx=(0, 10)) 

        for row in range(1, GRID_HEIGHT + 1):  # grid placement for buttons from row 1
            for col in range(GRID_WIDTH):
                button = tk.Canvas(self.master, width=CELL_SIZE, height=CELL_SIZE, bg=UNCLICKED_COLOR, highlightthickness=0)
                button.grid(row=row, column=col, sticky="nsew")
                # subtract 1 from each because of the top title bar
                button.bind("<Button-1>", lambda e, r=row, c=col: self.cell_click(r-1, c, e)) 
                button.bind("<ButtonRelease-1>", lambda e, r=row, c=col: self.hide_temporary_blanks(r-1, c, e))  
                button.bind("<Button-3>", lambda e, r=row, c=col: self.place_flag(r-1, c))
                button.bind("<Enter>", lambda e, r=row, c=col: self.on_hover(e, r-1, c))  
                button.bind("<Leave>", lambda e, r=row, c=col: self.on_leave(e, r-1, c))  
                self.buttons[row-1][col] = button

    def on_hover(self, event, row, col):
        # if the cell is revealed, flagged, or neither
        if (row, col) not in self.revealed:
            if (row, col) in self.flags:
                # slightly lighter gray for flagged cells on hover
                self.buttons[row][col].config(bg="#7e7e7e") # TODO: move to top constants
            else:
                # slightly lighter color for unclicked cells on hover
                self.buttons[row][col].config(bg="#e89b53")

    def on_leave(self, event, row, col):
        # Reset the color based on whether the cell is flagged or not
        if (row, col) not in self.revealed:
            if (row, col) in self.flags:
                # Reset to the original flag color
                self.buttons[row][col].config(bg="#666666")  # TODO: move to top constants
            else:
                # Reset to the original unclicked color
                self.buttons[row][col].config(bg=UNCLICKED_COLOR)


    def update_time_elapsed(self):
        if self.game_active:  # Only update if the game is active
            elapsed_time = int(time.time() - self.start_time)
            self.time_elapsed_label.config(text=f"Time: {elapsed_time}s")
            self.master.after(100, self.update_time_elapsed)

    # ---- DRAWING
    def place_flag(self, row, col, event=None):
        if self.first_click or (row, col) in self.revealed:  # so we can't flag on the first click or unrevealed cells
            return
        button = self.buttons[row][col]
        if (row, col) in self.flags:
            self.flags.remove((row, col))
            button.delete("flag")
            button.config(bg=UNCLICKED_COLOR)  # reset if flag removed
            self.on_hover(None, row, col)
        else:
            self.flags.add((row, col))
            button.config(bg="#666666") # TODO: move to top constants
            self.draw_flag(button)
            
            # manually trigger hor the flag cell
            # before, it was staying the main flag gray instead of becoming lighter
            self.on_hover(None, row, col)
            
        self.update_flag_counter()
        self.update_adjacent_cells_status(row, col)

    def update_flag_counter(self, flags=None):
        # allows for manually setting flags to x when the user reveals all cells
        if flags is None:
            flags = len(self.flags)
        self.flag_counter_label.config(text=f"Flagged: {flags}/{MINES_COUNT}")

    def draw_flag(self, button):
        flag_color = BG_COLOR
        total_flag_width = CELL_SIZE / 3  # total width of the flag (line + square + rectangle)
        flag_height = CELL_SIZE / 3
        line_thickness = flag_height / 5
        square_side = flag_height / 2
        rectangle_height = square_side
        rectangle_length = square_side * 0.8
        rectangle_y_offset = square_side * 0.3
        
        # positions for centering
        flag_x_start = (CELL_SIZE - total_flag_width) / 2
        line_y_start = (CELL_SIZE - flag_height) / 2
        square_x_start = flag_x_start + line_thickness
        rectangle_x_start = square_x_start + square_side
        rectangle_y_start = line_y_start + rectangle_y_offset
        
        # Draw flagpole
        button.create_rectangle(flag_x_start, line_y_start, flag_x_start + line_thickness, line_y_start + flag_height, tags="flag", fill=flag_color, outline=flag_color)
        
        # right square
        button.create_rectangle(square_x_start, line_y_start, square_x_start + square_side, line_y_start + square_side, tags="flag", fill=flag_color, outline=flag_color)
        
        # right downwards rectangle
        button.create_rectangle(rectangle_x_start, rectangle_y_start, rectangle_x_start + rectangle_length, rectangle_y_start + rectangle_height, tags="flag", fill=flag_color, outline=flag_color)

    def cell_click(self, row, col, event):
        if self.first_click:
            self.first_click = False
            self.start_time = time.time()
            self.game_active = True  # game starts
            self.update_time_elapsed()  # start updating time elapsed
            self.place_mines(row, col)
            self.reveal_cell(row, col)
        elif (row, col) not in self.flags and (row, col) not in self.revealed:
            if (row, col) in self.mines:
                self.game_over(False)
            else:
                self.reveal_cell(row, col)
                if self.check_win():
                    self.game_over(True)
        elif (row, col) in self.revealed:
            self.chord_or_show_temp_blanks(row, col)

    def chord_or_show_temp_blanks(self, row, col):
        num = self.adjacent_mines(row, col)
        flags_around = sum((r, c) in self.flags for r in range(max(0, row-1), min(GRID_HEIGHT, row+2)) for c in range(max(0, col-1), min(GRID_WIDTH, col+2)))
        if num == flags_around:
            for r in range(max(0, row-1), min(GRID_HEIGHT, row+2)):
                for c in range(max(0, col-1), min(GRID_WIDTH, col+2)):
                    if (r, c) not in self.flags:
                        if (r, c) in self.mines:
                            self.game_over(False)
                            return
                        self.reveal_cell(r, c)
            # Check for a win after revealing cells around a number
            if self.check_win():
                self.game_over(True)
        elif flags_around > num:  # Highlight the cell if more flags are placed around it than the number indicates
            self.buttons[row][col].config(bg=IMPOSSIBLE_COLOR)
        else:
            self.show_temporary_blanks(row, col)

    def show_temporary_blanks(self, row, col):
        for r in range(max(0, row-1), min(GRID_HEIGHT, row+2)):
            for c in range(max(0, col-1), min(GRID_WIDTH, col+2)):
                if (r, c) not in self.revealed and (r, c) not in self.flags:
                    self.buttons[r][c].config(bg=TEMP_BLANK_COLOR)
                    self.temp_blanks.add((r, c))

    def hide_temporary_blanks(self, row, col, event):
        for r, c in self.temp_blanks:
            self.buttons[r][c].config(bg=UNCLICKED_COLOR)
        self.temp_blanks.clear()

    def update_adjacent_cells_status(self, row, col):
        for r in range(max(0, row-1), min(GRID_HEIGHT, row+2)):
            for c in range(max(0, col-1), min(GRID_WIDTH, col+2)):
                if (r, c) in self.revealed:
                    num = self.adjacent_mines(r, c)
                    flags_around = sum((rr, cc) in self.flags for rr in range(max(0, r-1), min(GRID_HEIGHT, r+2)) for cc in range(max(0, c-1), min(GRID_WIDTH, c+2)))
                    if flags_around > num:
                        self.buttons[r][c].config(bg=IMPOSSIBLE_COLOR)
                    else:
                        self.buttons[r][c].config(bg=CLICKED_COLOR)  # Reset to clicked color if the impossible condition is no longer met


    def place_mines(self, start_row, start_col):
        safe_zone = {(start_row + i, start_col + j) for i in range(-1, 2) for j in range(-1, 2)}
        while len(self.mines) < MINES_COUNT:
            r, c = random.randint(0, GRID_HEIGHT - 1), random.randint(0, GRID_WIDTH - 1)
            if (r, c) not in safe_zone and (r, c) not in self.mines:
                self.mines.add((r, c))

    def fade_out_cell(self, button, steps, final_color, callback=None):
        current_color = button.cget('bg')
        r1, g1, b1 = self.master.winfo_rgb(current_color)
        r2, g2, b2 = self.master.winfo_rgb(final_color)
        
        delta_r = (r2 - r1) / steps
        delta_g = (g2 - g1) / steps
        delta_b = (b2 - b1) / steps
        
        def fade(step=0):
            nonlocal r1, g1, b1
            if step < steps:
                r1, g1, b1 = r1 + delta_r, g1 + delta_g, b1 + delta_b
                next_color = f'#{int(r1/256):02x}{int(g1/256):02x}{int(b1/256):02x}' # what
                button.config(bg=next_color)
                self.master.after(25, lambda: fade(step+1))  # schedule next step
            else:
                if callback:
                    callback()
        
        fade()  # start animation

    def interpolate_color(self, start_color, end_color, factor):
        """Interpolates between two colors with a given factor (0 to 1)."""
        start_r, start_g, start_b = self.master.winfo_rgb(start_color)
        end_r, end_g, end_b = self.master.winfo_rgb(end_color)
        r = int(start_r + (end_r - start_r) * factor)
        g = int(start_g + (end_g - start_g) * factor)
        b = int(start_b + (end_b - start_b) * factor)
        return f'#{r>>8:02x}{g>>8:02x}{b>>8:02x}' # what v2

    def reveal_cell(self, row, col):
        queue = [(row, col)]
        while queue:
            current_row, current_col = queue.pop(0)
            if (current_row, current_col) in self.revealed or (current_row, current_col) in self.flags:
                continue
            self.revealed.add((current_row, current_col))
            button = self.buttons[current_row][current_col]

            steps = 10 
            for i in range(steps + 1):
                factor = i / steps
                color = self.interpolate_color(UNCLICKED_COLOR, CLICKED_COLOR, factor)
                self.master.after(int(i * 50), lambda b=button, c=color: b.config(bg=c))  # schedule color update

            mines_count = self.adjacent_mines(current_row, current_col)
            if mines_count == 0:
                for r in range(max(0, current_row-1), min(GRID_HEIGHT, current_row+2)):
                    for c in range(max(0, current_col-1), min(GRID_WIDTH, current_col+2)):
                        if (r, c) not in self.revealed and (r, c) not in self.flags:
                            queue.append((r, c))
            else:
                self.master.after(steps * 10, lambda b=button, mc=mines_count: b.create_text(CELL_SIZE//2, CELL_SIZE//2, text=str(mc), fill=NUMBER_COLORS, font=("Arial", int(CELL_SIZE/2.7), "bold")))

    def adjacent_mines(self, row, col):
        return sum((r, c) in self.mines for r in range(max(0, row-1), min(GRID_HEIGHT, row+2)) for c in range(max(0, col-1), min(GRID_WIDTH, col+2)))
    
    def check_win(self):
        # if all non-mine cells revealed
        if len(self.revealed) == GRID_WIDTH * GRID_HEIGHT - MINES_COUNT:
            return True
        return False
        
    def game_over(self, win):
        self.game_active = False  # stop time updates
        # disable all buttons to prevent further interaction
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                self.buttons[row][col].unbind("<Button-1>")
                self.buttons[row][col].unbind("<Button-3>")
                self.buttons[row][col].unbind("<Enter>")
                self.buttons[row][col].unbind("<Leave>")

        if not win:
            # If the game is lost, reveal all mines and the entire board
            for r, c in self.mines:
                if (r, c) not in self.flags:  # Check if the mine was flagged
                    button = self.buttons[r][c]
                    button.config(bg=UNCLICKED_COLOR)  # Optionally, indicate mine locations differently
                    self.draw_mine(button)  # Draw a mine symbol only if it wasn't flagged
                # If it was flagged, it's already indicated as such, so we don't change it
            for row in range(GRID_HEIGHT):
                for col in range(GRID_WIDTH):
                    if (row, col) not in self.mines:
                        self.reveal_cell(row, col)  # Reveal numbers for non-mine cells
        else:
            # If the game is won, visually flag all unflagged mines without calling place_flag
            for r, c in self.mines:
                if (r, c) not in self.flags:
                    button = self.buttons[r][c]
                    button.config(bg="#666666")  # Change background to indicate flagging
                    self.draw_flag(button)  # Directly draw the flag on the canvas
            self.update_flag_counter(MINES_COUNT)  # Update flag counter to reflect all mines flagged

        # Show the appropriate message box for win/loss
        if win:
            end_time = time.time()
            time_taken = end_time - self.start_time  # Calculate time taken
            self.store_win_record(time_taken)  # Store the win record
            messagebox.showinfo("Minesweeper", "Congratulations! You've won!")
        else:
            messagebox.showinfo("Minesweeper", "Game Over! You hit a mine.")
        self.master.destroy()

    def store_win_record(self, time_taken):
        mode = f"{GRID_WIDTH}x{GRID_HEIGHT} - {MINES_COUNT} Mines"
        mode_encoded = mode.encode('utf-8')  # Encode the mode string as bytes
        record = struct.pack('I', len(mode_encoded)) + mode_encoded + struct.pack('f', time_taken)
        # 'I' is for unsigned int (length of the mode string), 'f' is for float (time_taken)
        with open("minesweeper.wins", "ab") as file:  # Open file in append binary mode
            file.write(record)

    def draw_mine(self, button):
        # Adjusted mine drawing parameters for a smaller design
        outer_circle_radius = CELL_SIZE * 0.2  # Smaller outer circle
        inner_circle_radius = CELL_SIZE * 0.07  # Smaller inner circle
        leg_size = CELL_SIZE * 0.1  # Smaller square "legs"
        
        # Draw outer circle
        button.create_oval(
            CELL_SIZE/2 - outer_circle_radius, CELL_SIZE/2 - outer_circle_radius,
            CELL_SIZE/2 + outer_circle_radius, CELL_SIZE/2 + outer_circle_radius,
            fill=BG_COLOR, outline=BG_COLOR
        )
        
        # Draw inner circle
        button.create_oval(
            CELL_SIZE/2 - inner_circle_radius, CELL_SIZE/2 - inner_circle_radius,
            CELL_SIZE/2 + inner_circle_radius, CELL_SIZE/2 + inner_circle_radius,
            fill=UNCLICKED_COLOR, outline=UNCLICKED_COLOR
        )
        
        # Calculate and draw legs at every 45 degrees around the outer circle
        for angle in range(0, 360, 45):  # 0, 45, 90, ..., 315 degrees
            radian = angle * (3.141592653589793 / 180)  # Convert angle to radians
            # Calculate the center position for each leg
            x_center = CELL_SIZE/2 + (outer_circle_radius + leg_size/2) * math.cos(radian)
            y_center = CELL_SIZE/2 + (outer_circle_radius + leg_size/2) * math.sin(radian)
            # Calculate the top-left corner based on the center position
            x = x_center - leg_size/2
            y = y_center - leg_size/2
            button.create_rectangle(
                x, y, x + leg_size, y + leg_size,
                fill=BG_COLOR, outline=BG_COLOR
            )

def main():
    root = tk.Tk()
    root.title("Minesweeper")
    root.resizable(False, False)  # Make the window non-resizable

    # Force Tkinter to draw the window so we can get its size
    root.update_idletasks()

    # Get window size
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position for window to be centered
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    # Set the window's position to center
    root.geometry(f'+{center_x}+{center_y}')

    game = Minesweeper(root)
    root.mainloop()

if __name__ == "__main__":
    main()