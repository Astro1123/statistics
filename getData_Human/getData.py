import sys
import platform
import functions
import CommandClass as cc
import PySimpleGUI as sg

def make_dpi_aware():
	import ctypes
	if int(platform.release()) >= 8:
		ctypes.windll.shcore.SetProcessDpiAwareness(True)

def getData():
	while True:
		try:
			cmd = functions.fileselect()
		except Exception as e:
			sg.popup_error(f'エラー')
			return 1
		if cmd.getcmd() == (cc.const.SYSTEM, cc.const.QUIT):
			return 0
		
		try:
			cmd = functions.main(cmd.getcmdlist())
		except Exception as e:
			sg.popup_error(f'エラー')
			return 1
		if cmd.getcmd() == (cc.const.SYSTEM, cc.const.QUIT):
			return 0
		elif cmd.getcode() == cc.const.ERROR:
			(_, name) = cmd.getcmd()
			sg.popup_error(f'エラー ({name})')
			return 1

if __name__ == "__main__":
	try:
	    make_dpi_aware()
	except ValueError as e:
		pass
	sys.exit(getData())
