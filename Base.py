import random
import os
import json

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
SAVE_IF_NEEDED_AND_QUIT = 4
MOVE_NAMES = ["left", "right", "up", "down", "save if needed and quit"]

# todo functions and data to be overridden in derived classes are
# GAME_NAME
# DEFAULT_TILE
# DEFAULT_GRID_SIZE
# DEFAULT_WINNING_TILE; set this to None if winning_tile is dependent on grid size (for GUI purpose)
# WINNING_TILE_CHOICES; set to empty tuple if winning tile is dependent on grid size
# init if winning_tile is dependent on grid size
# are_they_merge_able
# get_merge_result

_USER_NAME_FOR_TEMP_USES = "__temp-user-for-functions__"


class Base:
    GAME_NAME = 'KeepAdding'
    DEFAULT_TILE = 1
    DEFAULT_GRID_SIZE = 4
    DEFAULT_WINNING_TILE = 100
    WINNING_TILE_CHOICES = (DEFAULT_WINNING_TILE,)

    _KEY_BOARD_SIZE = 'key-board-size'
    _KEY_BOARD = 'key-grid'
    _KEY_WINNING_TILE = 'key-winning-tile'
    _KEY_GAME_ENDED = 'key-game-ended'
    _KEY_NUM_MOVES_USED = 'key-num-moves-used'
    _KEY_USER_NAME = 'key-user-name'
    _KEY_MOVEMENTS = 'key-movements'

    def __init__(self, user_name, grid_size=None, winning_tile=None):

        if grid_size is None:
            grid_size = self.DEFAULT_GRID_SIZE
        if winning_tile is None:
            winning_tile = self.DEFAULT_WINNING_TILE

        self._game_info = {self._KEY_USER_NAME: user_name, self._KEY_BOARD_SIZE: grid_size,
                           self._KEY_WINNING_TILE: winning_tile,
                           self._KEY_BOARD: [[0 for _ in range(grid_size)] for _ in range(grid_size)],
                           self._KEY_GAME_ENDED: False, self._KEY_NUM_MOVES_USED: 0,
                           self._KEY_MOVEMENTS: {}}

        self._set_1_random_tile_to_default_tile()
        self._set_1_random_tile_to_default_tile()

    def get_board_size(self):
        return self._game_info[self._KEY_BOARD_SIZE]

    def get_winning_tile(self):
        return self._game_info[self._KEY_WINNING_TILE]

    def game_ended(self):
        return self._game_info[self._KEY_GAME_ENDED]

    def get_num_moves_used(self):
        return self._game_info[self._KEY_NUM_MOVES_USED]

    def get_user_name(self):
        return self._game_info[self._KEY_USER_NAME]

    def get_cell(self, row, col):
        return self._game_info[self._KEY_BOARD][row][col]

    def set_board_size(self, board_size):
        self._game_info[self._KEY_BOARD_SIZE] = board_size

    def set_winning_tile(self, winning_tile):
        self._game_info[self._KEY_WINNING_TILE] = winning_tile

    def set_game_end_status(self):
        self._game_info[self._KEY_GAME_ENDED] = self.is_game_won() or self.is_game_lost()

    def set_num_moves_used(self, num_moves_used):
        self._game_info[self._KEY_NUM_MOVES_USED] = num_moves_used

    def increment_num_moves_used(self):
        self.set_num_moves_used(self.get_num_moves_used() + 1)

    def set_user_name(self, user_name):
        self._game_info[self._KEY_USER_NAME] = user_name

    def set_cell(self, row, col, value):
        self._game_info[self._KEY_BOARD][row][col] = value

    def __str__(self):
        s = "Game: %s\n" % self.GAME_NAME
        s += "Board size: %d" % self.get_board_size()
        s += "; Win Condition: Reach " + str(self.get_winning_tile()) + '\n'
        s += "User: %s\n" % self.get_user_name()
        s += "Grid:\n"

        board = self._game_info[self._KEY_BOARD]

        cells = []
        for r in board:
            for c in r:
                cells.append(str(c))

        width = len(max(cells, key=lambda x: len(x)))

        for r in board:
            for c in r:
                s += str(c).rjust(width, ' ') + ' '
            s += '\n'

        s += "Num moves used until now: %d" % self.get_num_moves_used()

        return s

    def _set_1_random_tile_to_default_tile(self):
        empties = []
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size()):
                if self.get_cell(r, c) == 0:
                    empties.append((r, c))

        try:
            r, c = random.choice(empties)
            self.set_cell(r, c, self.DEFAULT_TILE)
        except IndexError:
            pass

    def _make_left_move(self):
        self._bring_left()
        self._merge_left()
        self._bring_left()

    def _make_right_move(self):
        self._bring_right()
        self._merge_right()
        self._bring_right()

    def _make_up_move(self):
        self._transpose()
        self.perform_action(LEFT)
        self._transpose()

    def _make_down_move(self):
        self._transpose()
        self.perform_action(RIGHT)
        self._transpose()

    def is_game_won(self):
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size()):
                if self.get_cell(r, c) == self.get_winning_tile():
                    return True
        return False

    def is_game_lost(self):
        try:
            o = type(self)(_USER_NAME_FOR_TEMP_USES, self.get_board_size(), self.get_winning_tile())
        except TypeError:
            o = type(self)(_USER_NAME_FOR_TEMP_USES, self.get_board_size())

        for m in (UP, DOWN, RIGHT, LEFT):

            # copy into o
            o._copy_board_from(self)

            o.perform_action(m)

            if not self._are_grids_same(o):
                # print(MOVE_NAMES[m], "is available")
                # print(self, o)
                return False

        return True

    def _are_grids_same(self, other):
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size()):
                if self.get_cell(r, c) != other.get_cell(r, c):
                    return False
        return True

    def _copy_board_from(self, other):
        """
        :type other: Base
        """
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size()):
                self.set_cell(r, c, other.get_cell(r, c))

    # noinspection PyMethodMayBeStatic
    def are_they_merge_able(self, a, b):
        # they are not mergeable if any of them is empty
        return not (a == 0 or b == 0)

    # noinspection PyMethodMayBeStatic
    def get_merge_result(self, a, b):
        return a + b

    def perform_action(self, action):

        # don't call set_game_end_status function in this function => it creates recursion because
        # in that function, there is a call to is_game_lost function which calls perform_action on
        # some other object of the same class

        if self.game_ended():
            self.clear_movements()
            return

        assert action in (LEFT, RIGHT, UP, DOWN, SAVE_IF_NEEDED_AND_QUIT)

        self.clear_and_initialize_movements()

        try:
            o = type(self)(_USER_NAME_FOR_TEMP_USES, self.get_board_size(), self.get_winning_tile())
        except TypeError:
            o = type(self)(_USER_NAME_FOR_TEMP_USES, self.get_board_size())
        o._copy_board_from(self)

        if action == UP:
            self._make_up_move()
        elif action == DOWN:
            self._make_down_move()
        elif action == LEFT:
            self._make_left_move()
        elif action == RIGHT:
            self._make_right_move()
        elif action == SAVE_IF_NEEDED_AND_QUIT:
            self.save_game_if_needed()
        else:
            print("Never should have come here!!!")  # it won't come here

        if not o._are_grids_same(self):  # valid move
            if action not in (UP, DOWN):  # up or down calls perform_action with LEFT and RIGHT respectively
                self.increment_num_moves_used()
                self._set_1_random_tile_to_default_tile()
            self.process_movements_after_all_finished(action)
        else:
            self.clear_movements()

    def clear_and_initialize_movements(self):
        self.clear_movements()
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size()):
                if self.get_cell(r, c) != 0:  # if the block is not empty
                    self._game_info[self._KEY_MOVEMENTS][(r, c)] = (r, c)  # the block moved to the same cell :-)
        # if self.get_user_name() != _USER_NAME_FOR_TEMP_USES:
        #     print("After initialization:", self.get_movements(), sep='\n')

    def update_in_movements(self, r1, c1, r2, c2):
        # update if r1, c1 is in some value: note that initially keys and values are same
        for key in self._game_info[self._KEY_MOVEMENTS].keys():
            r, c = self._game_info[self._KEY_MOVEMENTS][key]
            if r == r1 and c == c1:
                self._game_info[self._KEY_MOVEMENTS][key] = (r2, c2)

    def clear_movements(self):
        self._game_info[self._KEY_MOVEMENTS] = {}

    def get_movements(self):
        return self._game_info[self._KEY_MOVEMENTS]

    def process_movements_after_all_finished(self, action):
        # remove waste movements - those in which cell stayed at the same place
        # transpose if action is UP or DOWN
        a_copy = dict(self.get_movements())

        # if self.get_user_name() != _USER_NAME_FOR_TEMP_USES:
        #     print("Movements before processing for user '%s'" % self.get_user_name(), self.get_movements(), sep='\n')

        self.clear_movements()

        for key in a_copy.keys():
            r1, c1 = key
            r2, c2 = a_copy[key]
            if r1 != r2 or c1 != c2:
                if action in (UP, DOWN):
                    self._game_info[self._KEY_MOVEMENTS][(c1, r1)] = (c2, r2)
                else:
                    self._game_info[self._KEY_MOVEMENTS][(r1, c1)] = (r2, c2)

        # if self.get_user_name() != _USER_NAME_FOR_TEMP_USES:
        #     print("Movements after processing for user '%s'" % self.get_user_name(), self.get_movements(), sep='\n')

    def _bring_left(self):
        for r in range(self.get_board_size()):
            index = 0
            for c in range(self.get_board_size()):
                if self.get_cell(r, c) != 0:
                    self.set_cell(r, index, self.get_cell(r, c))
                    self.update_in_movements(r, c, r, index)
                    index += 1
            for c in range(index, self.get_board_size()):
                self.set_cell(r, c, 0)

    def _bring_right(self):
        for r in range(self.get_board_size()):
            index = self.get_board_size() - 1
            for c in range(self.get_board_size() - 1, -1, -1):
                if self.get_cell(r, c) != 0:
                    self.set_cell(r, index, self.get_cell(r, c))
                    self.update_in_movements(r, c, r, index)
                    index -= 1
            for c in range(index, -1, -1):
                self.set_cell(r, c, 0)

    def _merge_left(self):
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size() - 1):
                o1 = self.get_cell(r, c)
                o2 = self.get_cell(r, c + 1)
                if self.are_they_merge_able(o1, o2):
                    temp = self.get_merge_result(o1, o2)
                    self.set_cell(r, c, 0)
                    self.set_cell(r, c + 1, 0)
                    self.set_cell(r, c, temp)
                    self.update_in_movements(r, c + 1, r, c)

    def _merge_right(self):
        for r in range(self.get_board_size()):
            for c in range(self.get_board_size() - 1, 0, -1):
                o1 = self.get_cell(r, c)
                o2 = self.get_cell(r, c - 1)
                if self.are_they_merge_able(o1, o2):
                    temp = self.get_merge_result(o1, o2)
                    self.set_cell(r, c, 0)
                    self.set_cell(r, c - 1, 0)
                    self.set_cell(r, c, temp)
                    self.update_in_movements(r, c - 1, r, c)

    def _transpose(self):
        for r in range(self.get_board_size()):
            for c in range(r + 1, self.get_board_size()):
                temp = self.get_cell(r, c)
                self.set_cell(r, c, self.get_cell(c, r))
                self.set_cell(c, r, temp)

    def play(self):
        while not self.game_ended():
            # os.system("cls")
            print(self)
            action = input("Your action: ").strip()
            try:
                assert action in 'wWaAsSdDqQ'
                if action in 'wW':
                    a = UP
                elif action in 'sS':
                    a = DOWN
                elif action in 'aA':
                    a = LEFT
                elif action in 'dD':
                    a = RIGHT
                else:
                    print("Quit command received")
                    self.save_game_if_needed()
                    return
                self.perform_action(a)
                self.set_game_end_status()
            except AssertionError:
                print("action should be one of", tuple('wWaAsSdD'))
        os.system("cls")
        print(self)
        if self.is_game_lost():
            print("Game lost!!  :-(")
        if self.is_game_won():
            print("Game Won!!   :-)")

    def _get_game_save_file_rel_path(self):
        if not os.path.isdir("data"):
            os.makedirs("data")
        return 'data/%s-%s.json' % (self.GAME_NAME, self.get_user_name())

    def save_game_if_needed(self):
        if self.game_ended() or self.get_num_moves_used() == 0:
            return
        self.clear_movements()
        with open(self._get_game_save_file_rel_path(), 'w') as f:
            f.write(json.dumps(self._game_info, indent=1))
        print("Game Saved")

    def does_saved_game_exist_for_this_user(self):
        return os.path.isfile(self._get_game_save_file_rel_path())

    def retrieve_if_saved_game_exists(self):
        if not self.does_saved_game_exist_for_this_user():
            return
        with open(self._get_game_save_file_rel_path()) as f:
            json_string = f.read().strip()
            self._game_info = json.loads(json_string)  # type: Base
            self.set_game_end_status()
        os.system('del "%s"' % os.path.abspath(self._get_game_save_file_rel_path()))


if __name__ == '__main__':
    game = Base("TempUser")
    game.retrieve_if_saved_game_exists()
    game.play()
