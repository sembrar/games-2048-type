import tkinter as tk
from tkinter import ttk
from math import ceil
import re

from Fibo import Fib
from Game2048 import TwoZeroFourEight
from Alphabet import Alphabet

from Base import LEFT, RIGHT, DOWN, UP, SAVE_IF_NEEDED_AND_QUIT
from leader_board import LeaderBoardDisplay, get_user_names
from tkinter import messagebox

import json

_games_classes = [Fib, TwoZeroFourEight, Alphabet]

games = {}
for g in _games_classes:
    games[g.GAME_NAME] = g


class Game(tk.Tk):

    def __init__(self):

        super().__init__()
        self.title("Board Game")
        self.iconbitmap("icon.ico")
        self.resizable(False, False)

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

        self.entry_user_name.bind("<KeyRelease>", self.entry_user_name_changed)

        self.button_continue_previous_game.bind("<ButtonRelease-1>", self.button_release)
        self.button_start_new_game.bind("<ButtonRelease-1>", self.button_release)

        label_frame_action_time_span = ttk.Labelframe(_all_container, text="Action Time Span")
        label_frame_action_time_span.grid(row=3, column=0)

        self.action_time_span = tk.IntVar(self)
        tk.Spinbox(master=label_frame_action_time_span, from_=100, to=1000, increment=100,
                   textvariable=self.action_time_span).grid(row=0, column=0)
        self.action_time_span.set(500)
        tk.Label(master=label_frame_action_time_span, text="milli seconds").grid(row=0, column=1)

        self.canvas = tk.Canvas(_all_container, width=400, height=400)
        self.canvas.grid(row=4, column=0)

        self.button_view_leader_board = ttk.Button(_all_container, text="View Leader Board")
        self.button_view_leader_board.grid(row=5, column=0, sticky='ew')
        self.button_view_leader_board.bind("<ButtonRelease-1>", self.button_release)

        self.string_var_winning_tile.trace_id = self.string_var_winning_tile.trace('w', self.safe_reset)
        self.int_var_grid_size.trace_id = self.int_var_grid_size.trace(
            'w', self.safe_reset_and_update_winning_tile_if_dependent)

        for key in 'w W s S a A d D q Q Up Right Left Down Escape'.split(' '):
            self.canvas.bind("<KeyRelease-%s>" % key, self.process_canvas_user_action)

        self.available_user_names = ''
        self.entry_user_name.bind("<FocusIn>", self.read_user_names)

        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        # print(w, h, sw, sh)

        y = int((sh - h) / 4)
        x = int((sw - w) / 2.75)

        self.geometry('+%d+%d' % (x, y))

        self.retrieve_settings()

    def entry_user_name_changed(self, event):
        cur_str = self.entry_user_name.get()
        if event.keysym != 'BackSpace':
            if event.keysym == 'Return':
                self.entry_user_name.selection_clear()
            else:
                matched = re.findall('%s.*' % cur_str, self.available_user_names)
                if len(matched) > 0:
                    matched.sort(key=lambda x: len(x))
                    remaining_string = matched[0][len(cur_str):]
                    if remaining_string != '':
                        print("Matched", matched, "Remaining str:", [remaining_string])
                        self.entry_user_name.insert(len(cur_str), remaining_string)
                        self.entry_user_name.select_range(len(cur_str), tk.END)
        self.set_continue_game_button_status()

    def read_user_names(self, *_):
        self.available_user_names = '\n'.join(get_user_names())
        print([self.available_user_names])

    def process_canvas_user_action(self, event):
        if self.board is None:
            return

        # print("-"*30)

        user_action = event.keysym
        # print("user-action =", user_action)

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
        # print(self.board)
        self.unbind_all_canvas_events_move_texts_and_draw_board_and_bind_them_back()

    def button_release(self, event):
        if not event.widget.instate(["hover", "!disabled"]):
            return
        if event.widget == self.button_continue_previous_game:
            self.continue_game()
            self.canvas.focus_set()
        elif event.widget == self.button_start_new_game:
            self.new_game()
            self.canvas.focus_set()
        elif event.widget == self.button_view_leader_board:
            self.canvas.focus_set()
            try:
                LeaderBoardDisplay(self.string_var_cur_game_name.get())
            except AttributeError:
                messagebox.showinfo("No details", "No leader board details to be shown!")

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

        self.button_continue_previous_game.state(["disabled"])
        # print(self.board)
        self.draw_board()

    def new_game(self):
        self.button_start_new_game.state(["disabled"])
        self.button_start_new_game.update_idletasks()

        if self.board is not None:
            self.board.update_leader_board_if_game_ended(force_update=True)

        self._set_game()
        # print(self.board)
        self.draw_board()

        self.button_start_new_game.state(["!disabled"])
        self.button_start_new_game.update_idletasks()

    def _set_game(self, *_):

        # print("-------New game set------")

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

    def retrieve_settings(self):
        try:
            with open('data/settings.json') as f:
                settings = json.loads(f.read().strip())

                # self.entry_user_name.delete(0, tk.END)
                # self.entry_user_name.insert(0, settings['user_name'])
                self.entry_user_name.focus_set()

                self.string_var_cur_game_name.set(settings['game_name'])
                self.string_var_winning_tile.set(settings['winning_tile'])
                self.int_var_grid_size.set(settings['grid_size'])
                self.action_time_span.set(settings['action_time_span'])
        except IOError:
            print("No previous settings available")

    def save_settings(self):
        settings = {'user_name': self.entry_user_name.get(), 'game_name': self.string_var_cur_game_name.get(),
                    'grid_size': self.int_var_grid_size.get(), 'winning_tile': self.string_var_winning_tile.get(),
                    'action_time_span': self.action_time_span.get()}
        with open('data/settings.json', 'w') as f:
            f.write(json.dumps(settings, indent=1))

    def destroy(self):
        self.save_settings()
        if self.board is not None:
            self.board.save_game_if_needed()
        super().destroy()

    def get_font_of_good_size_for_text(self, text, max_height, max_width,
                                       max_percentage=0.5, base_font="Times New Roman", start_size=7):

        tag_font_size_test = 'font-size-test'

        font_size = start_size - 1

        x, y = map(lambda _: int(int(self.canvas.cget(_)) / 2), ('width', 'height'))

        while True:
            font_size += 1
            final_font = '"%s" %d' % (base_font, font_size)

            font_test_text_id = self.canvas.create_text(x, y, text=text, font=final_font, tags=tag_font_size_test)
            x1, y1, x2, y2 = self.canvas.bbox(font_test_text_id)
            self.canvas.delete(tag_font_size_test)

            text_width = x2 - x1
            text_height = y2 - y1

            if text_width > max_width * max_percentage or text_height > max_height * max_percentage:
                font_size -= 1
                break

        final_font = '"%s" %d' % (base_font, font_size)
        return final_font

    def unbind_all_canvas_events_move_texts_and_draw_board_and_bind_them_back(self):

        if self.board is None:
            return

        movements = self.board.get_movements()
        if len(movements) == 0:
            return

        # unbind
        for key in 'w W s S a A d D q Q Up Right Left Down Escape'.split(' '):
            self.canvas.unbind("<KeyRelease-%s>" % key)

        # move

        frame_time = 40  # msec
        num_frames = int(ceil(self.action_time_span.get() / frame_time))
        # print("num frames =", num_frames)

        # calculate increment for each text per frame
        line_width, cell_size = self.get_line_width_cell_size()

        increments = {}
        for key in movements:
            r1, c1 = key
            r2, c2 = movements[key]
            x1, y1 = self.get_x_y_from(r1, c1, cell_size, line_width)
            x2, y2 = self.get_x_y_from(r2, c2, cell_size, line_width)
            increments[(r1, c1)] = (int(ceil((x2 - x1) / num_frames)), int(ceil((y2 - y1) / num_frames)))

        # print("movements:", movements, sep='\n')
        # print("increments:", increments, sep='\n')

        def move_texts(frame_num):
            if frame_num >= num_frames:
                self.draw_board()
                return
            for r1, c1 in increments.keys():
                self.canvas.move('%d-%d' % (r1, c1), *increments[(r1, c1)])
            # print("frame %d of %d" % (frame_num, num_frames))
            self.after(frame_time, move_texts, frame_num + 1)

        move_texts(0)

        # bind
        for key in 'w W s S a A d D q Q Up Right Left Down Escape'.split(' '):
            self.canvas.bind("<KeyRelease-%s>" % key, self.process_canvas_user_action)

    def get_x_y_from(self, r, c, cell_size, line_width):
        x = 3 + int((c + 0.5) * (cell_size + line_width))
        y = 3 + int((r + 0.5) * (cell_size + line_width))
        return x, y

    def get_line_width_cell_size(self):
        max_size = 400
        line_width = 2

        board_size = self.board.get_board_size()

        cell_size = int((max_size - (board_size + 1) * line_width) / board_size)

        return line_width, cell_size

    def draw_board(self):
        tag_on_canvas = 'on-canvas'

        if self.board is None:
            self.canvas.delete(tag_on_canvas)
            return

        board_size = self.board.get_board_size()
        line_width, cell_size = self.get_line_width_cell_size()

        required_size = (board_size + 1) * line_width + board_size * cell_size

        self.canvas.configure(width=required_size, height=required_size)

        self.canvas.delete(tag_on_canvas)

        for i in range(board_size + 1):
            p = 3 + i * (cell_size + line_width)
            self.canvas.create_line(p, 0, p, required_size, width=line_width, fill='blue', tags=tag_on_canvas)
            self.canvas.create_line(0, p, required_size, p, width=line_width, fill='blue', tags=tag_on_canvas)

        texts_and_positions_and_tag_rc = []
        for r in range(board_size):
            for c in range(board_size):
                text = str(self.board.get_cell(r, c))
                if text == '0':  # empty
                    continue
                x, y = self.get_x_y_from(r, c, cell_size, line_width)
                texts_and_positions_and_tag_rc.append((text, x, y, '%d-%d' % (r, c)))

        # get good font: todo
        biggest_text = max(texts_and_positions_and_tag_rc, key=lambda t: len(t[0]))[0]
        final_font = self.get_font_of_good_size_for_text(biggest_text, cell_size, cell_size, 0.75)

        if self.board.game_ended():
            if self.board.is_game_lost():
                color = 'red'
            else:
                color = 'green'
        else:
            color = 'black'

        for text, x, y, tag_rc in texts_and_positions_and_tag_rc:
            self.canvas.create_text(x, y, text=text, tags=(tag_on_canvas, tag_rc), font=final_font, fill=color)

        extra_height = 50
        self.canvas.configure(height=required_size + extra_height)
        text = "Num moves used = %d" % self.board.get_num_moves_used()
        font = self.get_font_of_good_size_for_text(text, extra_height, required_size, 0.75)
        self.canvas.create_text(required_size / 2, required_size + extra_height / 2, text=text, font=font,
                                tags=tag_on_canvas)


if __name__ == '__main__':
    Game().mainloop()
    # game = Game()
    # game.board = Fib("TempUser")
    # print(game.board)
    # input("Press Enter to continue")
    # game.draw_board()
    # game.mainloop()
    # print(game.board)
