import PySimpleGUI as sg
import numpy as np
import pandas as pd
from enum import Enum, auto
from scipy import stats
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Status(Enum):
	NULL = 0
	SUCCESS = auto()
	ERROR = auto()
	BACK = auto()
	NEXT = auto()
	QUIT = auto()

class ReturnInfo:
	status = -1
	data = ''
	
	def makeInfo(self, status, data):
		self.status = status
		self.data = data
		
	def getData(self):
		return self.data
		
	def getStatus(self):
		return self.status
	
	def splitInfo(self):
		return (self.status, self.data)

def QuitCmd():
	res = ReturnInfo()
	res.makeInfo(Status.QUIT, '')
	return res

def NextCmd():
	res = ReturnInfo()
	res.makeInfo(Status.NEXT, '')
	return res

def BackCmd():
	res = ReturnInfo()
	res.makeInfo(Status.BACK, '')
	return res

def SuccessCmd(data):
	res = ReturnInfo()
	res.makeInfo(Status.SUCCESS, data)
	return res
	

def SelectData(df, select, binval):
	dataName = list(df.columns.values)
	if select == None:
		default = 'Select'
	else:
		default = select
	
	layout = [
		[sg.Text("Select data which you want to use"), sg.Combo(dataName, default_value=default, readonly=True, key='Combo')],
		[sg.Text("Bins of Histogram"), sg.InputText(default_text=str(binval), key='Text')], 
		[sg.Button("Back"), sg.Button('Exit'), sg.Button('Select')]
	]
	window = sg.Window('Theme Browser', layout)
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = QuitCmd()
			break
		elif event == 'Back':
			res = BackCmd()
			break
		elif event == 'Select':
			if values['Combo'] in dataName:
				if 'Text' != '':
					try:
						binval = int(values['Text'])
					except ValueError as e:
						pass
					res = SuccessCmd((values['Combo'], binval))
					break
	
	window.close()
	return res

def CalcData(df, sel, binval):
	data = df[sel].dropna(how='all').values
	average = np.mean(data)
	maxval = np.max(data)
	minval = np.min(data)
	var = np.var(data)
	uvar = np.var(data, ddof=1)
	cstd = np.std(data)
	ustd = np.std(data, ddof=1)
	midrange = (maxval + minval) / 2
	rangeval = maxval - minval
	median = np.median(data)
	q3, q1 = np.percentile(data, [75, 25])
	iqr = q3 - q1
	c = data.size
	s = np.sum(data)
	skew = stats.skew(data)
	kurtosis = stats.kurtosis(data)
	modeval = statistics.multimode(data)
	
	columnsA = sg.Column(
		[
			[sg.Text('Average'), sg.InputText(f'{average}', readonly=True)],
			[sg.Text('Max'), sg.InputText(f'{maxval}', readonly=True)],
			[sg.Text('Third quartile'), sg.InputText(f'{q3}', readonly=True)],
			[sg.Text('Median'), sg.InputText(f'{median}', readonly=True)],
			[sg.Text('First quartile'), sg.InputText(f'{q1}', readonly=True)],
			[sg.Text('Min'), sg.InputText(f'{minval}', readonly=True)],
			[sg.Text('Mid-range'), sg.InputText(f'{midrange}', readonly=True)],
			[sg.Text('Mode'), sg.InputText(f'{modeval}', readonly=True)],
		]
	)
	columnsB = sg.Column(
		[
			[sg.Text('Range'), sg.InputText(f'{rangeval}', readonly=True)],
			[sg.Text('Interquartile range'), sg.InputText(f'{iqr}', readonly=True)],
			[sg.Text('Sample variance'), sg.InputText(f'{var}', readonly=True)],
			[sg.Text('Unbiased variance'), sg.InputText(f'{uvar}', readonly=True)],
			[sg.Text('Corrected sample standard deviation'), sg.InputText(f'{cstd}', readonly=True)],
			[sg.Text('Uncorrected sample standard deviation'), sg.InputText(f'{ustd}', readonly=True)],
			[sg.Text('Skewness'), sg.InputText(f'{skew}', readonly=True)],
			[sg.Text('Kurtosis'), sg.InputText(f'{kurtosis}', readonly=True)],
		]
	)
	columnsC = sg.Column(
		[
			[sg.Text('Sum'), sg.InputText(f'{s}', readonly=True)],
			[sg.Text('Count'), sg.InputText(f'{c}', readonly=True)],
		]
	)
	
	columns = sg.Column(
		[
			[columnsA],
			[columnsB],
			[columnsC],
			[sg.Button("Back"), sg.Button('Next'), sg.Button('Exit')]
		]
	)
	
	fig = plt.Figure()
	ax1 = fig.add_subplot(111)
	ax1.hist(data, bins=binval)
	ax1.set_title(f"Histogram of {sel}")
	
	layout = [
		[columns, sg.Canvas(key='CANVAS')]
	]
	
	win_location = (0, 0)
	window = sg.Window('Theme Browser', layout, finalize=True, location=win_location)
	
	draw_figure(window['CANVAS'].TKCanvas, fig)
	
	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			res = QuitCmd()
			break
		elif event == 'Back':
			res = BackCmd()
			break
		elif event == 'Next':
			res = NextCmd()
			break
	
	window.close()
	return res

def selectEncode(filename):
	enc = ["utf-8", "shift-jis", "cp932", "utf-8-sig", "iso2022_jp", "euc_jp"]
	i = 0
	for s in enc:
		try:
			df = pd.read_csv(filename, encoding=enc[i])
			res = enc[i]
			break
		except UnicodeDecodeError as e:
			i += 1
	else:
		res = "unknown"
	return res

def OpenFile(filename):
	encodeName = selectEncode(filename)
	if encodeName == "unknown":
		raise ValueError(f'Cannot open {filename}')
	df = pd.read_csv(filename, encoding=encodeName)
	return SuccessCmd(df)

def LoadData(filename):
	sg.theme('Dark Brown')
	
	layout = [
		[sg.Text("File"), sg.InputText(default_text=filename, key='Text'), sg.FileBrowse(key="file")], 
		[sg.Button("Back"), sg.Button('Exit'), sg.Submit()]
	]
	window = sg.Window('Title', layout)
	
	while True:
		event, values = window.read()
		
		if event in (sg.WIN_CLOSED, 'Back'):
			res = BackCmd()
			break
		elif event == 'Exit':
			res = QuitCmd()
			break
		elif event == 'Submit':
			if values["file"] != "":
				res = SuccessCmd(values["file"])
				break
			elif values["Text"] != "":
				res = SuccessCmd(values["Text"])
				break
	
	window.close()
	return res

def Basic():
	filename = ''
	select = None
	binval = 10
	while True:
		(code1, filename) = LoadData(filename).splitInfo()
		if code1 != Status.SUCCESS:
			return code1
		(code2, df) = OpenFile(filename).splitInfo()
		while True:
			(code3, val) = SelectData(df, select, binval).splitInfo()
			if code3 == Status.QUIT:
				return code3
			elif code3 == Status.BACK:
				break
			(select, binval) = val
			(code4, _) = CalcData(df, select, binval).splitInfo()
			if code4 != Status.BACK:
				return code4
	return Status.NULL

def draw_figure(canvas, figure):
	figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
	figure_canvas_agg.draw()
	figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
	return figure_canvas_agg
