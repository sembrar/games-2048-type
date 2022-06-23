import json

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


class ForLeaderBoardDisplay:

    def __init__(self):
        # noinspection PyUnresolvedReferences
        self._leader_board_details = []  # type: list[dict]
        self._retrieve_from_file()
        return

    def _retrieve_from_file(self):
        try:
            with open(_LEADER_BOARD_FILE) as f:
                _details = json.loads(f.read().strip())
                for key in _details:  # type: str
                    print(key)
                    self._leader_board_details.append({})

                    user_name, game_name, grid_size, winning_tile, winning_tile_as_int = \
                        key.split(_SEPARATOR_IN_LEADER_BOARD_KEYS)
                    grid_size = int(grid_size)
                    winning_tile_as_int = int(winning_tile_as_int)

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
    leader_board_display = ForLeaderBoardDisplay()
    print(leader_board_display)
