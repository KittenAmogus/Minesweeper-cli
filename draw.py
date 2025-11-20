from setting import *


def printf(*args):
    print(*args, end="")


def drawGrid():
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


def drawFull(world):
	drawGrid()
	for y, row in enumerate(world):
		for x, cell in enumerate(row):
			printf(f"\x1b[{2 + 2 * y};{2 + 4 * x}H")
			printf(str(cell) + "\x1b[0m")
	printf(f"\x1b[{2 + 2 * ROW};1H\n\r")


def draw(world, lworld):
	for y, row in enumerate(world):
		for x, cell in enumerate(row):
			if cell != lworld[y][x]:
				printf(f"\x1b[{2 + 2 * y};{2 + 4 * x}H")
				printf(str(cell) + "\x1b[0m")
	printf(f"\x1b[{2 + 2 * ROW};1H\n\r")

