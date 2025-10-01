import random
import keyboard as kb
import time

"""
Add main menu
"""


class Cell:
    def __init__(self, xy: tuple[int, int]):
        self.x, self.y = xy
        self.near = 0

        self.is_mine = False
        self.is_flag = False
        self.is_open = False

    def open(self):
        if self.is_open:
            return

        self.is_open = True

    def place_flag(self):
        if self.is_open:
            return 0
        self.is_flag = not self.is_flag
        if self.is_flag:
            return -1
        return 1

    @property
    def raw_string(self):
        return str(self)[str(self).rfind("\x1b") - 1:]

    def __str__(self):
        if not self.is_open:
            if self.is_flag:
                return Style.FLAG
            return Style.CLOSED
        if self.is_mine:
            return Style.MINE
        if self.near > 0:
            return Style.NUMBERS[self.near]
        return Style.EMPTY


class Style:
    COOL = "\x1b[92m" "(⌐■_■) <(Solved!)" "\x1b[0m"
    HAPPY = "\x1b[93m" "(^_^) <(You can do it!)" "\x1b[0m"
    DEAD = "\x1b[91m" "(x_x) <(Lose!)" "\x1b[0m"
    WALL = "\x1b[90m" "|" "\x1b[0m"

    EMPTY = "\x1b[0m" " " "\x1b[0m"
    CLOSED = "\x1b[90m" "#" "\x1b[0m"
    MINE = "\x1b[91m" "*" "\x1b[0m"
    DEAD_MINE = "\x1b[101;30m" "*" "\x1b[0m"
    FALSE_MINE = "\x1b[91m" "X" "\x1b[0m"
    FLAG = "\x1b[102;30m" "F" "\x1b[0m"

    NUMBERS = [EMPTY] + [f"\x1b[{col}m{num}\x1b[0m" for num, col in enumerate((94, 32, 91, 34, 31, 96, 95, 90), 1)]

    DEBUG = NUMBERS + [CLOSED, MINE, DEAD_MINE, FALSE_MINE, FLAG]


class Minesweeper:
    ROW = 16
    COLUMN = 16
    MINES = 40

    def __init__(self):
        self.game = False
        self.first = False
        self.restarted = False
        self.time = 0
        self.games = 0
        self.start_counter = 0

        self.buttons: list[list[Cell]] = []
        self.flags = self.MINES
        self.free_cells = self.ROW * self.COLUMN - self.MINES

        self.cursor = [0, 0]

    # --- ONE TIME ---

    def _neighbors(self, cell: Cell) -> list[Cell]:
        nbs = []

        for ay in range(cell.y - 1, cell.y + 2):
            if ay < 0 or ay >= self.ROW:
                continue
            for ax in range(cell.x - 1, cell.x + 2):
                if ax < 0 or ax >= self.COLUMN:
                    continue
                if self.buttons[ay][ax] == cell:
                    continue
                nbs.append(self.buttons[ay][ax])

        return nbs

    def set_dif(self, dif):
        match dif:
            case "Rookie":
                self.ROW, self.COLUMN, self.MINES = 9, 9, 10
            case "Normal":
                self.ROW, self.COLUMN, self.MINES = 16, 16, 40
            case "Expert":
                self.ROW, self.COLUMN, self.MINES = 16, 30, 99
            case _:
                self.ROW, self.COLUMN, self.MINES = 16, 16, 40

    def _bind(self):
        kb.add_hotkey("UP", lambda: self._change_cursor(y=-1))
        kb.add_hotkey("DOWN", lambda: self._change_cursor(y=1))
        kb.add_hotkey("LEFT", lambda: self._change_cursor(x=-1))
        kb.add_hotkey("RIGHT", lambda: self._change_cursor(x=1))

        ys = (-1, 1)
        xs = (-1, 1)

        for y, val_y in enumerate(["UP", "DOWN"]):
            for x, val_x in enumerate(["LEFT", "RIGHT"]):
                kb.add_hotkey(val_y + "+" + val_x, lambda a=ys[y], b=xs[x]: self._change_cursor(b, a))

        kb.add_hotkey("SPACE", lambda: self._on_open_pressed())
        kb.add_hotkey("r", self._restart)
        kb.add_hotkey("ESC", self._restart)
        kb.add_hotkey("f", lambda: self._flag(*self.cursor))
        kb.add_hotkey("TAB", lambda: self._flag(*self.cursor))

    def _create_buttons(self):
        for y in range(self.ROW):
            _line = []
            for x in range(self.COLUMN):
                cell = Cell((x, y))
                _line.append(cell)
            self.buttons.append(_line)

    def _create_mines(self, seed, exclude):
        random.seed(seed)
        cords = [(x, y) for x in range(self.COLUMN) for y in range(self.ROW)]
        cords.remove(exclude)

        for _ in range(self.MINES):
            cord = random.choice(cords)
            self.buttons[cord[1]][cord[0]].is_mine = True
            cords.remove(cord)

        self._recalc_near()

    def _recalc_near(self):
        for row in self.buttons:
            for cell in row:
                for nb in self._neighbors(cell):
                    if nb.is_mine:
                        cell.near += 1
                        # print(cell.x, cell.y, cell.near)
                # cell.open()

    # --- MULTI TIME ---

    def _enough_flags(self, cell):
        return len([i for i in self._neighbors(cell) if i.is_flag]) == cell.near

    def _game_over(self, win):
        self.game = False
        if not win:
            for row in self.buttons:
                for cell in row:
                    if cell.is_mine:
                        cell.open()
            self._draw()
        else:
            for row in self.buttons:
                for cell in row:
                    if not cell.is_mine:
                        cell.open()
                    else:
                        cell.is_flag = True
            self._draw(True)

    def _restart(self):
        self.game = False
        self.restarted = True

    def _on_open_pressed(self):
        if not self.game:
            self._restart()
            return
        x, y = self.cursor
        cell = self.buttons[y][x]
        if cell.is_flag:
            return
        if not cell.is_open:
            self._open_cell(x, y)
        else:
            if self._enough_flags(cell):
                for nb in self._neighbors(cell):
                    self._open_cell(nb.x, nb.y)
            else:
                self._flag(x, y)
        if self.free_cells > 0:
            self._draw()

    def _open_with_near(self, button):
        if button.is_flag:
            return
        queue: list[Cell] = [button]
        checked = []
        while queue:
            cur = queue[0]
            queue.remove(cur)
            if cur.is_flag:
                checked.append(cur)
                continue
            if cur.is_open:
                checked.append(cur)
                continue

            cur.open()
            self.free_cells -= 1

            if cur.near > 0:
                checked.append(cur)
                if not self._enough_flags(cur):
                    continue

            for neb in self._neighbors(cur):
                if not neb.is_mine:
                    queue.append(neb)

            checked.append(cur)

    def _flag(self, x, y):
        cell = self.buttons[y][x]
        if cell.is_open:
            if len([i for i in self._neighbors(cell) if not i.is_open]) == cell.near:
                for nb in self._neighbors(cell):
                    if not nb.is_open:
                        nb.is_flag = True
        else:
            flags = cell.place_flag()
            self.flags += flags
            if self.flags < 0:
                flags = cell.place_flag()
                self.flags += flags
        self._draw()

    def _open_cell(self, x, y):
        if self.buttons[y][x].is_flag:
            return
        if not self.game:
            return
        if self.first:
            self.first = False
            seed = time.time_ns() ** 2 % (10 ** 8)  # 28082121 - 8 on 26, 12 (If not first-clicked)
            self._create_mines(seed, tuple(self.cursor))
            print(f"[SEED] \x1b[33m{seed}\x1b[0m")
            self.start_counter = time.perf_counter()

        self._open_with_near(self.buttons[y][x])
        if self.buttons[y][x].is_mine:
            self.cursor = [x, y]
            self.game = False
            self._game_over(False)
        if self.free_cells == 0:
            self._game_over(True)
            return True
        # self._draw()

    def _change_cursor(self, x=0, y=0):
        if not self.game:
            return

        if 0 <= self.cursor[0] + x < self.COLUMN:
            self.cursor[0] += x
        # self.cursor[0] %= self.COLUMN
        if 0 <= self.cursor[1] + y < self.ROW:
            self.cursor[1] += y
        # self.cursor[1] %= self.ROW
        self._draw()

    def _draw(self, win=False):
        out = "\x1b[2J\x1b[H"

        if not self.game:
            if win:
                out += Style.COOL
            else:
                out += Style.DEAD
        else:
            out += Style.HAPPY
        out += "\n"
        if self.start_counter != 0:
            out += f"Time: {time.perf_counter() - self.start_counter:.0f}s\n"
        else:
            out += f"Time: -\n"
        out += f"Flags: {self.flags}\n"

        for y, row in enumerate(self.buttons):
            out += f"{(2 - len(str(y))) * " "}{y}" + Style.WALL
            for x, cell in enumerate(row):
                if y == self.cursor[1] and x == self.cursor[0]:
                    if self.game:
                        out += "\x1b[107;30m" + cell.raw_string
                    else:
                        if cell.is_mine:
                            out += Style.DEAD_MINE
                        else:
                            out += str(cell)
                else:
                    if not win and not self.game:
                        if cell.is_flag and not cell.is_mine:
                            out += Style.FALSE_MINE + Style.WALL
                            continue
                    out += str(cell)
                out += Style.WALL
            out += "\n"
        print(out.removesuffix("\n"))

    def _start(self):
        print("Start...")
        self.game = True
        self.first = True
        self._create_buttons()
        self.cursor = [0, 0]
        self.flags = self.MINES
        self.free_cells = self.ROW * self.COLUMN - self.MINES

        self._draw()
        while self.game:
            try:
                time.sleep(.01)

            except KeyboardInterrupt:
                return

        while not self.restarted:
            try:
                time.sleep(.01)

            except KeyboardInterrupt:
                return

        # if not self.restarted:
        #     try:
        #         kb.wait("ESC")
        #     except KeyboardInterrupt:
        #         return

        self.restarted = False
        self.buttons.clear()
        self.start_counter = 0
        self.games += 1
        self.game = False
        self.buttons.clear()
        self.flags = self.MINES
        self.free_cells = self.ROW * self.COLUMN - self.MINES
        self.time = 0
        self._start()

    def run(self):
        self._bind()
        self._start()
        print("\x1b[91m" "Game over" "\x1b[0m")


cursor = 0


def main():
    import os
    try:
        size = os.get_terminal_size()[0]

    except OSError:
        size = 120
    del os

    global cursor
    variants = ["Rookie", "Normal", "Expert"]

    def change_cursor(val):
        global cursor
        cursor += val
        cursor %= len(variants)
        draw()

    def rem():
        kb.remove_hotkey("UP")
        kb.remove_hotkey("DOWN")

    def draw():
        print("\x1b[2J\x1b[H")
        for line in (
                """

███╗░░░███╗██╗███╗░░██╗███████╗░██████╗░██╗░░░░░░░██╗███████╗███████╗██████╗░███████╗██████╗░
████╗░████║██║████╗░██║██╔════╝██╔════╝░██║░░██╗░░██║██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗
██╔████╔██║██║██╔██╗██║█████╗░░╚█████╗░░╚██╗████╗██╔╝█████╗░░█████╗░░██████╔╝█████╗░░██████╔╝
██║╚██╔╝██║██║██║╚████║██╔══╝░░░╚═══██╗░░████╔═████║░██╔══╝░░██╔══╝░░██╔═══╝░██╔══╝░░██╔══██╗
██║░╚═╝░██║██║██║░╚███║███████╗██████╔╝░░╚██╔╝░╚██╔╝░███████╗███████╗██║░░░░░███████╗██║░░██║
╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚══════╝╚═════╝░░░░╚═╝░░░╚═╝░░╚══════╝╚══════╝╚═╝░░░░░╚══════╝╚═╝░░╚═╝

Controls:
Move: Up/Down/Left/Right
Start: Enter
Flag: F/Tab
Open: Space
Restart: R/Esc
Exit: Ctrl+C

"""
        ).splitlines():
            print(line[:size].center(size))

        print("Difficulty:".center(size))
        for i, variant in enumerate(variants):
            if i == cursor:
                print(("\x1b[107;30m" + f"{i + 1}. " + variant + "\x1b[0m").center(
                    size + len("\x1b[107;30m") + len("\x1b[0m") - 2))
            else:
                print(f"{i + 1}. {variant}".center(size))
        print("")

    kb.add_hotkey("UP", lambda: change_cursor(-1))
    kb.add_hotkey("DOWN", lambda: change_cursor(1))

    draw()
    try:
        kb.wait("SPACE")
        rem()

    except KeyboardInterrupt:
        print("\r\x1b[91mCatched CTRL+C\x1b[0m")
        return

    game = Minesweeper()
    game.set_dif(variants[cursor])
    game.run()


if __name__ == '__main__':
    main()
