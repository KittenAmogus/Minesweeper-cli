class _Style:
	EMPTY = " "
	MINE = "@"
	FLAG = "F"
	CLOSED = " "


class _Color:
	EMPTY = "\x1b[100m"
	MINE = "\x1b[91m"
	FLAG = "\x1b[103;30m"
	CLOSED = ""

	CURSOR = "\x1b[95m"

	NUMBERS = tuple([EMPTY] + [
		f"\x1b[{i}m" for i in (104, 102, 101, 44, 41, 106, 105, 90)
		])


class Cell:
	def __init__(self, game, x, y):
		self.x = x
		self.y = y
		self.game = game

		self.isOpen = False
		self.isMine = False
		self.isFlag = False
		self.near = 0
	
	def open(self):
		if not (self.isOpen or self.isFlag):
			self.isOpen = True
			self.game.openRemain -= 1
			return self.isMine

	@property
	def pos(self):
		return self.x, self.y

	def __eq__(self, other):
		return self.isOpen == other.isOpen and self.isFlag == other.isFlag

	def _getString(self):
		if not self.isOpen:
			if self.isFlag:
				return _Style.FLAG
			return _Style.CLOSED

		if self.isMine:
			return _Style.MINE

		if self.near == 0:
			return _Style.EMPTY

		return str(self.near)
	
	def _getColor(self):
		if not self.isOpen:
			if self.isFlag:
				return _Color.FLAG
			return _Color.CLOSED

		if self.isMine:
			return _Color.MINE

		return _Color.NUMBERS[self.near]
	
	def __str__(self):
		if self.game.cursor[0] == self.x and self.game.cursor[1] == self.y:
			return f"{_Color.CURSOR}[{self._getString()}]"
		return f"{self._getColor()} {self._getString()} "


def copyCells(row):
	newRow = row.copy()
	for i, v in enumerate(newRow):
		newRow[i] = Cell(v.game, v.x, v.y)
		newRow[i].isOpen = v.isOpen
		newRow[i].isMine = v.isMine
		newRow[i].isFlag = v.isFlag
		newRow[i].near = v.near
	return newRow

