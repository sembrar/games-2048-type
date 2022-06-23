import json
from MyModules.Widgets.ScrolledWidgets.ScrolledFrame import ScrolledFrame as _ScrolledFrame
from tkinter import Tk as _Tk, Frame as _tkFrame
from tkinter.ttk import Label as _ttkLabel, Button as _ttkButton, Scrollbar as _ttkScrollbar

_LEADER_BOARD_FILE = 'data/leader-boards.json'

_SEPARATOR_IN_LEADER_BOARD_KEYS = '__________'

_KEY_NUM_GAMES_PLAYED = 'key-num-games-played'
_KEY_NUM_GAMES_WON = 'key-num-games-won'
_KEY_NUM_GAMES_LOST = 'key-num-games-lost'
_KEY_WIN_RATE = 'key-win-rate'
_KEY_TOTAL_NUM_MOVES_PLAYED = 'key-total-num-moves-played'
_KEY_TOTAL_NUM_MOVES_PLAYED_IN_WON_GAMES = _KEY_TOTAL_NUM_MOVES_PLAYED + '-in-won-games'
_KEY_TOTAL_NUM_MOVES_PLAYED_IN_LOST_GAMES = _KEY_TOTAL_NUM_MOVES_PLAYED + '-in-lost-games'
_KEY_NUM_MOVES_IN_FASTEST_WIN = 'key-fastest-win-in'
_KEY_NUM_MOVES_IN_SLOWEST_LOSE = 'key-slowest-lose-in'
_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES = 'key-highest-tile-reached-in-lost-games'
_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES_AS_INT = _KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES + '-as-int'
_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE = 'key-highest-tile-reached-in-slowest-lose'
_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE_AS_INT = _KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE + '-as-int'


class LeaderBoard:

    # noinspection PyStatementEffect
    # what are the valid changes for a new leaderboard line?
    # user-name, game-name, grid-size, winning-tile, winning-tile-as-in

    def __init__(self):
        self._leader_board_details = {}
        self._retrieve_from_file()

    def update_leader_board_with(self, user_name, game_name, grid_size, winning_tile, is_game_won, num_moves_played,
                                 tile_str_to_int_function, highest_tile_reached_if_game_lost=None):
        """
        :type user_name: str
        :type game_name: str
        :type grid_size: int
        :type winning_tile: str
        :type is_game_won: bool
        :type num_moves_played: int
        :type highest_tile_reached_if_game_lost: str
        :type tile_str_to_int_function: lambda
        :rtype:
        """
        key = self._get_key(user_name, game_name, grid_size, winning_tile, tile_str_to_int_function)

        if key not in self._leader_board_details:
            # create new detail
            self._leader_board_details[key] = {}
            self._leader_board_details[key][_KEY_NUM_GAMES_PLAYED] = 0
            self._leader_board_details[key][_KEY_NUM_GAMES_WON] = 0
            self._leader_board_details[key][_KEY_NUM_GAMES_LOST] = 0
            self._leader_board_details[key][_KEY_WIN_RATE] = 0
            self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED] = 0
            self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED_IN_WON_GAMES] = 0
            self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED_IN_LOST_GAMES] = 0
            self._leader_board_details[key][_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES] = None
            self._leader_board_details[key][_KEY_NUM_MOVES_IN_FASTEST_WIN] = None
            self._leader_board_details[key][_KEY_NUM_MOVES_IN_SLOWEST_LOSE] = None
            self._leader_board_details[key][_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES_AS_INT] = None
            self._leader_board_details[key][_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE] = None
            self._leader_board_details[key][_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE_AS_INT] = None

        # update with given details
        self._leader_board_details[key][_KEY_NUM_GAMES_PLAYED] += 1

        if is_game_won:
            self._leader_board_details[key][_KEY_NUM_GAMES_WON] += 1
            self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED_IN_WON_GAMES] += num_moves_played
            if self._leader_board_details[key][_KEY_NUM_MOVES_IN_FASTEST_WIN] is None or \
                    self._leader_board_details[key][_KEY_NUM_MOVES_IN_FASTEST_WIN] > num_moves_played:
                self._leader_board_details[key][_KEY_NUM_MOVES_IN_FASTEST_WIN] = num_moves_played
        else:
            self._leader_board_details[key][_KEY_NUM_GAMES_LOST] += 1
            self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED_IN_LOST_GAMES] += num_moves_played
            if self._leader_board_details[key][_KEY_NUM_MOVES_IN_SLOWEST_LOSE] is None or \
                    self._leader_board_details[key][_KEY_NUM_MOVES_IN_SLOWEST_LOSE] < num_moves_played:
                self._leader_board_details[key][_KEY_NUM_MOVES_IN_SLOWEST_LOSE] = num_moves_played
                self._leader_board_details[key][_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE] = \
                    highest_tile_reached_if_game_lost
                self._leader_board_details[key][
                    _KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE_AS_INT] = tile_str_to_int_function(
                    highest_tile_reached_if_game_lost)

            assert highest_tile_reached_if_game_lost is not None

            current_highest_tile_in_lost_games = self._leader_board_details[key][
                _KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES]

            if current_highest_tile_in_lost_games is None or \
                    tile_str_to_int_function(current_highest_tile_in_lost_games) < \
                    tile_str_to_int_function(highest_tile_reached_if_game_lost):
                new_highest_tile_in_lost_games = highest_tile_reached_if_game_lost
            else:
                new_highest_tile_in_lost_games = current_highest_tile_in_lost_games

            self._leader_board_details[key][
                _KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES] = new_highest_tile_in_lost_games

            self._leader_board_details[key][
                _KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES_AS_INT] = tile_str_to_int_function(
                new_highest_tile_in_lost_games)

        self._leader_board_details[key][_KEY_WIN_RATE] = \
            float(self._leader_board_details[key][_KEY_NUM_GAMES_WON]) / self._leader_board_details[key][
                _KEY_NUM_GAMES_PLAYED]

        self._leader_board_details[key][_KEY_TOTAL_NUM_MOVES_PLAYED] += num_moves_played

        self._save_to_file()

    @staticmethod
    def _get_key(user_name, game_name, grid_size, winning_tile, tile_str_to_int_conversion):
        """
        :type user_name: str
        :type game_name: str
        :type grid_size: int
        :type winning_tile: str
        :type tile_str_to_int_conversion: lambda
        :rtype: str
        """
        return _SEPARATOR_IN_LEADER_BOARD_KEYS.join((user_name, game_name, str(grid_size), str(winning_tile),
                                                     str(tile_str_to_int_conversion(winning_tile))))

    def _save_to_file(self):
        with open(_LEADER_BOARD_FILE, 'w') as f:
            f.write(json.dumps(self._leader_board_details, indent=2))

    def _retrieve_from_file(self):
        try:
            with open(_LEADER_BOARD_FILE) as f:
                self._leader_board_details = json.loads(f.read().strip())
            print("Data read from LeaderBoardsFile")
        except IOError:
            print("LeaderBoardsFile is not yet created by the program!")

    def __str__(self):
        return json.dumps(self._leader_board_details, indent=2)


_KEY_USER_NAME = 'key-user-name'
_KEY_GAME_NAME = 'key-game-name'
_KEY_GRID_SIZE = 'key-grid-size'
_KEY_WINNING_TILE = 'key-winning-tile'
_KEY_WINNING_TILE_AS_INT = _KEY_WINNING_TILE + '-as-int'


class LeaderBoardDisplay:
    detail_user_name = 'User name'
    detail_grid_size = 'Grid size'
    detail_winning_tile = 'Winning Tile'
    detail_games_played_won_lost = 'Games played\n  (Won,Lost)'
    detail_win_rate = 'Win rate'
    detail_num_moves_played_in_games_won_lost = '         Total moves played\n(In Won games,In Lost Games)'
    detail_highest_tile_reached_in_lost_games = 'Highest Tile Reached in Lost Games'
    detail_fastest_win_in = 'Moves in Fastest Win'
    detail_slowest_lose_in_and_highest_tile_reached = '    Moves in Slowest Lose\n(And Highest Tile Reached)'

    font_leader_board_detail = '"Times New Roman" 13'

    details = (detail_user_name, detail_grid_size, detail_winning_tile, detail_games_played_won_lost,
               detail_win_rate, detail_num_moves_played_in_games_won_lost,
               detail_highest_tile_reached_in_lost_games,
               detail_fastest_win_in, detail_slowest_lose_in_and_highest_tile_reached)

    def __init__(self, game_name):
        # noinspection PyUnresolvedReferences
        self._leader_board_details = []  # type: list[dict]
        self._retrieve_from_file(game_name)

        if len(self._leader_board_details) == 0:
            if __name__ != '__main__':
                raise AttributeError

        root = _Tk()
        root.title('LeaderBoard for "%s"' % game_name)
        root.iconbitmap('icon.ico')

        _temp_scrollbar = _ttkScrollbar(root)
        _temp_scrollbar.grid(row=1, column=len(self.details))
        # _temp_scrollbar2 = _ttkScrollbar(root)
        # _temp_scrollbar2.grid(row=1, column=len(self.details) + 1)

        self.scroll_frame = _ScrolledFrame(root, horizontal_scroll=False)
        self.scroll_frame.grid(row=1, column=0, columnspan=len(self.details) + 2, sticky='nsew')
        root.rowconfigure(1, weight=1)
        root.columnconfigure(len(self.details), weight=1)

        for detail_index in range(len(self.details)):
            detail = self.details[detail_index]
            _temp_button = _ttkButton(
                self.scroll_frame, text=max(detail.split('\n'), key=lambda x: len(x)), state='disabled')
            _temp_button.grid(row=0, column=detail_index)

        self._leader_board_detail_key_widget_list_dict = {}  # type: dict[str, list]

        for leader_board_detail_index in range(len(self._leader_board_details)):

            leader_board_detail = self._leader_board_details[leader_board_detail_index]

            key = self._get_key_for_detail(leader_board_detail)

            self._leader_board_detail_key_widget_list_dict[key] = []

            for detail_index in range(len(self.details)):
                detail = self.details[detail_index]
                widget = self._get_filled_widget_for_detail_from_leader_board_detail(
                    detail, leader_board_detail, self.scroll_frame)
                widget.grid(row=leader_board_detail_index, column=detail_index, sticky='nsew')
                self._leader_board_detail_key_widget_list_dict[key].append(widget)

                _temp_widget = self._get_filled_widget_for_detail_from_leader_board_detail(
                    detail, leader_board_detail, root)
                _temp_widget.grid(row=0, column=detail_index)

        for detail_index in range(len(self.details)):
            detail = self.details[detail_index]
            button = _ttkButton(root, text=detail)
            button.bind("<ButtonRelease-1>", self.ttk_button_press_release)
            button.grid(row=0, column=detail_index, sticky='news')

        self.sort_by_detail(self.detail_num_moves_played_in_games_won_lost)

        root.mainloop()

    def ttk_button_press_release(self, event):
        if not event.widget.instate(["!disabled", "hover"]):
            return
        text = event.widget.cget('text')
        assert text in self.details
        descending_order = False
        if text == self.detail_user_name:
            descending_order = False
        elif text == self.detail_grid_size:
            descending_order = True
        elif text == self.detail_games_played_won_lost:
            descending_order = True
        elif text == self.detail_win_rate:
            descending_order = True
        elif text == self.detail_num_moves_played_in_games_won_lost:
            descending_order = True
        elif text == self.detail_highest_tile_reached_in_lost_games:
            descending_order = True
        elif text == self.detail_fastest_win_in:
            descending_order = False
        elif text == self.detail_slowest_lose_in_and_highest_tile_reached:
            descending_order = True
        elif text == self.detail_winning_tile:
            descending_order = True
        self.sort_by_detail(text, descending_order)

    def sort_by_detail(self, detail, descending=False):

        assert detail in self.details

        try:

            if detail == self.detail_user_name:
                self._leader_board_details.sort(key=lambda x: x[_KEY_USER_NAME], reverse=descending)
            elif detail == self.detail_grid_size:
                self._leader_board_details.sort(key=lambda x: x[_KEY_GRID_SIZE], reverse=descending)
            elif detail == self.detail_games_played_won_lost:
                self._leader_board_details.sort(key=lambda x: x[_KEY_NUM_GAMES_PLAYED], reverse=descending)
            elif detail == self.detail_win_rate:
                self._leader_board_details.sort(key=lambda x: x[_KEY_WIN_RATE], reverse=descending)
            elif detail == self.detail_num_moves_played_in_games_won_lost:
                self._leader_board_details.sort(key=lambda x: x[_KEY_TOTAL_NUM_MOVES_PLAYED], reverse=descending)
            elif detail == self.detail_highest_tile_reached_in_lost_games:
                self._leader_board_details.sort(key=lambda x: x[_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES_AS_INT],
                                                reverse=descending)
            elif detail == self.detail_fastest_win_in:
                self._leader_board_details.sort(key=lambda x: x[_KEY_NUM_MOVES_IN_FASTEST_WIN], reverse=descending)
            elif detail == self.detail_slowest_lose_in_and_highest_tile_reached:
                self._leader_board_details.sort(key=lambda x: x[_KEY_NUM_MOVES_IN_SLOWEST_LOSE], reverse=descending)
            elif detail == self.detail_winning_tile:
                self._leader_board_details.sort(key=lambda x: x[_KEY_WINNING_TILE_AS_INT], reverse=descending)

        except TypeError:
            print("Couldn't sort")

        for leader_board_detail_index in range(len(self._leader_board_details)):
            leader_board_detail = self._leader_board_details[leader_board_detail_index]
            key = self._get_key_for_detail(leader_board_detail)

            if leader_board_detail_index & 1:
                color = 'cyan'
            else:
                color = 'light blue'

            for i in range(len(self._leader_board_detail_key_widget_list_dict[key])):
                self._leader_board_detail_key_widget_list_dict[key][i].grid(row=leader_board_detail_index, column=i)
                self._leader_board_detail_key_widget_list_dict[key][i].configure(bg=color)
                for child in self._leader_board_detail_key_widget_list_dict[key][i].winfo_children():
                    child.configure(background=color)

    def _get_filled_widget_for_detail_from_leader_board_detail(self, detail, leader_board_detail, master):
        assert detail in self.details

        frame = _tkFrame(master)

        if detail == self.detail_user_name:
            _ttkLabel(frame, text=leader_board_detail[_KEY_USER_NAME], font=self.font_leader_board_detail,
                      anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_grid_size:
            _ttkLabel(frame, text=leader_board_detail[_KEY_GRID_SIZE], font=self.font_leader_board_detail,
                      anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_winning_tile:
            _ttkLabel(frame, text=leader_board_detail[_KEY_WINNING_TILE], font=self.font_leader_board_detail,
                      anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_games_played_won_lost:
            _ttkLabel(frame, text=leader_board_detail[_KEY_NUM_GAMES_PLAYED], font=self.font_leader_board_detail
                      ).grid(row=0, column=1)

            _ttkLabel(frame, text='(', font=self.font_leader_board_detail).grid(row=0, column=2)

            _ttkLabel(frame, text=leader_board_detail[_KEY_NUM_GAMES_WON], font=self.font_leader_board_detail,
                      foreground='green').grid(row=0, column=3)

            _ttkLabel(frame, text=',', font=self.font_leader_board_detail).grid(row=0, column=4)

            _ttkLabel(frame, text=leader_board_detail[_KEY_NUM_GAMES_LOST], font=self.font_leader_board_detail,
                      foreground='red').grid(row=0, column=5)

            _ttkLabel(frame, text=')', font=self.font_leader_board_detail).grid(row=0, column=6)

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(7, weight=1)

        elif detail == self.detail_win_rate:
            _ttkLabel(frame, text='%.3f' % leader_board_detail[_KEY_WIN_RATE], font=self.font_leader_board_detail,
                      anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_num_moves_played_in_games_won_lost:
            _ttkLabel(frame, text=leader_board_detail[_KEY_TOTAL_NUM_MOVES_PLAYED], font=self.font_leader_board_detail
                      ).grid(row=0, column=1)

            _ttkLabel(frame, text='(', font=self.font_leader_board_detail).grid(row=0, column=2)

            _ttkLabel(frame, text=leader_board_detail[_KEY_TOTAL_NUM_MOVES_PLAYED_IN_WON_GAMES],
                      font=self.font_leader_board_detail, foreground='green').grid(row=0, column=3)

            _ttkLabel(frame, text=',', font=self.font_leader_board_detail).grid(row=0, column=4)

            _ttkLabel(frame, text=leader_board_detail[_KEY_TOTAL_NUM_MOVES_PLAYED_IN_LOST_GAMES],
                      font=self.font_leader_board_detail, foreground='red').grid(row=0, column=5)

            _ttkLabel(frame, text=')', font=self.font_leader_board_detail).grid(row=0, column=6)

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(7, weight=1)

        elif detail == self.detail_highest_tile_reached_in_lost_games:
            _ttkLabel(frame,
                      text=leader_board_detail[_KEY_HIGHEST_TILE_REACHED_IN_LOST_GAMES],
                      font=self.font_leader_board_detail, anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_fastest_win_in:
            _ttkLabel(frame,
                      text=leader_board_detail[_KEY_NUM_MOVES_IN_FASTEST_WIN],
                      font=self.font_leader_board_detail, anchor='n').grid(row=0, column=0, sticky='ew')
            frame.columnconfigure(0, weight=1)

        elif detail == self.detail_slowest_lose_in_and_highest_tile_reached:
            _ttkLabel(frame, text=leader_board_detail[_KEY_NUM_MOVES_IN_SLOWEST_LOSE],
                      font=self.font_leader_board_detail).grid(row=0, column=1)

            _ttkLabel(frame, text='(', font=self.font_leader_board_detail).grid(row=0, column=2)

            _ttkLabel(frame, text=leader_board_detail[_KEY_HIGHEST_TILE_REACHED_IN_SLOWEST_LOSE],
                      font=self.font_leader_board_detail, foreground='red').grid(row=0, column=3)

            _ttkLabel(frame, text=')', font=self.font_leader_board_detail).grid(row=0, column=4)

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(5, weight=1)

        return frame

    @staticmethod
    def _get_key_for_detail(detail):
        """
        :type detail: dict
        :rtype: str
        """
        user_name = detail[_KEY_USER_NAME]
        grid_size = detail[_KEY_GRID_SIZE]
        winning_tile = detail[_KEY_WINNING_TILE]
        return _SEPARATOR_IN_LEADER_BOARD_KEYS.join((user_name, str(grid_size), str(winning_tile)))

    def _retrieve_from_file(self, required_game_name):
        try:
            with open(_LEADER_BOARD_FILE) as f:
                _details = json.loads(f.read().strip())
                for key in _details:  # type: str

                    user_name, game_name, grid_size, winning_tile, winning_tile_as_int = \
                        key.split(_SEPARATOR_IN_LEADER_BOARD_KEYS)

                    if required_game_name != game_name:
                        continue

                    grid_size = int(grid_size)
                    winning_tile_as_int = int(winning_tile_as_int)

                    self._leader_board_details.append({})

                    self._leader_board_details[-1][_KEY_USER_NAME] = user_name
                    self._leader_board_details[-1][_KEY_GAME_NAME] = game_name
                    self._leader_board_details[-1][_KEY_GRID_SIZE] = grid_size
                    self._leader_board_details[-1][_KEY_WINNING_TILE] = winning_tile
                    self._leader_board_details[-1][_KEY_WINNING_TILE_AS_INT] = winning_tile_as_int

                    self._leader_board_details[-1].update(_details[key])
            print("Data read from LeaderBoardsFile")
        except IOError:
            print("LeaderBoardsFile is not yet created by the program!")

    def __str__(self):
        return json.dumps(self._leader_board_details, indent=2)


if __name__ == '__main__':
    # leader_board = LeaderBoard()
    # leader_board.update_leader_board_with("Sagar", "2048", 4, '256', True, 150, int)
    # leader_board.update_leader_board_with("Sagar", "2048", 4, '2048', False, 200, int, '256')
    # print("LeaderBoard:", leader_board, sep='\n')
    leader_board_display = LeaderBoardDisplay("2048")
    # print(leader_board_display)
