import const

const.ERROR = -1
const.INVALID_VALUE_EXCEPTION = 'INVALID_VALUE_EXCEPTION'
const.FAILURE_EXCEPTION = 'FAILURE_EXCEPTION'

const.NULL = 0
const.NULLCMD = 'NULL'
const.SYSTEM = 1
const.QUIT = 'QUIT'
const.OTHER = 'OTHER'
const.FILESELECT = 2
const.DATASELECT = 3

class CommandClass:
	code = -1
	cmd = ''
	l = []
    
	def getcode(self):
		return self.code
	
	def getcmd(self):
		return (self.code, self.cmd)
	
	def getcmdlist(self):
		return (self.code, self.cmd, self.l)
	
	def setcmd(self, code, cmd, *arg):
		self.code = code
		self.cmd = cmd
		if arg == ((),):
			self.l.append(0)
		else:
			self.l.append(len(arg[0]))
			self.l.extend([x for x in arg[0]])

def MakeCommand(code, cmd, *arg):
	cc = CommandClass()
	cc.setcmd(code, cmd, arg)
	return cc

def FalureCommand():
	return MakeCommand(const.ERROR, const.FAILURE_EXCEPTION)

def QuitCommand():
	return MakeCommand(const.SYSTEM, const.QUIT)

def OtherCommand():
	return MakeCommand(const.SYSTEM, const.OTHER)

def NULLCommand():
	return MakeCommand(const.NULL, const.NULLCMD)

def InvalidValueCommand():
	return MakeCommand(const.ERROR, const.INVALID_VALUE_EXCEPTION)
