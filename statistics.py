import platform
import sys
import traceback

from ResClass import Status
import Main

def make_dpi_aware():
	import ctypes
	if int(platform.release()) >= 8:
		ctypes.windll.shcore.SetProcessDpiAwareness(True)

def main(initial):
	try:
		res = Main.main(initial)
	except Exception as e:
		#print(e)
		print(traceback.format_exc())
		sys.exit(1)
	return res

if __name__ == '__main__':
	try:
		make_dpi_aware()
	except ValueError as e:
		pass
	
	initial = 'Select'
	while True:
		(res, initial) = main(initial)
		if res == Status.QUIT:
			sys.exit(0)
		elif res == Status.ERROR:
			sys.exit(1)
