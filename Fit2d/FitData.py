from . import functions
from .ReturnInfo import Status

def FitData():
	filename = ''
	while True:
		(code1, filename) = load(filename)
		if code1 != Status.SUCCESS:
			return code1
		(code2, df) = openfile(filename)
		res2 = ()
		while True:
			(code3, res) = select(df, res2)
			if code3 == Status.QUIT:
				return code3
			elif code3 == Status.BACK:
				break
			(code4, res2) = plot(res)
			if code4 != Status.BACK:
				return code4
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

def select(df, res):
	res = functions.SelectData(df, res)
	if res.getStatus() == Status.SUCCESS:
		df = res.getData()[0]
		xName = res.getData()[1]
		yName = res.getData()[2]
	elif res.getStatus() == Status.BACK:
		return (Status.BACK, df)
	else:
		return (Status.ERROR, -1)
	l = (df, xName, yName)
	return (Status.SUCCESS, l)
	
def plot(data):
	(df, xName, yName) = data
	res = functions.ScatterGraph(df, xName, yName)
	if res.getStatus() == Status.BACK:
		return (Status.BACK, data)
	if res.getStatus() == Status.NEXT:
		return (Status.NEXT, 0)
	else:
		return (Status.ERROR, -1)
	
	