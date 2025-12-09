import random
import time

from cell import Cell, copyCells
from draw import drawFull, drawGrid, drawInfo, draw
from setting import *
from term_acts import Getch


class Game:
	def __init__(self):
		# import os
		# if os.name == "nt":
		# 	print("\x1b[91mThis version is only for Unix!\x1b[0m")
		# 	exit(1)
		# del os

		self.getch = Getch()
		self.game = False
		
		self.world = None
		self.lworld = None
		self.flags_remain = 0
		self.openRemain = 0
		self.turn = 0
		self.time = 0
		self.ltime = time.perf_counter()

		self.ROW, self.COL = ROW, COL
		self.MINES = MINES

		self.first_click = False

		self.lcursor = [0, 0]
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
			self.lworld.append(copyCells(_line))
	
	def _genMines(self, start):
		start = tuple(start)
		positions = [(x, y) for x in range(self.COL) for y in range(self.ROW)]
		positions.remove(start)

		for _ in range(self.MINES):
			pos = random.choice(positions)
			positions.remove(pos)
			self.world[pos[1]][pos[0]].isMine = True

		for y, row in enumerate(self.world):
			for x, cell in enumerate(row):
				if cell.isMine:
					continue

				for nb in self._neighbors(cell):
					if nb.isMine:
						cell.near += 1
	
	def _start(self):
		self.flags_remain = self.MINES
		self.openRemain = self.ROW * self.COL - self.MINES
		self.first_click = True
		self.game = True
		self.cursor = [0, 0]
		self.turn = 0
	
	# MULTI TIME METHODS


	def _gameOver(self, win):
		self.game = False
		self.lcursor = self.cursor.copy()
		if win:
			print("You won!")
			print("""
\x1b[93m┌──┐
│  │
╰┐┌╯
 ╯╰\x1b[0m
			""".strip())
			return

		for row in self.world:
			for cell in row:
				if not cell.isMine or cell.isFlag:
					continue

				cell.open()
		draw(self, self.world, self.lworld)
		

	def _flagCell(self, pos):
		cell = self.world[pos[1]][pos[0]]
		if cell.isOpen:
			if len(tuple(i for i in self._neighbors(cell) if not i.isOpen)) == cell.near:
				for nb in self._neighbors(cell):
					if nb.isOpen:
						continue
					if not nb.isFlag:
						self.flags_remain -= 1
					nb.isFlag = True
			return

		cell.isFlag = not cell.isFlag
		if cell.isFlag:
			self.flags_remain -= 1
			if self.flags_remain < 0:
				cell.isFlag = False
				self.flags_remain = 0
		else:
			self.flags_remain += 1

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

			cur.open()
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
			flags = 0
			for nb in self._neighbors(cell):
				if nb.isFlag:
					flags += 1
			if flags >= cell.near:
				for nb in self._neighbors(cell):
					if nb.isFlag:
						continue
					if nb.open():
						self.cursor = list(nb.pos)
						self._gameOver(False)
					elif nb.near == 0:
						self._revealNearCells(nb.pos)

			return False

		cell.open()

		if cell.isMine:
			return True
		
		if cell.near == 0:
			self._revealNearCells(pos)

		return False

	def _moveCursor(self, *moveTo):
		self.lcursor = self.cursor.copy()
		self.cursor[0] += moveTo[0]
		self.cursor[1] += moveTo[1]

		self.cursor[0] %= self.COL
		self.cursor[1] %= self.ROW

	def _processChar(self, char):

		if not self.game:
			return False
		
		match char:
			case 'A':
				self._moveCursor(0, -1)
			case 'B':
				self._moveCursor(0, 1)
			case 'C':
				self._moveCursor(1, 0)
			case 'D':
				self._moveCursor(-1, 0)

			case 'w':
				self._moveCursor(0, -1)
			case 's':
				self._moveCursor(0, 1)
			case 'd':
				self._moveCursor(1, 0)
			case 'a':
				self._moveCursor(-1, 0)

			case ' ':
				self.turn += 1
				if self.first_click:
					self._genMines(self.cursor)
					self.first_click = False
					self.ltime = time.perf_counter()

				if self._revealCell(self.cursor):
					self._gameOver(False)
					return True
				if self.openRemain <= 0:
					self._gameOver(True)
				# self.turn ++
			case '\r':
				self.turn += 1
				self._flagCell(self.cursor)

			case '\t':
				self.turn += 1
				self._flagCell(self.cursor)
			
			case '\x1b':
				pass

			case '[':
				pass

			case _:
				print(f"Unknow command [{repr(char)}] ", end="\r")
				return False
		
		return True

	def play(self, mode):
		from os import get_terminal_size
		size = get_terminal_size()
		del get_terminal_size

		self.ROW, self.COL, self.MINES = mode
		if self.ROW * 2 + 3 > size[1]:
			print("Terminal is too small(Y)")
			exit(1)
		if self.COL * 4 + 14 > size[0]:
			print("Terminal is too small(X)")
			exit(1)

		while True:
			self._genWorld()
			self._start()
			drawFull(self, self.world)

			while self.game:
				if not self.first_click:
					self.time = int(time.perf_counter() - self.ltime)
				char = self.getch()
				if char == '\x03':
					break
	
				if self._processChar(char):
					draw(self, self.world, self.lworld)
					self.lworld = [copyCells(i) for i in self.world]

			else:
				
				char = self.getch()
				
				while char not in ('\x03', ' '):
					char = self.getch()
				if char != '\x03':
					continue
			break


def main():
	game = Game()

	import sys
	argv = sys.argv

	md = None
	if len( argv ) > 1:
		md = argv[ 1 ].lower()
		if md.isdigit():
			md = int( md )
			if ( md <= 0 | md >= 4):
				md = 1
		elif md in ( "easy", "normal", "hard"):
			md = ( "easy", "normal", "hard").index( md ) + 1
		else:
			print("Difficulty must be 1/2/3 or easy/normal/hard")
			md = None
	modes = {
		"Easy": (9, 9, 10),
		"Normal": (16, 16, 30),
		"Hard": (16, 30, 99)
	}

	if md is None:
			
		print("\x1b[H\x1b[2J", end="")
		print("Choose mode(default Easy)")
		for i, k in enumerate(modes.keys()):
			print(f"{i + 1}. {k}")
		print("\n0. Quit")
		try:
			inp = int(input("\n\x1b[95mMode (0-3) > \x1b[0m"))
	
			if 0 <inp <= 3:
				print(f"Mode: {list(modes.keys())[inp - 1]}")
			elif inp == 0:
				print("Quit")
				return
		
		except ValueError:
			inp = 1
	
		except KeyboardInterrupt:
			return
	
		if not (0 <= inp < 4):
			inp = 1
		
		md = inp
	
	print("""
WASD / ARROWS - MOVE
SPACE - REVEAL
TAB / ENTER - FLAG
CTRL+C - EXIT
	   """)
	print("Press any key to continue...", end="", flush=True)
	char = game.getch()
	if char == '\x03':
		print("\x1b[91mInterrupted\x1b[0m")
		return

	game.play(modes[list(modes.keys())[md - 1]])


if __name__ == "__main__":
	main()

