# Source - https://stackoverflow.com/a␍
# Posted by Anurag Uniyal␍
# Retrieved 2025-11-20, License - CC BY-SA 2.5␍
 

class Getch:
	def __init__(self):
		try:
			self.impl = _GetchWindows()
		except ImportError:
			self.impl = _GetchUnix()
	
	def getBytes(self):
		return self.impl.getBytes()

	def __call__(self):
		return self.impl()


class _GetchWindows:
	def __init__(self):
		import msvcrt
	
	def getBytes(self):
		import msvcrt
		return msvcrt.getch()

	def _getArrow(self, char):
		match (char):
			case "H":
				return "A"
			case "K":
				return "D"
			case "P":
				return "B"
			case "M":
				return "C"
			case _:
				return char

	def __call__(self):
		import msvcrt
		try:
			return msvcrt.getch().decode('utf-8')
		except UnicodeDecodeError:
			return self._getArrow(msvcrt.getch().decode('utf-8'))


class _GetchUnix:
	def __init__(self):
		import tty, sys
	
	def getBytes(self):
		return bytes(self())

	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)

		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		
		return ch


if __name__ == "__main__":
	getch = Getch()
	while True:
		char = getch.getBytes()
		if char == b'\x03':
			break
		print(repr(char))

