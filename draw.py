def printf(*args):
    print(*args, end="")


def drawInfoGrid(game):
	ROW, COL = game.ROW, game.COL

	printf(f"\x1b[1;{4 * COL + 3}H╭")
	for _ in range(9):
		printf("─")
	printf("╮")
	
	for i, val in enumerate(("Mines", "Time", "Turn")):
		printf(f"\x1b[{i + 2};{4 * COL + 3}H│{val}{' ' * (9 - len(val))}│")

	printf(f"\x1b[{i + 3};{4 * COL + 3}H╰")
	for _ in range(9):
		printf("─")
	printf("╯")


def drawInfo(game):
	drawInfoGrid(game)
	time = str(game.time)
	flags = str(game.flags_remain)
	turn = str(game.turn)

	printf(f"\x1b[{2};{(4 * game.COL + 5) + (8 - len(flags))}H{flags}")
	printf(f"\x1b[{3};{(4 * game.COL + 5) + (8 - len(time))}H{time}")
	printf(f"\x1b[{4};{(4 * game.COL + 5) + (8 - len(turn))}H{turn}")


def drawGrid(game):
	ROW, COL = game.ROW, game.COL
	printf("\x1b[H\x1b[2J\x1b[3J")
	
	printf("╭")
	for _ in range(COL - 1):
		printf("───┬")
	printf("───╮\n\r")

	for y in range(ROW):
		for _ in range(COL):
			printf("│   ")
		printf("│\n\r")

		if y +1 < ROW:
			printf("├")

			for _ in range(COL - 1):
				printf("───┼")
			printf("───┤\n\r")

	printf("╰")
	for _ in range(COL - 1):
		printf("───┴")
	printf("───╯\n\r")

	drawInfoGrid(game)


def drawFull(game, world):
	ROW, COL = game.ROW, game.COL
	drawGrid(game)
	drawInfo(game)
	for y, row in enumerate(world):
		for x, cell in enumerate(row):
			printf(f"\x1b[{2 + 2 * y};{2 + 4 * x}H")
			printf(str(cell) + "\x1b[0m")
	printf(f"\x1b[{2 + 2 * ROW};1H\n\r")


def draw(game, world, lworld):
	drawInfo(game)
	ROW, COL = game.ROW, game.COL
	for y, row in enumerate(world):
		for x, cell in enumerate(row):
			if not cell == lworld[y][x] or\
			tuple(game.cursor) == (x, y) or\
			tuple(game.lcursor) == (x, y):
				printf(f"\x1b[{2 + 2 * y};{2 + 4 * x}H")
				printf(str(cell) + "\x1b[0m")
	printf(f"\x1b[{2 + 2 * ROW};1H")
	print(flush=True)

