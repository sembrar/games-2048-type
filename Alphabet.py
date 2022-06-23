from Base import Base


class Alphabet(Base):

    GAME_NAME = 'Alphabet'
    DEFAULT_TILE = 'A'
    DEFAULT_WINNING_TILE = 'Z'
    DEFAULT_GRID_SIZE = 4
    WINNING_TILE_CHOICES = tuple('DEFGHIJKLMNOPQRSTUVWXYZ')

    def are_they_merge_able(self, a, b):
        if super().are_they_merge_able(a, b):
            return a == b

    def get_merge_result(self, a, b):
        return str(chr(ord(a) + 1))


if __name__ == '__main__':
    game = Alphabet("TempUser")
    game.retrieve_if_saved_game_exists()
    game.play()
