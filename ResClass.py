from enum import Enum, auto
import Fit2d
import Main
import CommandClass

class Status(Enum):
	NULL = 0
	SUCCESS = auto()
	ERROR = auto()
	BACK = auto()
	QUIT = auto()

def readGetData(res):
	if res == 1:
		return Status.ERROR
	if res == 0:
		return Status.SUCCESS
	return Status.NULL

def readFit2d(res):
	if res == Fit2d.ReturnInfo.Status.SUCCESS:
		return Status.SUCCESS
	elif res == Fit2d.ReturnInfo.Status.ERROR:
		return Status.ERROR
	elif res == Fit2d.ReturnInfo.Status.BACK:
		return Status.BACK
	elif res == Fit2d.ReturnInfo.Status.NEXT:
		return Status.BACK
	elif res == Fit2d.ReturnInfo.Status.QUIT:
		return Status.QUIT
	return Status.NULL

def readMain(res):
	if res == Main.Status.QUIT:
		return Status.QUIT
	elif res == Main.Status.ERROR:
		return Status.ERROR
	return Status.NULL
