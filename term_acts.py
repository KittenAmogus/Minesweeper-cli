# Source - https://stackoverflow.com/a␍
# Posted by Anurag Uniyal␍
# Retrieved 2025-11-20, License - CC BY-SA 2.5␍
 

class Getch:
	def __init__(self):
		try:
			self.impl = _GetchWindows()
		except ImportError:
			self.impl = _GetchUnix()
	
	def __call__(self):
		return self.impl()


class _GetchWindows:
	def __init__(self):
		import msvcrt
	
	def __call__(self):
		import msvcrt
		try:
			return msvcrt.getch().decode('utf-8')
		except UnicodeDecodeError:
			return '\x03'


class _GetchUnix:
	def __init__(self):
		import tty, sys

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

