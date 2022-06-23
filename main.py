import tkinter as tk
from tkinter import ttk

from Fibo import Fib
from Game2048 import TwoZeroFourEight
from Alphabet import Alphabet
from Base import LEFT, RIGHT, DOWN, UP, SAVE_IF_NEEDED_AND_QUIT


_games_classes = [Fib, TwoZeroFourEight, Alphabet]

games = {}
for g in _games_classes:
    games[g.GAME_NAME] = g


class Game(tk.Tk):

    def __init__(self):

        super().__init__()
        self.title("Board Game")

        _all_container = ttk.Frame(self)
        _all_container.grid(row=0, column=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        label_frame_user_name = ttk.Labelframe(_all_container, text="User name")
        label_frame_user_name.grid(row=0, column=0)

        self.entry_user_name = ttk.Entry(label_frame_user_name, width=40)
        self.entry_user_name.grid()

        choices_frame = ttk.Frame(_all_container)
        choices_frame.grid(row=1, column=0)

        label_frame_game_choice = ttk.Labelframe(choices_frame, text="Game")
        label_frame_grid_size_choice = ttk.Labelframe(choices_frame, text="Grid Size")
        label_frame_winning_tile_choice = ttk.Labelframe(choices_frame, text="Winning Tile")

        label_frame_game_choice.grid(row=0, column=0, rowspan=2, sticky='nsw')
        label_frame_grid_size_choice.grid(row=0, column=1, sticky='nsw')
        label_frame_winning_tile_choice.grid(row=1, column=1, sticky='nsw')

        self.game_names = sorted(games.keys())

        self.string_var_cur_game_name = tk.StringVar(self)

        for game_name in self.game_names:
            ttk.Radiobutton(label_frame_game_choice, text=game_name, variable=self.string_var_cur_game_name,
                            value=game_name).grid(sticky='w')

        self.int_var_grid_size = tk.IntVar(self)
        self.spin_box_grid_size = tk.Spinbox(label_frame_grid_size_choice, from_=2, to=10, increment=1,
                                             textvariable=self.int_var_grid_size)
        self.spin_box_grid_size.grid(row=0, column=0)

        self.string_var_winning_tile = tk.StringVar(self)
        self.combobox_winning_tile_choices = ttk.Combobox(label_frame_winning_tile_choice,
                                                          textvariable=self.string_var_winning_tile)
        self.combobox_winning_tile_choices.grid()
        self.combobox_winning_tile_choices.bind("<Key>", lambda *_: 'break')

        buttons_frame = ttk.Frame(_all_container)
        buttons_frame.grid(row=2, column=0)

        self.button_continue_previous_game = ttk.Button(buttons_frame, text="Continue Previous Game", width=25)
        self.button_start_new_game = ttk.Button(buttons_frame, text="Start New Game", width=25)

        self.button_continue_previous_game.grid(row=0, column=0)
        self.button_start_new_game.grid(row=0, column=1)

        self.board = None

        self.string_var_cur_game_name.trace('w', self.change_game_choice_options)
        self.string_var_cur_game_name.set(self.game_names[0])

        self.entry_user_name.bind("<KeyRelease>", self.set_continue_game_button_status)

        self.button_continue_previous_game.bind("<ButtonRelease-1>", self.button_release)
        self.button_start_new_game.bind("<ButtonRelease-1>", self.button_release)

        self.canvas = tk.Canvas(_all_container, width=400, height=400)
        self.canvas.grid(row=3, column=0)

        self.string_var_winning_tile.trace_id = self.string_var_winning_tile.trace('w', self.safe_reset)
        self.int_var_grid_size.trace_id = self.int_var_grid_size.trace(
            'w', self.safe_reset_and_update_winning_tile_if_dependent)

        for key in 'w W s S a A d D q Q Up Right Left Down Escape'.split(' '):
            self.canvas.bind("<KeyRelease-%s>" % key, self.process_canvas_user_action)

    def process_canvas_user_action(self, event):
        if self.board is None:
            return

        print("-"*30)

        user_action = event.keysym
        print("user-action =", user_action)

        if user_action in 'w W Up'.split(' '):
            self.board.perform_action(UP)
        elif user_action in 's S Down'.split(' '):
            self.board.perform_action(DOWN)
        elif user_action in 'a A Left'.split(' '):
            self.board.perform_action(LEFT)
        elif user_action in 'd D Right'.split(' '):
            self.board.perform_action(RIGHT)
        elif user_action in 'q Q Escape'.split(' '):
            self.board.perform_action(SAVE_IF_NEEDED_AND_QUIT)
            self.board = None
            self.draw_board()
            return

        self.board.set_game_end_status()
        print(self.board)
        self.draw_board()

    def button_release(self, event):
        if not event.widget.instate(["hover", "!disabled"]):
            return
        if event.widget == self.button_continue_previous_game:
            self.continue_game()
            self.canvas.focus_set()
        elif event.widget == self.button_start_new_game:
            self.new_game()
            self.canvas.focus_set()

    def set_continue_game_button_status(self, *_):

        self.safe_reset()

        self._set_game()
        if self.board.does_saved_game_exist_for_this_user():
            self.button_continue_previous_game.state(["!disabled"])
        else:
            self.button_continue_previous_game.state(["disabled"])

        self.board = None

    def safe_reset(self, *_):
        if self.board is not None:
            self.board.save_game_if_needed()
            self.board = None
            self.draw_board()

    def safe_reset_and_update_winning_tile_if_dependent(self, *_):
        self.safe_reset()

        game_name = self.string_var_cur_game_name.get()
        if games[game_name].DEFAULT_WINNING_TILE is None:
            self._set_game()
            winning_tile = self.board.get_winning_tile()
            self.board = None
            self.string_var_winning_tile.set(str(winning_tile))

    def change_game_choice_options(self, *_):

        self.safe_reset()

        game_name = self.string_var_cur_game_name.get()
        self.int_var_grid_size.set(games[game_name].DEFAULT_GRID_SIZE)
        self.combobox_winning_tile_choices.configure(values=tuple(map(str, games[game_name].WINNING_TILE_CHOICES)))

        default_winning_tile = games[game_name].DEFAULT_WINNING_TILE
        self.string_var_winning_tile.set(str(default_winning_tile))
        self.set_continue_game_button_status()

    def continue_game(self):
        self._set_game()
        self.board.retrieve_if_saved_game_exists()

        self.string_var_winning_tile.trace_vdelete('w', self.string_var_winning_tile.trace_id)
        self.int_var_grid_size.trace_vdelete('w', self.int_var_grid_size.trace_id)

        self.int_var_grid_size.set(self.board.get_board_size())
        self.string_var_winning_tile.set(self.board.get_winning_tile())

        self.string_var_winning_tile.trace_id = self.string_var_winning_tile.trace('w', self.safe_reset)
        self.int_var_grid_size.trace_id = self.int_var_grid_size.trace(
            'w', self.safe_reset_and_update_winning_tile_if_dependent)

        print(self.board)
        self.button_continue_previous_game.state(["disabled"])
        print(self.board)
        self.draw_board()

    def new_game(self):
        self.button_start_new_game.state(["disabled"])
        self.button_start_new_game.update_idletasks()

        self._set_game()
        print(self.board)
        self.draw_board()

        self.button_start_new_game.state(["!disabled"])
        self.button_start_new_game.update_idletasks()

    def _set_game(self, *_):

        print("-------New game set------")

        user_name = self.entry_user_name.get().strip()  # type: str
        if user_name == "":
            user_name = "TempUser"

        game_name = self.string_var_cur_game_name.get()

        if games[game_name].DEFAULT_WINNING_TILE is None:
            self.board = games[game_name](user_name, self.int_var_grid_size.get())

            self.string_var_winning_tile.trace_vdelete('w', self.string_var_winning_tile.trace_id)
            self.string_var_winning_tile.set(self.board.get_winning_tile())
            self.string_var_winning_tile.trace_id = self.string_var_winning_tile.trace('w', self.safe_reset)

        else:
            self.board = games[game_name](
                user_name, self.int_var_grid_size.get(),
                type(games[game_name].WINNING_TILE_CHOICES[0])(self.string_var_winning_tile.get()))

    def destroy(self):
        if self.board is not None:
            self.board.save_game_if_needed()
        super().destroy()

    def draw_board(self):
        print("Drawing board - started")
        tag_on_canvas = 'on-canvas'
        tag_text = 'text'

        self.canvas.delete(tag_on_canvas)

        if self.board is None:
            return

        max_size = 400
        line_width = 2

        board_size = self.board.get_board_size()

        cell_size = int((max_size - (board_size + 1)*line_width)/board_size)

        required_size = (board_size+1)*line_width + board_size*cell_size

        self.canvas.configure(width=required_size, height=required_size)

        for i in range(board_size+1):
            p = 3 + i*(cell_size + line_width)
            self.canvas.create_line(p, 0, p, required_size, width=line_width, fill='black', tags=tag_on_canvas)
            self.canvas.create_line(0, p, required_size, p, width=line_width, fill='black', tags=tag_on_canvas)

        texts_and_positions = []
        for r in range(board_size):
            for c in range(board_size):
                text = str(self.board.get_cell(r, c))
                if text == '0':  # empty
                    continue
                x = 3 + int((c + 0.5)*(cell_size + line_width))
                y = 3 + int((r + 0.5)*(cell_size + line_width))
                texts_and_positions.append((text, x, y))

        # find font size
        base_font = 'Times New Roman'
        font_size = 7
        while True:
            font_size += 1
            final_font = '"%s" %d' % (base_font, font_size)
            biggest_text = max(texts_and_positions, key=lambda t: len(t[0]))[0]
            font_test_text_id = self.canvas.create_text(required_size/2, required_size/2, text=biggest_text,
                                                        font=final_font, tags=tag_text)
            x1, y1, x2, y2 = self.canvas.bbox(font_test_text_id)
            self.canvas.delete(tag_text)
            font_test_text_size = max(x2 - x1, y2 - y1)
            if font_test_text_size > cell_size/2:
                font_size -= 1
                break

        if self.board.game_ended():
            if self.board.is_game_lost():
                color = 'red'
            else:
                color = 'green'
        else:
            color = 'black'

        for text, x, y in texts_and_positions:
            self.canvas.create_text(x, y, text=text, tags=(tag_on_canvas, tag_text), font=final_font, fill=color)

        print("In draw canvas", self.board, sep='\n')
        print("Drawing board - end")


if __name__ == '__main__':
    Game().mainloop()
    # game = Game()
    # game.board = Fib("TempUser")
    # print(game.board)
    # input("Press Enter to continue")
    # game.draw_board()
    # game.mainloop()
    # print(game.board)
