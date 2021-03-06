from Base import Base


# noinspection PyPep8Naming
def nFib(n):
    """
    :type n: int
    """
    assert n > 0

    if n == 1:
        return 0
    if n == 2:
        return 1

    f1, f2 = 0, 1

    while n > 2:
        f1, f2 = f2, f1 + f2
        n -= 1

    return f2


class Fib(Base):

    GAME_NAME = "Fibonacci"
    DEFAULT_TILE = 1
    DEFAULT_GRID_SIZE = 4
    WINNING_TILE_CHOICES = tuple(map(lambda x: nFib(x), range(4, 4+10)))
    DEFAULT_WINNING_TILE = WINNING_TILE_CHOICES[0]

    def are_they_merge_able(self, a, b):
        if not super().are_they_merge_able(a, b):
            return False

        # Check if they are consecutive Fibs

        big = max(a, b)
        small = min(a, b)

        fib1 = 1  # 0 is not merge able
        fib2 = 1

        while fib2 < big:
            temp = fib2
            fib2 += fib1
            fib1 = temp

        if small == fib1 and big == fib2:
            return True
        return False

    def get_merge_result(self, a, b):
        return a+b


if __name__ == '__main__':
    game = Fib("TempUser", 2)
    game.retrieve_if_saved_game_exists()
    game.play()
