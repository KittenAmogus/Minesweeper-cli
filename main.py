from cell import Cell
from draw import drawFull, drawGrid, draw
from setting import *
from term_acts import GetchUnix


class Game:
	def __init__(self):
		import os
		if os.name == "nt":
			print("\x1b[91mThis version is only for Unix!\x1b[0m")
			exit(1)
		del os

		self.getch = GetchUnix()
		self.game = False
		
		self.world = None
		self.lworld = None
		self.flags_remain = 0

		self.ROW, self.COL = ROW, COL
		self.MINES = MINES

		self.first_click = False

		self.cursor = [0, 0]
	
	def _genWorld(self):
		self.world = []
		self.lworld = []

		for y in range(self.ROW):
			_line = []
			for x in range(self.COL):
				cell = Cell(self, x, y)
				_line.append(cell)
			self.world.append(_line)
			self.lworld.append(_line.copy())
	
	def _start(self):
		self.flags_remain = self.MINES
		self.first_click = True
		self.game = True
	
	# MULTI TIME METHODS

	def _flagCell(self, pos):
		cell = self.world[pos[1]][pos[0]]
		cell.isFlag = not cell.isFlag

	def _neighbors(self, cell):
		nbs = []
		for ay in range(cell.y - 1, cell.y + 2):
			if ay < 0 or ay >= self.ROW:
				continue
			for ax in range(cell.x - 1, cell.x + 2):
				if ax < 0 or ax >= self.COL:
					continue

				if ax == cell.x and ay == cell.y:
					continue
				
				nbs.append(self.world[ay][ax])
		return nbs

	def _revealNearCells(self, pos):
		init_cell = self.world[pos[1]][pos[0]]
		
		queue = self._neighbors(init_cell)
		
		while queue:
			cur = queue[0]
			queue.pop(0)
			if cur.isOpen or cur.isFlag:
				continue

			cur.isOpen = True
			if cur.near > 0:
				continue
			
			for nb in self._neighbors(cur):
				if not nb.isOpen or nb.isFlag:
					queue.append(nb)

	def _revealCell(self, pos):
		cell = self.world[pos[1]][pos[0]]
			
		if cell.isFlag:
			return False

		if cell.isOpen:
			return False

		cell.isOpen = True

		if cell.isMine:
			return True

		self._revealNearCells(pos)

		return False

	def _moveCursor(self, *moveTo):
		self.cursor[0] += moveTo[0]
		self.cursor[1] += moveTo[1]

		self.cursor[0] %= self.COL
		self.cursor[1] %= self.ROW

	def _processChar(self, char):
		match char:
			case 'w':
				self._moveCursor(0, -1)
			case 's':
				self._moveCursor(0, 1)
			case 'd':
				self._moveCursor(1, 0)
			case 'a':
				self._moveCursor(-1, 0)

			case ' ':
				self._revealCell(self.cursor)
				# self.turn ++
			case '\r':
				self._flagCell(self.cursor)

			case _:
				print(repr(char))
				return False
		
		return True

	def play(self):
		self._genWorld()
		self._start()
		
		drawFull(self.world)

		while self.game:
			char = self.getch()
			if char == '\x03':
				break

			if self._processChar(char):
				draw(self.world, self.lworld)
				self.lworld = [i.copy() for i in self.world]


def main():
	game = Game()
	game.play()


if __name__ == "__main__":
	main()

