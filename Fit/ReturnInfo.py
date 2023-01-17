from enum import Enum, auto

class ReturnInfo:
	status = -1
	DataList = []
	
	def makeInfo(self, status, *arg):
		self.status = status
		self.DataList = [x for x in arg]
		
	def getData(self):
		return self.DataList
		
	def getStatus(self):
		return self.status

class Status(Enum):
	NULL = 0
	SUCCESS = auto()
	ERROR = auto()
	BACK = auto()
	QUIT = auto()
	NEXT = auto()
	FAILURE = auto()
	COMMAND = auto()

def QuitCmd():
	res = ReturnInfo()
	res.makeInfo(Status.QUIT)
	return res

def NextCmd():
	res = ReturnInfo()
	res.makeInfo(Status.NEXT)
	return res

def BackCmd():
	res = ReturnInfo()
	res.makeInfo(Status.BACK)
	return res
	
def SuccessCmd(*arg):
	res = ReturnInfo()
	res.makeInfo(Status.SUCCESS, *arg)
	return res
	
def FailCmd():
    res = ReturnInfo()
    res.makeInfo(Status.FAILURE, '')
    return res