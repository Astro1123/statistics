from . import functions
from . import Dimension3
from .ReturnInfo import Status
from .ReturnInfo import ExecuteCommand
from .residualPlot import plotResiduals

def FitData(d):
	filename = ''
	while True:
		(code1, filename) = load(filename)
		if code1 != Status.SUCCESS:
			return code1
		(code2, df) = openfile(filename)
		res2 = ()
		if d == 2:
			while True:
				(code3, res) = select(df, res2, d)
				if code3 == Status.QUIT:
					return code3
				elif code3 == Status.BACK:
					break
				while True:
					(code4, res2) = plot(res)
					if code4 == Status.COMMAND:
						(cmd, *data) = res2
						if cmd == ExecuteCommand.RPLOT:
							code5 = plotResiduals(data).getStatus()
							if code5 == Status.QUIT:
								return code5
					elif code4 != Status.BACK:
						return code4
					else:
						break
		elif d == 3:
			while True:
				(code3, res) = select(df, res2, d)
				if code3 == Status.QUIT:
					return code3
				elif code3 == Status.BACK:
					break
				while True:
					(code4, res2) = plot3(res)
					if code4 == Status.COMMAND:
						(cmd, *data) = res2
						if cmd == ExecuteCommand.RPLOT:
							code5 = plotResiduals(data).getStatus()
							if code5 == Status.QUIT:
								return code5
					elif code4 != Status.BACK:
						return code4
					else:
						break
		else:
			while True:
				(code3, res) = select(df, res2, d)
				if code3 == Status.QUIT:
					return code3
				elif code3 == Status.BACK:
					break
				while True:
					(code4, res2) = plotm(res)
					if code4 == Status.COMMAND:
						(cmd, *data) = res2
						if cmd == ExecuteCommand.RPLOT:
							code5 = plotResiduals(data).getStatus()
							if code5 == Status.QUIT:
								return code5
					elif code4 != Status.BACK:
						return code4
					else:
						break
	return Status.NULL

def load(filename):
	res = functions.LoadData(filename);
	if res.getStatus() == Status.SUCCESS:
		filename = res.getData()[0]
		return (Status.SUCCESS, filename)
	else:
		return (res.getStatus(), -1)

def openfile(filename):
	try:
		res = functions.OpenFile(filename)
	except ValueError as e:
		raise
	
	if res.getStatus() == Status.SUCCESS:
		df = res.getData()[0]
		return (Status.SUCCESS, df)
	elif res.getStatus() == Status.BACK:
		return (Status.BACK, filename)
	else:
		return (Status.ERROR, -1)

def select(df, res, d):
	if d == 2:
		res = functions.SelectData(df, res)
	elif d == 3:
		res = Dimension3.SelectData3(df, res)
	else:
		res = Dimension3.SelectDatam(df, res)
	if res.getStatus() == Status.SUCCESS:
		if d >= 2:
			df = res.getData()[0]
			xName = res.getData()[1]
			yName = res.getData()[2]
			if d == 3:
				zName = res.getData()[3]
				l = (df, xName, yName, zName)
			else:
				l = (df, xName, yName)
		else:
			df = res.getData()[0]
			xName = res.getData()[1]
			l = (df, xName)
	elif res.getStatus() == Status.BACK:
		return (Status.BACK, df)
	elif res.getStatus() == Status.QUIT:
		return (Status.QUIT, 0)
	else:
		return (Status.ERROR, -1)
	return (Status.SUCCESS, l)
	
def plot(data):
	(df, xName, yName) = data
	res = functions.ScatterGraph(df, xName, yName)
	if res.getStatus() == Status.BACK:
		return (Status.BACK, data)
	if res.getStatus() == Status.NEXT:
		return (Status.NEXT, 0)
	if res.getStatus() == Status.COMMAND:
		return (Status.COMMAND, res.getData())
	else:
		return (Status.ERROR, -1)
	
def plot3(data):
	(df, xName, yName, zName) = data
	res = Dimension3.ScatterGraph3(df, xName, yName, zName)
	if res.getStatus() == Status.BACK:
		return (Status.BACK, data)
	if res.getStatus() == Status.NEXT:
		return (Status.NEXT, 0)
	if res.getStatus() == Status.COMMAND:
		return (Status.COMMAND, res.getData())
	else:
		return (Status.ERROR, -1)
	
def plotm(data):
	(df, xName) = data
	res = Dimension3.ScatterGraphm(df, xName)
	if res.getStatus() == Status.BACK:
		return (Status.BACK, data)
	if res.getStatus() == Status.NEXT:
		return (Status.NEXT, 0)
	if res.getStatus() == Status.COMMAND:
		return (Status.COMMAND, res.getData())
	else:
		return (Status.ERROR, -1)
