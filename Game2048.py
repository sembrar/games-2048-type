from Base import Base


class TwoZeroFourEight(Base):

    GAME_NAME = '2048'
    DEFAULT_TILE = 1
    DEFAULT_WINNING_TILE = 2048
    DEFAULT_GRID_SIZE = 4
    WINNING_TILE_CHOICES = tuple(list(map(lambda x: 2**x, range(11, 21))) + [-1])

    def are_they_merge_able(self, a, b):
        if super().are_they_merge_able(a, b):
            return a == b

    def get_merge_result(self, a, b):
        return a + b


if __name__ == '__main__':
    game = TwoZeroFourEight("TempUser")
    game.retrieve_if_saved_game_exists()
    game.play()
